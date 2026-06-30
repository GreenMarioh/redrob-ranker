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
import concurrent.futures
from pathlib import Path

import psutil
import pandas as pd

# ── make sure the project root is on sys.path ─────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

# ── CLI args ──────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Profile the redrob-ranker pipeline")
parser.add_argument(
    "--sample-interval",
    type=float,
    default=0.1,
    metavar="SEC",
    help="How often (seconds) to sample CPU / RAM during execution (default: 0.1s)",
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


def main():
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
    # PHASE 1 – Load candidates from disk
    # ─────────────────────────────────────────────────────────────────────────────
    section("PHASE 1 — Reading raw file")
    t0_total = time.perf_counter()
    t0 = time.perf_counter()

    data_path = ROOT / "data/raw/candidates.jsonl"
    with open(data_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    t_read = time.perf_counter() - t0
    print(f"  Read {len(lines):,} lines into memory  [{fmt_time(t_read)}]")

    # ─────────────────────────────────────────────────────────────────────────────
    # PHASE 2 – Multiprocessing parse + score + reasoning
    # ─────────────────────────────────────────────────────────────────────────────
    section("PHASE 2 — Multiprocess computation")
    from scripts.export_submission import process_candidate_line

    t0 = time.perf_counter()
    results = []
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for result in executor.map(process_candidate_line, lines, chunksize=1000):
            if result is not None:
                results.append(result)
    t_compute = time.perf_counter() - t0
    print(f"  Computed scores for {len(results):,} candidates  [{fmt_time(t_compute)}]")

    # ─────────────────────────────────────────────────────────────────────────────
    # PHASE 3 – Sort, Normalize, Build DataFrame
    # ─────────────────────────────────────────────────────────────────────────────
    section("PHASE 3 — Sorting & DataFrame build")
    t0 = time.perf_counter()

    results.sort(key=lambda x: x["score"], reverse=True)
    raw_scores = [r["score"] for r in results]
    min_score = min(raw_scores) if raw_scores else 0.0
    max_score = max(raw_scores) if raw_scores else 1.0
    score_range = max_score - min_score

    rows = []
    for rank, res in enumerate(results, start=1):
        score = res["score"]
        normalized_score = (score - min_score) / score_range if score_range > 0 else 1.0
        rows.append({
            "candidate_id": res["candidate_id"],
            "rank": rank,
            "score": round(normalized_score, 4),
            "reasoning": res["reasoning"]
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
            pass

    cpu_count = psutil.cpu_count(logical=True)
    sys_cpu   = psutil.cpu_percent(interval=1)

    # ─────────────────────────────────────────────────────────────────────────────
    # Final report
    # ─────────────────────────────────────────────────────────────────────────────
    print(f"\n{'=' * 60}")
    print("  RESOURCE USAGE REPORT")
    print(f"{'=' * 60}")

    print("\n  THROUGHPUT")
    print(f"   Candidates processed : {len(lines):,}")
    print(f"   Throughput           : {len(lines) / t_total:,.0f} candidates/sec")

    print("\n  WALL-CLOCK TIME")
    print(f"   Read raw file        : {fmt_time(t_read)}")
    print(f"   Multiprocess compute : {fmt_time(t_compute)}")
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


if __name__ == "__main__":
    main()
