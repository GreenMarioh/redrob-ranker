"""
profile_pipeline.py
-------------------
Profiles the full export_submission pipeline and reports:
  - Wall-clock time (total + per phase)
  - Peak & average RAM usage (RSS)
  - CPU usage (per-core & overall)
  - Disk I/O (bytes read/written)
  - Output file sizes

Usage:
    python scripts/profile_pipeline.py [--sample-interval 0.5]
"""

import sys
import time
import threading
import argparse
from pathlib import Path

import psutil

# ── make sure the project root is on sys.path ─────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

# ── CLI args ──────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Profile the redrob-ranker pipeline")
parser.add_argument(
    "--sample-interval",
    type=float,
    default=0.5,
    metavar="SEC",
    help="How often (seconds) to sample CPU / RAM during execution (default: 0.5s)",
)
args = parser.parse_args()

# ── Resource sampler (runs in a background thread) ────────────────────────────
proc = psutil.Process()

class ResourceSampler:
    def __init__(self, interval: float):
        self.interval = interval
        self.ram_samples = []   # MB
        self.cpu_samples = []   # %
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self):
        self._thread.start()

    def stop(self):
        self._stop.set()
        self._thread.join()

    def _run(self):
        while not self._stop.is_set():
            try:
                mem = proc.memory_info().rss / 1024 / 1024
                cpu = proc.cpu_percent(interval=None)
                self.ram_samples.append(mem)
                self.cpu_samples.append(cpu)
            except psutil.NoSuchProcess:
                break
            self._stop.wait(self.interval)

    @property
    def peak_ram(self):
        return max(self.ram_samples, default=0.0)

    @property
    def avg_ram(self):
        return sum(self.ram_samples) / len(self.ram_samples) if self.ram_samples else 0.0

    @property
    def peak_cpu(self):
        return max(self.cpu_samples, default=0.0)

    @property
    def avg_cpu(self):
        return sum(self.cpu_samples) / len(self.cpu_samples) if self.cpu_samples else 0.0


def fmt_bytes(n):
    for unit in ("B", "KB", "MB", "GB"):
        if abs(n) < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def fmt_time(secs):
    m, s = divmod(secs, 60)
    if m:
        return f"{int(m)}m {s:.2f}s"
    return f"{s:.3f}s"


SECTION = "─" * 60

def section(title):
    print(f"\n{SECTION}")
    print(f"  {title}")
    print(SECTION)


# ── Baseline disk I/O snapshot ────────────────────────────────────────────────
try:
    _io_start = proc.io_counters()
    io_tracking = True
except (AttributeError, psutil.AccessDenied):
    io_tracking = False

# ── Start sampler ─────────────────────────────────────────────────────────────
proc.cpu_percent(interval=None)   # warm up
sampler = ResourceSampler(args.sample_interval)
sampler.start()

# ─────────────────────────────────────────────────────────────────────────────
# PHASE 1 – Load candidates
# ─────────────────────────────────────────────────────────────────────────────
section("PHASE 1 — Loading candidates")
from parsing.loader import load_candidates_jsonl

t0_total = time.perf_counter()
t0 = time.perf_counter()

candidates = load_candidates_jsonl(str(ROOT / "data/raw/candidates.jsonl"))

t_load = time.perf_counter() - t0
print(f"  Loaded {len(candidates):,} candidates  [{fmt_time(t_load)}]")

# ─────────────────────────────────────────────────────────────────────────────
# PHASE 2 – Rank candidates
# ─────────────────────────────────────────────────────────────────────────────
section("PHASE 2 — Ranking candidates")
from ranking.rank import rank_candidates
from features.semantic import KEYWORDS

t0 = time.perf_counter()

ranked = rank_candidates(candidates)

t_rank = time.perf_counter() - t0
print(f"  Ranked {len(ranked):,} candidates  [{fmt_time(t_rank)}]")

# ─────────────────────────────────────────────────────────────────────────────
# PHASE 3 – Build output DataFrame
# ─────────────────────────────────────────────────────────────────────────────
section("PHASE 3 — Building output DataFrame")
import pandas as pd
from ranking.explanations import explain_candidate

t0 = time.perf_counter()

raw_scores  = [s for s, _ in ranked]
min_score   = min(raw_scores)
max_score   = max(raw_scores)
score_range = max_score - min_score

rows = []
for rank, (score, candidate) in enumerate(ranked, start=1):
    explain_candidate(candidate)
    ai_skills_count = sum(1 for s in candidate.skills if s.name.lower() in KEYWORDS)
    title     = candidate.profile.current_title
    years     = candidate.profile.years_of_experience
    resp_rate = candidate.redrob_signals.recruiter_response_rate
    reasoning = (
        f"{title} with {years:.1f} yrs; "
        f"{ai_skills_count} AI core skills; "
        f"response rate {resp_rate:.2f}."
    )
    norm_score = (score - min_score) / score_range if score_range > 0 else 1.0
    rows.append({
        "candidate_id": candidate.candidate_id,
        "rank":         rank,
        "score":        round(norm_score, 4),
        "reasoning":    reasoning,
    })

df = pd.DataFrame(rows)
t_build = time.perf_counter() - t0
print(f"  DataFrame built: {len(df):,} rows  [{fmt_time(t_build)}]")

# ─────────────────────────────────────────────────────────────────────────────
# PHASE 4 – Write outputs
# ─────────────────────────────────────────────────────────────────────────────
section("PHASE 4 — Writing output files")
output_dir = ROOT / "outputs"
output_dir.mkdir(exist_ok=True)

csv_path  = output_dir / "ranked_candidates.csv"
xlsx_path = output_dir / "ranked_candidates.xlsx"

t0 = time.perf_counter()
df.to_csv(csv_path, index=False)
t_csv = time.perf_counter() - t0
print(f"  CSV  saved  [{fmt_time(t_csv)}]  ({fmt_bytes(csv_path.stat().st_size)})")

t0 = time.perf_counter()
df.to_excel(xlsx_path, index=False)
t_xlsx = time.perf_counter() - t0
print(f"  XLSX saved  [{fmt_time(t_xlsx)}]  ({fmt_bytes(xlsx_path.stat().st_size)})")

t_write = t_csv + t_xlsx
t_total = time.perf_counter() - t0_total

# ─────────────────────────────────────────────────────────────────────────────
# Stop sampler & collect final metrics
# ─────────────────────────────────────────────────────────────────────────────
sampler.stop()

if io_tracking:
    try:
        _io_end     = proc.io_counters()
        bytes_read  = _io_end.read_bytes  - _io_start.read_bytes
        bytes_write = _io_end.write_bytes - _io_start.write_bytes
    except psutil.AccessDenied:
        io_tracking = False

cpu_count = psutil.cpu_count(logical=True)
sys_cpu   = psutil.cpu_percent(interval=1)

# ─────────────────────────────────────────────────────────────────────────────
# Final report
# ─────────────────────────────────────────────────────────────────────────────
print(f"\n{'=' * 60}")
print("  RESOURCE USAGE REPORT")
print(f"{'=' * 60}")

print("\n  THROUGHPUT")
print(f"   Candidates processed : {len(candidates):,}")
print(f"   Throughput           : {len(candidates) / t_total:,.0f} candidates/sec")

print("\n  WALL-CLOCK TIME")
print(f"   Load candidates      : {fmt_time(t_load)}")
print(f"   Rank candidates      : {fmt_time(t_rank)}")
print(f"   Build DataFrame      : {fmt_time(t_build)}")
print(f"   Write files          : {fmt_time(t_write)}")
print(f"   {'─' * 35}")
print(f"   Total                : {fmt_time(t_total)}")

print("\n  MEMORY (RSS)")
print(f"   Peak RAM             : {sampler.peak_ram:.1f} MB")
print(f"   Avg  RAM             : {sampler.avg_ram:.1f} MB")
print(f"   Samples collected    : {len(sampler.ram_samples)}")

print(f"\n  CPU")
print(f"   Logical CPU count    : {cpu_count}")
print(f"   Peak process CPU     : {sampler.peak_cpu:.1f}%")
print(f"   Avg  process CPU     : {sampler.avg_cpu:.1f}%")
print(f"   System CPU (now)     : {sys_cpu:.1f}%")

if io_tracking:
    print(f"\n  DISK I/O")
    print(f"   Total bytes read     : {fmt_bytes(bytes_read)}")
    print(f"   Total bytes written  : {fmt_bytes(bytes_write)}")

print(f"\n  OUTPUT FILES")
print(f"   CSV  size            : {fmt_bytes(csv_path.stat().st_size)}")
print(f"   XLSX size            : {fmt_bytes(xlsx_path.stat().st_size)}")

print(f"\n{'=' * 60}\n")
