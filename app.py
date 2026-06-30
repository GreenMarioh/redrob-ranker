import streamlit as st
import sys
import json
import io
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from parsing.loader import load_candidates_jsonl, parse_candidate
from ranking.rank import rank_candidates
from ranking.explanations import explain_candidate
from features.scorer import total_score
from features.semantic import keyword_score, KEYWORDS
from features.career_relevance import career_relevance_score
from features.experience import experience_score
from features.behavior import behavior_score
from features.availability import availability_score
from features.honeypot import honeypot_penalty, explain_honeypot

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Redrob Candidate Ranker",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    *, html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .block-container { padding-top: 1.5rem; padding-bottom: 1rem; }

    /* Hero */
    .hero {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid rgba(148, 163, 184, 0.12);
        border-radius: 12px;
        padding: 1.75rem 2rem;
        margin-bottom: 1.25rem;
    }
    .hero h1 { color: #f1f5f9; font-size: 1.5rem; font-weight: 700; margin: 0 0 0.2rem 0; }
    .hero p  { color: #94a3b8; font-size: 0.85rem; margin: 0; }

    /* Metric cards */
    .metric-row { display: flex; gap: 0.75rem; margin-bottom: 1.25rem; }
    .metric-card {
        flex: 1;
        background: #1e293b;
        border: 1px solid rgba(148, 163, 184, 0.1);
        border-radius: 10px;
        padding: 1rem 1.25rem;
    }
    .metric-card .label {
        font-size: 0.68rem; font-weight: 600; color: #64748b;
        text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.25rem;
    }
    .metric-card .value { font-size: 1.4rem; font-weight: 700; color: #e2e8f0; }
    .metric-card .sub   { font-size: 0.65rem; color: #475569; margin-top: 0.15rem; }

    /* Candidate detail card */
    .detail-card {
        background: #1e293b;
        border: 1px solid rgba(148, 163, 184, 0.1);
        border-radius: 10px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 0.75rem;
    }
    .detail-card .rank  { font-size: 0.65rem; font-weight: 700; color: #6366f1; text-transform: uppercase; letter-spacing: 0.08em; }
    .detail-card .title { font-size: 1rem; font-weight: 700; color: #f1f5f9; margin: 0.1rem 0; }
    .detail-card .meta  { font-size: 0.78rem; color: #94a3b8; }

    /* Flags */
    .flag-item {
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.2);
        color: #fca5a5; font-size: 0.75rem;
        padding: 0.3rem 0.7rem; border-radius: 6px;
        margin: 0.15rem 0; display: inline-block;
    }
    .clean-flag {
        background: rgba(34, 197, 94, 0.1);
        border: 1px solid rgba(34, 197, 94, 0.2);
        color: #86efac; font-size: 0.75rem;
        padding: 0.3rem 0.7rem; border-radius: 6px;
        display: inline-block;
    }

    /* Section divider */
    .section-label {
        font-size: 0.95rem; font-weight: 600; color: #e2e8f0;
        margin: 1rem 0 0.6rem 0;
        padding-bottom: 0.4rem;
        border-bottom: 1px solid rgba(148, 163, 184, 0.1);
    }

    /* Sidebar */
    .sidebar-brand { font-size: 1.1rem; font-weight: 700; color: #e2e8f0; margin-bottom: 0.1rem; }
    .sidebar-sub   { font-size: 0.7rem; color: #64748b; margin-bottom: 1.25rem; }

    /* Cleanup */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_jsonl_from_upload(uploaded_file):
    candidates = []
    content = uploaded_file.getvalue().decode("utf-8")
    for line in content.strip().split("\n"):
        if not line.strip():
            continue
        candidates.append(parse_candidate(json.loads(line)))
    return candidates


def build_results(ranked, global_min, global_max):
    rng = global_max - global_min

    rows = []
    for rank, (score, c) in enumerate(ranked, start=1):
        expl = explain_candidate(c)
        hp = honeypot_penalty(c)
        flags = explain_honeypot(c)
        ai_skills = sum(1 for s in c.skills if s.name.lower() in KEYWORDS)
        norm = (score - global_min) / rng if rng > 0 else 1.0

        rows.append({
            "rank": rank,
            "candidate_id": c.candidate_id,
            "title": c.profile.current_title,
            "company": c.profile.current_company,
            "years_exp": c.profile.years_of_experience,
            "score": round(norm, 4),
            "raw_score": round(score, 4),
            "semantic": round(expl["semantic"], 2),
            "career": round(expl["career"], 2),
            "experience": round(expl["experience"], 2),
            "behavior": round(expl["behavior"], 2),
            "availability": round(expl["availability"], 2),
            "honeypot": round(hp, 2),
            "flags": len(flags),
            "flag_details": " | ".join(flags) if flags else "",
            "ai_skills": ai_skills,
            "location": c.profile.location,
            "response_rate": round(c.redrob_signals.recruiter_response_rate, 2),
            "open_to_work": c.redrob_signals.open_to_work_flag,
            "notice_days": c.redrob_signals.notice_period_days,
        })
    return pd.DataFrame(rows)


def radar_chart(row):
    cats = ["Semantic", "Career", "Experience", "Behavior", "Availability"]
    vals = [row["semantic"], row["career"], row["experience"], row["behavior"], row["availability"]]
    vals.append(vals[0])
    cats.append(cats[0])

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=vals, theta=cats, fill="toself",
        fillcolor="rgba(99, 102, 241, 0.15)",
        line=dict(color="#6366f1", width=2),
        marker=dict(size=5, color="#6366f1"),
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, 1], gridcolor="rgba(255,255,255,0.07)", linecolor="rgba(255,255,255,0.07)"),
            angularaxis=dict(gridcolor="rgba(255,255,255,0.07)", linecolor="rgba(255,255,255,0.07)"),
        ),
        showlegend=False,
        margin=dict(l=50, r=50, t=25, b=25),
        height=300,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0", size=11),
    )
    return fig


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown('<div class="sidebar-brand">🏆 Redrob Ranker</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-sub">Candidate Ranking System</div>', unsafe_allow_html=True)

    st.divider()

    uploaded_file = st.file_uploader(
        "Upload candidates file", type=["jsonl", "json"],
        help="JSONL format, one candidate per line",
    )

    default_path = PROJECT_ROOT / "data" / "raw" / "candidates.jsonl"
    has_default = default_path.exists()

    if has_default and not uploaded_file:
        st.caption("Default dataset detected at data/raw/")

    run = st.button(
        "Run Pipeline",
        use_container_width=True,
        type="primary",
        disabled=(not uploaded_file and not has_default),
    )

    st.divider()

    st.caption("Built by Peaceful Pigeons in Proxies")


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.markdown("""
<div class="hero">
    <h1>🏆 Redrob Candidate Ranker</h1>
    <p>Multi-signal ranking with honeypot detection — top 100 AI/ML candidates</p>
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Pipeline execution
# ---------------------------------------------------------------------------

if run or "results_df" in st.session_state:

    if run:
        with st.spinner("Processing candidates..."):
            if uploaded_file:
                candidates = load_jsonl_from_upload(uploaded_file)
            else:
                candidates = load_candidates_jsonl(str(default_path))

            ranked = rank_candidates(candidates)
            
            # Get global min/max before slicing
            raw_scores = [s for s, _ in ranked]
            global_min = min(raw_scores)
            global_max = max(raw_scores)
            
            # Keep top 100 only
            ranked = ranked[:100]
            df = build_results(ranked, global_min, global_max)

            st.session_state["results_df"] = df
            st.session_state["candidates_map"] = {
                c.candidate_id: c for _, c in ranked
            }

    df = st.session_state["results_df"]

    # ── Metrics ──────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-card">
            <div class="label">Candidates Ranked</div>
            <div class="value">{len(df)}</div>
        </div>
        <div class="metric-card">
            <div class="label">Highest Score</div>
            <div class="value">{df['score'].max():.4f}</div>
        </div>
        <div class="metric-card">
            <div class="label">Average Score</div>
            <div class="value">{df['score'].mean():.4f}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Tabs ─────────────────────────────────────────────────────────
    tab_board, tab_explore, tab_export = st.tabs([
        "Leaderboard", "Candidate Explorer", "Export",
    ])

    # ── Leaderboard ──────────────────────────────────────────────────
    with tab_board:
        fc1, fc2 = st.columns([2, 1])
        with fc1:
            search = st.text_input("Search by ID or title", "", placeholder="e.g. CAND_0088025")

        view = df.copy()
        if search:
            mask = (
                view["candidate_id"].str.contains(search, case=False, na=False)
                | view["title"].str.contains(search, case=False, na=False)
            )
            view = view[mask]

        st.dataframe(
            view[[
                "rank", "candidate_id", "title", "company",
                "years_exp", "score",
                "response_rate", "open_to_work",
            ]].rename(columns={
                "rank": "Rank", "candidate_id": "ID", "title": "Title",
                "company": "Company", "years_exp": "Yrs Exp", "score": "Score",
                "response_rate": "Resp Rate", "open_to_work": "Open",
            }),
            width="stretch",
            height=540,
            hide_index=True,
        )

    # ── Candidate Explorer ───────────────────────────────────────────
    with tab_explore:
        options = [
            f"#{row['rank']}  {row['candidate_id']}  —  {row['title']}"
            for _, row in df.iterrows()
        ]

        if options:
            sel = st.selectbox("Select candidate to view detailed profile", options, label_visibility="collapsed")
            sel_id = sel.split("  ")[1]
            row = df[df["candidate_id"] == sel_id].iloc[0]

            st.markdown(f"""
            <div class="detail-card">
                <div class="rank">Rank #{int(row['rank'])}  ·  Overall Score {row['score']:.4f}</div>
                <div class="title">{row['title']}</div>
                <div class="meta">{row['company']}  ·  {row['years_exp']:.0f} years experience  ·  {row['location']}</div>
            </div>
            """, unsafe_allow_html=True)

            cand_tabs = st.tabs(["📊 Score Analysis", "💼 Career & Skills", "📡 Platform Signals"])

            with cand_tabs[0]:
                col_left, col_right = st.columns([1, 1])
                with col_left:
                    st.plotly_chart(radar_chart(row), use_container_width=True)
                with col_right:
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.dataframe(
                        pd.DataFrame({
                            "Scoring Component": ["Semantic Fit", "Career Relevance", "Experience Fit", "Behavioral", "Availability"],
                            "Raw Score": [row["semantic"], row["career"], row["experience"], row["behavior"], row["availability"]],
                            "Weight": ["25%", "25%", "15%", "20%", "15%"],
                        }),
                        hide_index=True, width="stretch",
                    )

            cmap = st.session_state.get("candidates_map", {})
            cand = cmap.get(sel_id)

            if cand:
                with cand_tabs[1]:
                    d1, d2 = st.columns([1.2, 1])
                    with d1:
                        st.markdown('<div class="section-label">Professional Summary</div>', unsafe_allow_html=True)
                        st.write(cand.profile.summary)

                        st.markdown('<div class="section-label">Career History</div>', unsafe_allow_html=True)
                        for job in cand.career_history[:3]:
                            st.markdown(f"**{job.title}** at **{job.company}**")
                            st.caption(f"{job.duration_months} months · {job.industry}")
                            st.write(job.description)
                            st.markdown("---")

                    with d2:
                        st.markdown('<div class="section-label">Top Skills</div>', unsafe_allow_html=True)
                        skills_rows = []
                        for s in cand.skills[:15]:
                            skills_rows.append({
                                "Skill": s.name,
                                "Level": s.proficiency,
                                "Endorsements": s.endorsements,
                                "Experience": f"{s.duration_months} mo",
                            })
                        if skills_rows:
                            st.dataframe(pd.DataFrame(skills_rows), hide_index=True, width="stretch")

                with cand_tabs[2]:
                    st.markdown('<div class="section-label">Redrob Engagement Metrics</div>', unsafe_allow_html=True)
                    sig = cand.redrob_signals
                    s1, s2, s3 = st.columns(3)
                    with s1:
                        st.metric("Recruiter Response Rate", f"{sig.recruiter_response_rate*100:.0f}%")
                        st.metric("Open to Work", "Yes" if sig.open_to_work_flag else "No")
                    with s2:
                        st.metric("Interview Completion", f"{sig.interview_completion_rate*100:.0f}%")
                        st.metric("Notice Period", f"{sig.notice_period_days} days")
                    with s3:
                        st.metric("GitHub Activity Score", f"{sig.github_activity_score:.0f}/100")
                        st.metric("Saved by Recruiters (30d)", f"{sig.saved_by_recruiters_30d}")

    # ── Export ───────────────────────────────────────────────────────
    with tab_export:
        export_df = df[["candidate_id", "rank", "score"]].copy()
        export_df["reasoning"] = df.apply(
            lambda r: (
                f"{r['title']} with {r['years_exp']:.1f} yrs; "
                f"{r['ai_skills']} AI core skills; "
                f"response rate {r['response_rate']:.2f}."
            ), axis=1,
        )

        st.markdown('<div class="section-label">Submission Format Preview</div>', unsafe_allow_html=True)
        st.dataframe(export_df.head(10), hide_index=True, width="stretch")

        c1, c2 = st.columns(2)
        with c1:
            st.download_button(
                "Download CSV",
                export_df.to_csv(index=False),
                "ranked_candidates.csv",
                "text/csv",
                use_container_width=True,
            )
        with c2:
            buf = io.BytesIO()
            export_df.to_excel(buf, index=False, engine="openpyxl")
            st.download_button(
                "Download XLSX",
                buf.getvalue(),
                "ranked_candidates.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

else:
    # ── Empty state ──────────────────────────────────────────────────
    st.markdown("")
    _, center, _ = st.columns([1, 2, 1])
    with center:
        st.markdown("""
        ### Get started

        Upload a `candidates.jsonl` file in the sidebar and click **Run Pipeline**
        to rank the top 100 candidates.

        The system scores candidates across semantic relevance, career evidence,
        experience fit, behavioral signals, and availability — then applies
        honeypot detection to filter inconsistent profiles.

        ---

        *Peaceful Pigeons in Proxies — Redrob Hackathon*
        """)
