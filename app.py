import streamlit as st
import sys
import json
import io
import tempfile
import os
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------------------------
# Path setup — ensure project modules are importable
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
# Custom CSS
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    /* ── Global ──────────────────────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    *, html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }

    /* ── Hero banner ─────────────────────────────────────────────────── */
    .hero {
        background: linear-gradient(135deg, #6C63FF 0%, #3B82F6 50%, #06B6D4 100%);
        border-radius: 16px;
        padding: 2rem 2.5rem;
        margin-bottom: 1.5rem;
        position: relative;
        overflow: hidden;
    }
    .hero::before {
        content: '';
        position: absolute;
        top: -50%; left: -50%;
        width: 200%; height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.06) 0%, transparent 70%);
        animation: shimmer 8s ease-in-out infinite;
    }
    @keyframes shimmer {
        0%, 100% { transform: translate(0, 0); }
        50% { transform: translate(30%, 30%); }
    }
    .hero h1 {
        color: white;
        font-size: 2rem;
        font-weight: 800;
        margin: 0 0 0.25rem 0;
        position: relative;
    }
    .hero p {
        color: rgba(255,255,255,0.85);
        font-size: 1rem;
        margin: 0;
        position: relative;
    }

    /* ── Metric cards ────────────────────────────────────────────────── */
    .metric-card {
        background: linear-gradient(145deg, #1E2433 0%, #161B26 100%);
        border: 1px solid rgba(108, 99, 255, 0.2);
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        text-align: center;
        transition: transform 0.2s, border-color 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(108, 99, 255, 0.5);
    }
    .metric-label {
        font-size: 0.75rem;
        font-weight: 600;
        color: #8B92A5;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.35rem;
    }
    .metric-value {
        font-size: 1.75rem;
        font-weight: 800;
        background: linear-gradient(135deg, #6C63FF, #06B6D4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .metric-sub {
        font-size: 0.7rem;
        color: #5A6178;
        margin-top: 0.2rem;
    }

    /* ── Section headers ─────────────────────────────────────────────── */
    .section-header {
        font-size: 1.1rem;
        font-weight: 700;
        color: #FAFAFA;
        margin: 1.5rem 0 0.75rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid rgba(108, 99, 255, 0.3);
    }

    /* ── Candidate card ──────────────────────────────────────────────── */
    .candidate-card {
        background: linear-gradient(145deg, #1E2433 0%, #161B26 100%);
        border: 1px solid rgba(108, 99, 255, 0.15);
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 0.75rem;
    }
    .candidate-rank {
        font-size: 0.7rem;
        font-weight: 700;
        color: #6C63FF;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    .candidate-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #FAFAFA;
        margin: 0.15rem 0;
    }
    .candidate-meta {
        font-size: 0.8rem;
        color: #8B92A5;
    }

    /* ── Flag badges ─────────────────────────────────────────────────── */
    .flag-badge {
        background: rgba(239, 68, 68, 0.15);
        border: 1px solid rgba(239, 68, 68, 0.3);
        color: #F87171;
        font-size: 0.75rem;
        padding: 0.3rem 0.75rem;
        border-radius: 6px;
        margin: 0.2rem 0.3rem 0.2rem 0;
        display: inline-block;
    }
    .clean-badge {
        background: rgba(34, 197, 94, 0.15);
        border: 1px solid rgba(34, 197, 94, 0.3);
        color: #4ADE80;
        font-size: 0.75rem;
        padding: 0.3rem 0.75rem;
        border-radius: 6px;
        display: inline-block;
    }

    /* ── Sidebar ─────────────────────────────────────────────────────── */
    .sidebar-title {
        font-size: 1.3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #6C63FF, #06B6D4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.15rem;
    }
    .sidebar-sub {
        font-size: 0.72rem;
        color: #5A6178;
        margin-bottom: 1.5rem;
    }

    /* ── Table fixes ─────────────────────────────────────────────────── */
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
    }

    /* ── Tabs ─────────────────────────────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }

    /* ── Hide streamlit branding ─────────────────────────────────────── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def load_jsonl_from_upload(uploaded_file, limit=None):
    """Parse candidates from an uploaded JSONL file."""
    candidates = []
    content = uploaded_file.getvalue().decode("utf-8")
    for idx, line in enumerate(content.strip().split("\n")):
        if not line.strip():
            continue
        candidate_dict = json.loads(line)
        candidates.append(parse_candidate(candidate_dict))
        if limit is not None and len(candidates) >= limit:
            break
    return candidates


def build_results_dataframe(ranked):
    """Build a DataFrame from ranked candidates with all score breakdowns."""
    raw_scores = [s for s, _ in ranked]
    min_s, max_s = min(raw_scores), max(raw_scores)
    score_range = max_s - min_s

    rows = []
    for rank, (score, cand) in enumerate(ranked, start=1):
        expl = explain_candidate(cand)
        hp = honeypot_penalty(cand)
        flags = explain_honeypot(cand)
        ai_skills = sum(1 for s in cand.skills if s.name.lower() in KEYWORDS)
        norm = (score - min_s) / score_range if score_range > 0 else 1.0

        rows.append({
            "rank": rank,
            "candidate_id": cand.candidate_id,
            "title": cand.profile.current_title,
            "company": cand.profile.current_company,
            "years_exp": cand.profile.years_of_experience,
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
            "location": cand.profile.location,
            "country": cand.profile.country,
            "response_rate": round(cand.redrob_signals.recruiter_response_rate, 2),
            "open_to_work": cand.redrob_signals.open_to_work_flag,
            "notice_days": cand.redrob_signals.notice_period_days,
        })
    return pd.DataFrame(rows)


def render_metric_card(label, value, sub=""):
    sub_html = f'<div class="metric-sub">{sub}</div>' if sub else ""
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {sub_html}
    </div>
    """


def create_radar_chart(row):
    """Create a radar chart for a single candidate's score breakdown."""
    categories = ["Semantic", "Career", "Experience", "Behavior", "Availability"]
    # Normalize scores to [0, 1] range for radar (semantic/career can be large)
    sem_norm = min(row["semantic"] / 100, 1.0) if row["semantic"] > 0 else 0
    car_norm = min(row["career"] / 50, 1.0) if row["career"] > 0 else 0
    values = [sem_norm, car_norm, row["experience"], row["behavior"], row["availability"]]
    values.append(values[0])  # close the polygon
    categories.append(categories[0])

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill="toself",
        fillcolor="rgba(108, 99, 255, 0.2)",
        line=dict(color="#6C63FF", width=2),
        marker=dict(size=6, color="#6C63FF"),
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(
                visible=True, range=[0, 1],
                gridcolor="rgba(255,255,255,0.1)",
                linecolor="rgba(255,255,255,0.1)",
            ),
            angularaxis=dict(
                gridcolor="rgba(255,255,255,0.1)",
                linecolor="rgba(255,255,255,0.1)",
            ),
        ),
        showlegend=False,
        margin=dict(l=60, r=60, t=30, b=30),
        height=320,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#FAFAFA", size=12),
    )
    return fig


def create_score_distribution(df):
    """Create a score distribution histogram."""
    fig = px.histogram(
        df, x="score", nbins=50,
        color_discrete_sequence=["#6C63FF"],
        labels={"score": "Normalized Score", "count": "Candidates"},
    )
    fig.update_layout(
        xaxis_title="Normalized Score",
        yaxis_title="Number of Candidates",
        margin=dict(l=40, r=20, t=20, b=40),
        height=300,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#FAFAFA", size=12),
        xaxis=dict(gridcolor="rgba(255,255,255,0.06)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.06)"),
        bargap=0.05,
    )
    return fig


def create_component_box(df):
    """Create a box plot comparing score component distributions."""
    melt_df = df[["semantic", "career", "experience", "behavior", "availability"]].copy()
    # Normalize semantic and career to [0,1] for fair comparison
    if melt_df["semantic"].max() > 0:
        melt_df["semantic"] = melt_df["semantic"] / melt_df["semantic"].max()
    if melt_df["career"].max() > 0:
        melt_df["career"] = melt_df["career"] / melt_df["career"].max()

    melt_df = melt_df.melt(var_name="Component", value_name="Score (normalized)")
    colors = ["#6C63FF", "#3B82F6", "#06B6D4", "#10B981", "#F59E0B"]

    fig = px.box(
        melt_df, x="Component", y="Score (normalized)",
        color="Component",
        color_discrete_sequence=colors,
    )
    fig.update_layout(
        margin=dict(l=40, r=20, t=20, b=40),
        height=320,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#FAFAFA", size=12),
        xaxis=dict(gridcolor="rgba(255,255,255,0.06)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.06)"),
        showlegend=False,
    )
    return fig


def create_honeypot_pie(df):
    """Pie chart of clean vs flagged candidates."""
    flagged = (df["flags"] > 0).sum()
    clean = len(df) - flagged
    fig = go.Figure(data=[go.Pie(
        labels=["Clean Profiles", "Flagged Profiles"],
        values=[clean, flagged],
        marker=dict(colors=["#10B981", "#EF4444"]),
        hole=0.55,
        textinfo="label+percent",
        textfont=dict(size=12),
    )])
    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        height=300,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#FAFAFA", size=12),
        showlegend=False,
    )
    return fig


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown('<div class="sidebar-title">🏆 Redrob Ranker</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-sub">AI Candidate Ranking System</div>', unsafe_allow_html=True)

    st.markdown("---")

    uploaded_file = st.file_uploader(
        "Upload Candidates (JSONL)",
        type=["jsonl", "json"],
        help="Upload a candidates.jsonl file to rank",
    )

    # Check for default data file
    default_path = PROJECT_ROOT / "data" / "raw" / "candidates.jsonl"
    has_default = default_path.exists()

    if has_default and not uploaded_file:
        st.success("📂 Default dataset detected")

    candidate_limit = st.slider(
        "Candidate Limit",
        min_value=100,
        max_value=100000,
        value=1000,
        step=100,
        help="Limit the number of candidates to process for faster results",
    )

    run_button = st.button(
        "🚀 Run Ranking Pipeline",
        use_container_width=True,
        type="primary",
        disabled=(not uploaded_file and not has_default),
    )

    st.markdown("---")

    st.markdown("##### Pipeline Components")
    st.markdown("""
    - 🔍 Semantic Relevance (25%)
    - 💼 Career Relevance (25%)
    - 📊 Behavioral Signals (20%)
    - 🎯 Experience Fit (15%)
    - ✅ Availability (15%)
    - 🛡️ Honeypot Detection (×)
    """)

    st.markdown("---")
    st.markdown(
        '<div style="font-size:0.7rem; color:#5A6178; text-align:center;">'
        'Built by Peaceful Pigeons in Proxies<br>'
        'Redrob Hackathon 2025'
        '</div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Main content
# ---------------------------------------------------------------------------

# Hero
st.markdown("""
<div class="hero">
    <h1>🏆 Redrob Candidate Ranker</h1>
    <p>Explainable AI/ML candidate ranking with honeypot detection and multi-signal scoring</p>
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Process candidates
# ---------------------------------------------------------------------------

if run_button or "results_df" in st.session_state:

    # Run the pipeline on button press
    if run_button:
        with st.spinner("⚙️ Running ranking pipeline..."):

            progress = st.progress(0, text="Loading candidates...")

            if uploaded_file:
                candidates = load_jsonl_from_upload(uploaded_file, limit=candidate_limit)
            else:
                candidates = load_candidates_jsonl(
                    str(default_path), limit=candidate_limit
                )

            progress.progress(30, text=f"Loaded {len(candidates):,} candidates. Scoring...")

            ranked = rank_candidates(candidates)

            progress.progress(70, text="Building results...")

            df = build_results_dataframe(ranked)

            progress.progress(100, text="Done!")

            st.session_state["results_df"] = df
            st.session_state["candidates_map"] = {
                cand.candidate_id: cand for cand in candidates
            }

        st.toast("✅ Ranking complete!", icon="🎉")

    df = st.session_state["results_df"]

    # ── Metrics row ──────────────────────────────────────────────────
    st.markdown('<div class="section-header">📊 Overview</div>', unsafe_allow_html=True)

    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.markdown(render_metric_card(
            "Total Candidates", f"{len(df):,}"
        ), unsafe_allow_html=True)
    with m2:
        st.markdown(render_metric_card(
            "Top Score", f"{df['score'].max():.4f}",
        ), unsafe_allow_html=True)
    with m3:
        st.markdown(render_metric_card(
            "Average Score", f"{df['score'].mean():.4f}",
        ), unsafe_allow_html=True)
    with m4:
        flagged = (df["flags"] > 0).sum()
        pct = flagged / len(df) * 100
        st.markdown(render_metric_card(
            "Honeypot Flags", f"{flagged:,}",
            f"{pct:.1f}% of candidates"
        ), unsafe_allow_html=True)
    with m5:
        top_title = df.iloc[0]["title"] if len(df) > 0 else "N/A"
        st.markdown(render_metric_card(
            "Top Candidate", f"#{1}",
            top_title[:30]
        ), unsafe_allow_html=True)

    st.markdown("")

    # ── Tabs ─────────────────────────────────────────────────────────
    tab_board, tab_explore, tab_analytics, tab_export = st.tabs([
        "🏅 Leaderboard",
        "🔎 Candidate Explorer",
        "📈 Analytics",
        "📥 Export",
    ])

    # ── Tab 1: Leaderboard ───────────────────────────────────────────
    with tab_board:
        st.markdown('<div class="section-header">Ranked Candidates</div>', unsafe_allow_html=True)

        # Filters
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            search_q = st.text_input(
                "🔍 Search by ID or Title", "", placeholder="e.g. CAND_0088025",
            )
        with fc2:
            flag_filter = st.selectbox(
                "🛡️ Honeypot Filter",
                ["All", "Clean Only", "Flagged Only"],
            )
        with fc3:
            top_n = st.selectbox(
                "📋 Show Top N",
                [20, 50, 100, 500, "All"],
            )

        display_df = df.copy()

        if search_q:
            mask = (
                display_df["candidate_id"].str.contains(search_q, case=False, na=False)
                | display_df["title"].str.contains(search_q, case=False, na=False)
            )
            display_df = display_df[mask]

        if flag_filter == "Clean Only":
            display_df = display_df[display_df["flags"] == 0]
        elif flag_filter == "Flagged Only":
            display_df = display_df[display_df["flags"] > 0]

        if top_n != "All":
            display_df = display_df.head(int(top_n))

        st.dataframe(
            display_df[[
                "rank", "candidate_id", "title", "company",
                "years_exp", "score", "honeypot", "flags",
                "response_rate", "open_to_work",
            ]].rename(columns={
                "rank": "Rank",
                "candidate_id": "Candidate ID",
                "title": "Title",
                "company": "Company",
                "years_exp": "Years Exp",
                "score": "Score",
                "honeypot": "HP Multi",
                "flags": "Flags",
                "response_rate": "Resp Rate",
                "open_to_work": "Open",
            }),
            use_container_width=True,
            height=500,
            hide_index=True,
        )

    # ── Tab 2: Candidate Explorer ────────────────────────────────────
    with tab_explore:
        st.markdown('<div class="section-header">Detailed Candidate View</div>', unsafe_allow_html=True)

        # Candidate selector
        candidate_options = [
            f"#{row['rank']} — {row['candidate_id']} — {row['title']}"
            for _, row in df.head(200).iterrows()
        ]

        if candidate_options:
            selected = st.selectbox("Select a candidate", candidate_options)
            selected_id = selected.split(" — ")[1]
            row = df[df["candidate_id"] == selected_id].iloc[0]

            # Top card
            st.markdown(f"""
            <div class="candidate-card">
                <div class="candidate-rank">Rank #{int(row['rank'])} · Score {row['score']:.4f}</div>
                <div class="candidate-title">{row['title']}</div>
                <div class="candidate-meta">
                    {row['company']} · {row['years_exp']:.0f} years · {row['location']}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Score radar + breakdown
            rc1, rc2 = st.columns([1, 1])

            with rc1:
                st.markdown("**Score Breakdown**")
                fig = create_radar_chart(row)
                st.plotly_chart(fig, use_container_width=True)

            with rc2:
                st.markdown("**Raw Feature Scores**")
                score_data = pd.DataFrame({
                    "Component": ["Semantic", "Career", "Experience", "Behavior", "Availability"],
                    "Score": [row["semantic"], row["career"], row["experience"], row["behavior"], row["availability"]],
                    "Weight": ["25%", "25%", "15%", "20%", "15%"],
                })
                st.dataframe(score_data, hide_index=True, use_container_width=True)

                st.markdown(f"**Honeypot Multiplier:** `{row['honeypot']:.2f}`")

                if row["flags"] > 0:
                    st.markdown("**Consistency Flags:**")
                    for flag in row["flag_details"].split(" | "):
                        st.markdown(f'<span class="flag-badge">⚠️ {flag}</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span class="clean-badge">✅ No inconsistencies detected</span>', unsafe_allow_html=True)

            # Detailed profile from candidate object
            candidates_map = st.session_state.get("candidates_map", {})
            cand = candidates_map.get(selected_id)

            if cand:
                st.markdown("---")
                dc1, dc2 = st.columns(2)

                with dc1:
                    st.markdown("**📝 Profile Summary**")
                    summary = cand.profile.summary
                    if len(summary) > 800:
                        summary = summary[:800] + "..."
                    st.text_area("Summary", summary, height=150, disabled=True, label_visibility="collapsed")

                    st.markdown("**💼 Career History** (top 3)")
                    for i, job in enumerate(cand.career_history[:3]):
                        with st.expander(f"{job.title} @ {job.company} ({job.duration_months}m)", expanded=(i == 0)):
                            desc = job.description
                            if len(desc) > 500:
                                desc = desc[:500] + "..."
                            st.caption(f"{'🟢 Current' if job.is_current else '⚪ Past'} · {job.industry}")
                            st.write(desc)

                with dc2:
                    st.markdown("**🛠️ Top Skills**")
                    skills_data = []
                    for s in cand.skills[:12]:
                        in_keywords = "✅" if s.name.lower() in KEYWORDS else ""
                        skills_data.append({
                            "Skill": s.name,
                            "Proficiency": s.proficiency,
                            "Endorsements": s.endorsements,
                            "Months": s.duration_months,
                            "AI Core": in_keywords,
                        })
                    if skills_data:
                        st.dataframe(pd.DataFrame(skills_data), hide_index=True, use_container_width=True)

                    st.markdown("**📡 Redrob Signals**")
                    signals = cand.redrob_signals
                    sig_data = {
                        "Open to Work": "✅ Yes" if signals.open_to_work_flag else "❌ No",
                        "Recruiter Response Rate": f"{signals.recruiter_response_rate:.2f}",
                        "Interview Completion": f"{signals.interview_completion_rate:.2f}",
                        "GitHub Activity": f"{signals.github_activity_score:.0f}",
                        "Notice Period": f"{signals.notice_period_days} days",
                        "Saved by Recruiters (30d)": f"{signals.saved_by_recruiters_30d}",
                        "Profile Views (30d)": f"{signals.profile_views_received_30d}",
                        "Willing to Relocate": "✅ Yes" if signals.willing_to_relocate else "❌ No",
                        "Work Mode": signals.preferred_work_mode,
                    }
                    for label, val in sig_data.items():
                        st.markdown(f"**{label}:** {val}")

    # ── Tab 3: Analytics ─────────────────────────────────────────────
    with tab_analytics:

        ac1, ac2 = st.columns(2)

        with ac1:
            st.markdown('<div class="section-header">Score Distribution</div>', unsafe_allow_html=True)
            fig = create_score_distribution(df)
            st.plotly_chart(fig, use_container_width=True)

        with ac2:
            st.markdown('<div class="section-header">Honeypot Analysis</div>', unsafe_allow_html=True)
            fig = create_honeypot_pie(df)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown('<div class="section-header">Component Score Distributions (Normalized)</div>', unsafe_allow_html=True)
        fig = create_component_box(df)
        st.plotly_chart(fig, use_container_width=True)

        # Experience vs Score scatter
        st.markdown('<div class="section-header">Experience vs Score</div>', unsafe_allow_html=True)
        fig = px.scatter(
            df, x="years_exp", y="score",
            color="honeypot",
            color_continuous_scale=["#EF4444", "#F59E0B", "#10B981"],
            labels={
                "years_exp": "Years of Experience",
                "score": "Normalized Score",
                "honeypot": "HP Multiplier",
            },
            opacity=0.6,
        )
        fig.update_layout(
            margin=dict(l=40, r=20, t=20, b=40),
            height=350,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#FAFAFA", size=12),
            xaxis=dict(gridcolor="rgba(255,255,255,0.06)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.06)"),
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── Tab 4: Export ────────────────────────────────────────────────
    with tab_export:
        st.markdown('<div class="section-header">Download Ranked Results</div>', unsafe_allow_html=True)

        export_df = df[[
            "candidate_id", "rank", "score", "title", "company",
            "years_exp", "semantic", "career", "experience",
            "behavior", "availability", "honeypot", "flags",
            "flag_details", "ai_skills", "response_rate",
            "open_to_work", "notice_days",
        ]].copy()

        # Build reasoning column
        export_df["reasoning"] = export_df.apply(
            lambda r: (
                f"{r['title']} with {r['years_exp']:.1f} yrs; "
                f"{r['ai_skills']} AI core skills; "
                f"response rate {r['response_rate']:.2f}."
            ),
            axis=1,
        )

        # Submission-format export (4 columns)
        submission_df = export_df[["candidate_id", "rank", "score", "reasoning"]]

        ec1, ec2 = st.columns(2)

        with ec1:
            st.markdown("#### 📄 Submission Format")
            st.caption("4 columns: candidate_id, rank, score, reasoning")

            csv_sub = submission_df.to_csv(index=False)
            st.download_button(
                "⬇️ Download CSV (Submission)",
                csv_sub,
                "ranked_candidates.csv",
                "text/csv",
                use_container_width=True,
            )

            xlsx_buf = io.BytesIO()
            submission_df.to_excel(xlsx_buf, index=False, engine="openpyxl")
            st.download_button(
                "⬇️ Download XLSX (Submission)",
                xlsx_buf.getvalue(),
                "ranked_candidates.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

        with ec2:
            st.markdown("#### 📊 Full Analysis Export")
            st.caption("All columns including score breakdowns and honeypot flags")

            csv_full = export_df.to_csv(index=False)
            st.download_button(
                "⬇️ Download CSV (Full)",
                csv_full,
                "ranked_candidates_full.csv",
                "text/csv",
                use_container_width=True,
            )

            xlsx_full_buf = io.BytesIO()
            export_df.to_excel(xlsx_full_buf, index=False, engine="openpyxl")
            st.download_button(
                "⬇️ Download XLSX (Full)",
                xlsx_full_buf.getvalue(),
                "ranked_candidates_full.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

        st.markdown("---")
        st.markdown("**Preview (Submission Format — Top 10)**")
        st.dataframe(submission_df.head(10), hide_index=True, use_container_width=True)


else:
    # ── Landing page (no data loaded) ────────────────────────────────
    st.markdown("")

    lc1, lc2, lc3 = st.columns([1, 2, 1])
    with lc2:
        st.markdown("""
        ### Getting Started

        1. **Upload** a `candidates.jsonl` file in the sidebar
        2. **Set** the candidate limit (start small for quick results)
        3. **Click** 🚀 Run Ranking Pipeline

        The system will score and rank candidates across six dimensions:

        | Signal | Weight | Description |
        |--------|--------|-------------|
        | 🔍 Semantic | 25% | AI/ML keyword relevance with synonym expansion |
        | 💼 Career | 25% | Real work evidence from job descriptions |
        | 📊 Behavior | 20% | Recruiter response, GitHub, interview signals |
        | 🎯 Experience | 15% | Years + title relevance + retrieval depth |
        | ✅ Availability | 15% | Open-to-work, notice period, flexibility |
        | 🛡️ Honeypot | ×mult | Penalizes inconsistent / fabricated profiles |

        ---

        *Built by **Peaceful Pigeons in Proxies** for the Redrob Hackathon*
        """)
