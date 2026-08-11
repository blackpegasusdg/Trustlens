import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="TrustLens",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 10% 10%, rgba(30, 100, 255, 0.10), transparent 30%),
        radial-gradient(circle at 90% 20%, rgba(120, 60, 255, 0.08), transparent 30%),
        #080d18;
    color: #f5f7fb;
}


/* Sidebar */

section[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #0c1322 0%,
        #080d18 100%
    );
    border-right: 1px solid rgba(255,255,255,0.08);
}

section[data-testid="stSidebar"] * {
    color: #dce5f7;
}


/* Main container */

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1500px;
}


/* Hero */

.hero {
    background:
        linear-gradient(
            135deg,
            rgba(21, 35, 65, 0.95),
            rgba(11, 18, 33, 0.95)
        );
    border: 1px solid rgba(110, 160, 255, 0.18);
    border-radius: 24px;
    padding: 42px;
    margin-bottom: 30px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.30);
}

.hero-title {
    font-size: 44px;
    font-weight: 800;
    letter-spacing: -1px;
    margin-bottom: 10px;
}

.hero-title span {
    background: linear-gradient(
        90deg,
        #ffffff,
        #79aaff
    );
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-subtitle {
    color: #91a4c4;
    font-size: 17px;
    line-height: 1.6;
    max-width: 800px;
}

.status {
    display: inline-flex;
    align-items: center;
    gap: 9px;
    margin-top: 24px;
    padding: 9px 15px;
    border-radius: 999px;
    background: rgba(43, 210, 130, 0.08);
    border: 1px solid rgba(43, 210, 130, 0.25);
    color: #65e6a3;
    font-size: 13px;
    font-weight: 600;
}

.status-dot {
    width: 8px;
    height: 8px;
    background: #45e493;
    border-radius: 50%;
    box-shadow: 0 0 12px rgba(69,228,147,0.8);
}


/* Section */

.section-title {
    font-size: 25px;
    font-weight: 750;
    margin-top: 15px;
    margin-bottom: 5px;
}

.section-subtitle {
    color: #7f92b3;
    font-size: 14px;
    margin-bottom: 22px;
}


/* KPI cards */

.kpi-card {
    background: linear-gradient(
        145deg,
        rgba(24, 34, 55, 0.98),
        rgba(14, 22, 38, 0.98)
    );
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 18px;
    padding: 23px;
    min-height: 135px;
    box-shadow: 0 10px 35px rgba(0,0,0,0.20);
}

.kpi-label {
    color: #8193b3;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.kpi-value {
    color: #f6f8fc;
    font-size: 31px;
    font-weight: 800;
    margin-top: 10px;
}

.kpi-description {
    color: #687d9f;
    font-size: 12px;
    margin-top: 5px;
}


/* Alert cards */

.alert-card {
    border-radius: 16px;
    padding: 20px;
    border: 1px solid rgba(255,255,255,0.07);
    background: rgba(20,29,47,0.85);
}

.alert-high {
    border-left: 4px solid #ff5264;
}

.alert-medium {
    border-left: 4px solid #ffbd55;
}

.alert-low {
    border-left: 4px solid #4bdc91;
}


/* Info cards */

.info-card {
    background: rgba(20,29,47,0.80);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 17px;
    padding: 22px;
    margin-bottom: 15px;
}

.info-title {
    font-size: 16px;
    font-weight: 700;
    margin-bottom: 8px;
}

.info-text {
    color: #8799b8;
    font-size: 13px;
    line-height: 1.6;
}


/* Risk badges */

.risk-high {
    display: inline-block;
    padding: 5px 10px;
    border-radius: 999px;
    background: rgba(255,70,90,0.13);
    color: #ff6b78;
    font-size: 11px;
    font-weight: 700;
}

.risk-medium {
    display: inline-block;
    padding: 5px 10px;
    border-radius: 999px;
    background: rgba(255,190,70,0.13);
    color: #ffc95f;
    font-size: 11px;
    font-weight: 700;
}

.risk-low {
    display: inline-block;
    padding: 5px 10px;
    border-radius: 999px;
    background: rgba(60,220,140,0.13);
    color: #5ce59d;
    font-size: 11px;
    font-weight: 700;
}


/* Footer */

.footer {
    text-align: center;
    color: #536683;
    font-size: 12px;
    margin-top: 60px;
    padding: 25px;
    border-top: 1px solid rgba(255,255,255,0.06);
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# FILE LOCATIONS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_LOCATIONS = [
    BASE_DIR / "data",
    BASE_DIR / "src" / "data"
]


def find_data_file(filename):
    """
    Searches both:
        TrustLens/data/
        TrustLens/src/data/
    """

    for directory in DATA_LOCATIONS:
        path = directory / filename

        if path.exists():
            return path

    return None


# ============================================================
# DATA LOADER
# ============================================================

@st.cache_data
def load_csv(filename):

    path = find_data_file(filename)

    if path is None:
        return None

    try:
        return pd.read_csv(path)
    except Exception:
        return None


# ============================================================
# LOAD ALL DATA
# ============================================================

scores = load_csv("trustlens_scores.csv")
users = load_csv("users.csv")
users_scored = load_csv("users_scored.csv")
comments = load_csv("comments.csv")
comments_scored = load_csv("comments_scored.csv")
ratings = load_csv("ratings.csv")
rating_analysis = load_csv("rating_analysis.csv")
items = load_csv("items.csv")
interactions = load_csv("interactions.csv")
coordination = load_csv("coordination_events.csv")
graph_features = load_csv("graph_features.csv")
recommendation_impact = load_csv("recommendation_impact.csv")
recommendation_ranking = load_csv("recommendation_ranking.csv")


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def first_existing_column(df, candidates):

    if df is None:
        return None

    for col in candidates:
        if col in df.columns:
            return col

    return None


def safe_numeric(df, column):

    if df is None or column not in df.columns:
        return pd.Series(dtype=float)

    return pd.to_numeric(df[column], errors="coerce").fillna(0)


def count_column(df, candidates):

    col = first_existing_column(df, candidates)

    if col is None:
        return 0

    return len(df)


def get_risk_column(df):

    return first_existing_column(
        df,
        [
            "risk_level",
            "risk",
            "risk_category"
        ]
    )


def get_risk_score_column(df):

    return first_existing_column(
        df,
        [
            "risk_score",
            "overall_risk",
            "score"
        ]
    )


def get_user_column(df):

    return first_existing_column(
        df,
        [
            "user_id",
            "userid",
            "user"
        ]
    )


def display_dataframe(df, height=430):

    if df is None or df.empty:

        st.info("No data available for this section.")

        return

    st.dataframe(
        df,
        use_container_width=True,
        height=height,
        hide_index=True
    )


def metric_card(label, value, description=""):

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-description">{description}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def section_header(title, subtitle=""):

    st.markdown(
        f"""
        <div class="section-title">{title}</div>
        <div class="section-subtitle">{subtitle}</div>
        """,
        unsafe_allow_html=True
    )


def risk_color(level):

    level = str(level).upper()

    if "HIGH" in level:
        return "#ff5969"

    if "MEDIUM" in level:
        return "#ffc45c"

    return "#55df99"


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div style="
            font-size:25px;
            font-weight:800;
            margin-bottom:5px;
        ">
            🛡️ TRUSTLENS
        </div>

        <div style="
            color:#7185a6;
            font-size:12px;
            margin-bottom:25px;
        ">
            Social Platform Security Intelligence
        </div>
        """,
        unsafe_allow_html=True
    )

    page = st.radio(
        "COMMAND CENTER",
        [
            "Overview",
            "Risk Intelligence",
            "Account Detection",
            "Comment Analysis",
            "Rating Attacks",
            "Coordination",
            "Recommendation Impact",
            "Network Intelligence",
            "Data Explorer"
        ]
    )

    st.markdown("---")

    st.markdown(
        """
        <div style="
            color:#617594;
            font-size:11px;
            line-height:1.6;
        ">
        TRUSTLENS combines behavioral analysis,
        anomaly detection, coordination analysis,
        rating manipulation detection and
        recommendation-impact analysis.
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# HERO
# ============================================================

st.markdown(
    """
    <div class="hero">

        <div class="hero-title">
            🛡️ TRUST<span>LENS</span>
        </div>

        <div class="hero-subtitle">
            AI-Powered Social Media Authenticity,
            Bias & Recommendation Security Analyzer
        </div>

        <div class="status">
            <div class="status-dot"></div>
            THREAT ANALYSIS ENGINE ACTIVE
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# OVERVIEW
# ============================================================

if page == "Overview":

    section_header(
        "Command Center",
        "Real-time overview of platform integrity and detected manipulation signals."
    )

    total_users = 0
    high_risk = 0
    medium_risk = 0
    rating_attacks = 0
    suspicious_comments = 0
    recommendation_changes = 0

    if scores is not None:

        total_users = len(scores)

        risk_col = get_risk_column(scores)

        if risk_col:

            high_risk = (
                scores[risk_col]
                .astype(str)
                .str.upper()
                .str.contains("HIGH")
                .sum()
            )

            medium_risk = (
                scores[risk_col]
                .astype(str)
                .str.upper()
                .str.contains("MEDIUM")
                .sum()
            )

    if rating_analysis is not None:
        rating_attacks = len(rating_analysis)

    if comments_scored is not None:

        suspicious_col = first_existing_column(
            comments_scored,
            [
                "spam_score",
                "duplicate_score",
                "suspicious_score"
            ]
        )

        if suspicious_col:
            suspicious_comments = (
                pd.to_numeric(
                    comments_scored[suspicious_col],
                    errors="coerce"
                )
                .fillna(0)
                > 50
            ).sum()

    if recommendation_impact is not None:
        recommendation_changes = len(recommendation_impact)


    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        metric_card(
            "USERS ANALYZED",
            f"{total_users:,}",
            "Accounts evaluated"
        )

    with c2:
        metric_card(
            "HIGH RISK",
            f"{high_risk:,}",
            "Critical accounts"
        )

    with c3:
        metric_card(
            "MEDIUM RISK",
            f"{medium_risk:,}",
            "Requires monitoring"
        )

    with c4:
        metric_card(
            "RATING ATTACKS",
            f"{rating_attacks:,}",
            "Suspicious rating events"
        )

    with c5:
        metric_card(
            "RECOMMENDATION EVENTS",
            f"{recommendation_changes:,}",
            "Ranking changes analyzed"
        )


    st.markdown("<br>", unsafe_allow_html=True)


    # --------------------------------------------------------
    # Risk Distribution
    # --------------------------------------------------------

    section_header(
        "Risk Distribution",
        "Distribution of accounts across TrustLens risk categories."
    )

    if scores is not None:

        risk_col = get_risk_column(scores)

        if risk_col:

            risk_counts = (
                scores[risk_col]
                .astype(str)
                .value_counts()
                .reset_index()
            )

            risk_counts.columns = [
                "Risk Level",
                "Users"
            ]

            fig = px.bar(
                risk_counts,
                x="Risk Level",
                y="Users",
                text="Users",
                template="plotly_dark"
            )

            fig.update_traces(
                textposition="outside"
            )

            fig.update_layout(
                height=420,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=20, r=20, t=30, b=20)
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )


    # --------------------------------------------------------
    # Top suspicious users
    # --------------------------------------------------------

    section_header(
        "Most Suspicious Accounts",
        "Accounts with the highest combined threat scores."
    )

    if scores is not None:

        risk_score_col = get_risk_score_column(scores)

        if risk_score_col:

            top = scores.sort_values(
                risk_score_col,
                ascending=False
            ).head(10)

            display_dataframe(top, 400)


# ============================================================
# RISK INTELLIGENCE
# ============================================================

elif page == "Risk Intelligence":

    section_header(
        "Risk Intelligence",
        "Combined threat scoring across multiple manipulation signals."
    )

    if scores is None:

        st.error("trustlens_scores.csv could not be found.")

    else:

        risk_score_col = get_risk_score_column(scores)
        risk_col = get_risk_column(scores)

        c1, c2, c3 = st.columns(3)

        with c1:
            metric_card(
                "AVERAGE RISK",
                f"{safe_numeric(scores, risk_score_col).mean():.2f}"
                if risk_score_col else "N/A",
                "Mean platform risk"
            )

        with c2:
            metric_card(
                "MAX RISK",
                f"{safe_numeric(scores, risk_score_col).max():.2f}"
                if risk_score_col else "N/A",
                "Highest detected risk"
            )

        with c3:
            metric_card(
                "ACCOUNTS",
                f"{len(scores):,}",
                "Total analyzed"
            )


        if risk_score_col:

            chart_data = scores.copy()

            chart_data[risk_score_col] = pd.to_numeric(
                chart_data[risk_score_col],
                errors="coerce"
            ).fillna(0)

            fig = px.histogram(
                chart_data,
                x=risk_score_col,
                nbins=25,
                template="plotly_dark",
                title="Risk Score Distribution"
            )

            fig.update_layout(
                height=430,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )


        st.markdown("### Risk Table")

        if risk_score_col:

            display_cols = [
                col for col in [
                    "user_id",
                    "bot_score",
                    "spam_score",
                    "duplicate_score",
                    "coordination_score",
                    "rating_attack_score",
                    "campaign_boost",
                    "risk_score",
                    "risk_level"
                ]
                if col in scores.columns
            ]

            table = scores.sort_values(
                risk_score_col,
                ascending=False
            )

            display_dataframe(
                table[display_cols].head(50),
                550
            )


# ============================================================
# ACCOUNT DETECTION
# ============================================================

elif page == "Account Detection":

    section_header(
        "Account Detection",
        "Behavioral indicators used to identify suspicious and potentially automated accounts."
    )

    df = scores if scores is not None else users_scored

    if df is None:

        st.error("Account scoring data is unavailable.")

    else:

        bot_col = first_existing_column(
            df,
            [
                "bot_score",
                "bot_probability",
                "bot_risk"
            ]
        )

        if bot_col:

            bot_values = safe_numeric(df, bot_col)

            c1, c2, c3 = st.columns(3)

            with c1:
                metric_card(
                    "AVG BOT SCORE",
                    f"{bot_values.mean():.2f}",
                    "Average automation signal"
                )

            with c2:
                metric_card(
                    "HIGH BOT SIGNAL",
                    f"{(bot_values >= 70).sum():,}",
                    "Score ≥ 70"
                )

            with c3:
                metric_card(
                    "LOW BOT SIGNAL",
                    f"{(bot_values < 30).sum():,}",
                    "Score < 30"
                )


            chart = pd.DataFrame({
                "Bot Score": bot_values
            })

            fig = px.histogram(
                chart,
                x="Bot Score",
                nbins=20,
                template="plotly_dark",
                title="Bot Score Distribution"
            )

            fig.update_layout(
                height=400,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )


        display_dataframe(
            df.sort_values(
                bot_col,
                ascending=False
            ).head(50)
            if bot_col else df.head(50),
            550
        )


# ============================================================
# COMMENT ANALYSIS
# ============================================================

elif page == "Comment Analysis":

    section_header(
        "Comment Authenticity",
        "Detection of spam, duplicates and suspicious commenting behavior."
    )

    df = comments_scored if comments_scored is not None else comments

    if df is None:

        st.error("Comment data is unavailable.")

    else:

        spam_col = first_existing_column(
            df,
            [
                "spam_score",
                "spam_risk"
            ]
        )

        duplicate_col = first_existing_column(
            df,
            [
                "duplicate_score",
                "dup_score"
            ]
        )

        c1, c2, c3 = st.columns(3)

        with c1:
            metric_card(
                "COMMENTS",
                f"{len(df):,}",
                "Comments analyzed"
            )

        with c2:
            metric_card(
                "SPAM SIGNAL",
                f"{safe_numeric(df, spam_col).mean():.2f}"
                if spam_col else "N/A",
                "Average spam score"
            )

        with c3:
            metric_card(
                "DUPLICATE SIGNAL",
                f"{safe_numeric(df, duplicate_col).mean():.2f}"
                if duplicate_col else "N/A",
                "Average duplicate score"
            )


        if spam_col and duplicate_col:

            plot_df = pd.DataFrame({
                "Spam Score": safe_numeric(df, spam_col),
                "Duplicate Score": safe_numeric(df, duplicate_col)
            })

            fig = px.scatter(
                plot_df,
                x="Spam Score",
                y="Duplicate Score",
                template="plotly_dark",
                title="Spam vs Duplicate Behavior"
            )

            fig.update_layout(
                height=450,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )


        display_dataframe(
            df.head(100),
            550
        )


# ============================================================
# RATING ATTACKS
# ============================================================

elif page == "Rating Attacks":

    section_header(
        "Rating Manipulation",
        "Detection of suspicious rating behavior and potential review manipulation."
    )

    if rating_analysis is None:

        st.error("rating_analysis.csv could not be found.")

    else:

        df = rating_analysis

        attack_col = first_existing_column(
            df,
            [
                "rating_attack_score",
                "attack_score",
                "rating_score"
            ]
        )

        c1, c2, c3 = st.columns(3)

        with c1:
            metric_card(
                "RATINGS ANALYZED",
                f"{len(df):,}",
                "Rating events"
            )

        with c2:
            metric_card(
                "AVG ATTACK SCORE",
                f"{safe_numeric(df, attack_col).mean():.2f}"
                if attack_col else "N/A",
                "Average manipulation signal"
            )

        with c3:
            metric_card(
                "HIGH ATTACK SIGNAL",
                f"{(safe_numeric(df, attack_col) >= 70).sum():,}"
                if attack_col else "N/A",
                "Score ≥ 70"
            )


        if attack_col:

            plot_df = df.copy()

            plot_df[attack_col] = pd.to_numeric(
                plot_df[attack_col],
                errors="coerce"
            ).fillna(0)

            fig = px.histogram(
                plot_df,
                x=attack_col,
                nbins=20,
                template="plotly_dark",
                title="Rating Attack Score Distribution"
            )

            fig.update_layout(
                height=400,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )


        display_dataframe(
            df.sort_values(
                attack_col,
                ascending=False
            ).head(100)
            if attack_col else df.head(100),
            550
        )


# ============================================================
# COORDINATION
# ============================================================

elif page == "Coordination":

    section_header(
        "Coordinated Activity",
        "Detection of groups of accounts behaving similarly or engaging in synchronized activity."
    )

    df = coordination

    if df is None:

        st.warning(
            "coordination_events.csv was not found."
        )

        if scores is not None and "coordination_score" in scores.columns:

            st.info(
                "Showing coordination scores from the TrustLens scoring dataset."
            )

            coord_df = scores[
                [
                    c for c in [
                        "user_id",
                        "coordination_score",
                        "risk_score",
                        "risk_level"
                    ]
                    if c in scores.columns
                ]
            ].sort_values(
                "coordination_score",
                ascending=False
            )

            display_dataframe(
                coord_df.head(100),
                550
            )

    else:

        metric_card(
            "COORDINATION EVENTS",
            f"{len(df):,}",
            "Detected synchronized events"
        )

        display_dataframe(
            df.head(150),
            600
        )


# ============================================================
# RECOMMENDATION IMPACT
# ============================================================

elif page == "Recommendation Impact":

    section_header(
        "Recommendation Security",
        "Measures how suspicious activity changes recommendation rankings."
    )

    if recommendation_impact is None:

        st.error(
            "recommendation_impact.csv could not be found."
        )

    else:

        df = recommendation_impact.copy()

        rank_change_col = first_existing_column(
            df,
            [
                "rank_change",
                "change_in_rank"
            ]
        )

        score_change_col = first_existing_column(
            df,
            [
                "score_change",
                "change_in_score"
            ]
        )

        c1, c2, c3 = st.columns(3)

        with c1:

            metric_card(
                "ITEMS ANALYZED",
                f"{len(df):,}",
                "Recommendation candidates"
            )

        with c2:

            if rank_change_col:

                rank_values = safe_numeric(
                    df,
                    rank_change_col
                )

                metric_card(
                    "LARGEST RANK SHIFT",
                    f"{rank_values.abs().max():.0f}",
                    "Absolute rank change"
                )

            else:

                metric_card(
                    "RANK SHIFT",
                    "N/A",
                    "Not available"
                )

        with c3:

            if score_change_col:

                score_values = safe_numeric(
                    df,
                    score_change_col
                )

                metric_card(
                    "MAX SCORE CHANGE",
                    f"{score_values.abs().max():.3f}",
                    "Recommendation score"
                )

            else:

                metric_card(
                    "SCORE CHANGE",
                    "N/A",
                    "Not available"
                )


        if rank_change_col:

            plot_df = df.copy()

            plot_df[rank_change_col] = pd.to_numeric(
                plot_df[rank_change_col],
                errors="coerce"
            ).fillna(0)

            plot_df["Direction"] = np.where(
                plot_df[rank_change_col] > 0,
                "Moved Down",
                np.where(
                    plot_df[rank_change_col] < 0,
                    "Moved Up",
                    "No Change"
                )
            )

            fig = px.scatter(
                plot_df,
                x=rank_change_col,
                y=score_change_col
                if score_change_col
                else rank_change_col,
                hover_name="item_id"
                if "item_id" in plot_df.columns
                else None,
                color="Direction",
                template="plotly_dark",
                title="Recommendation Ranking Impact"
            )

            fig.update_layout(
                height=450,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )


        if rank_change_col:

            largest = df.copy()

            largest["_abs_change"] = (
                pd.to_numeric(
                    largest[rank_change_col],
                    errors="coerce"
                )
                .abs()
            )

            largest = (
                largest
                .sort_values(
                    "_abs_change",
                    ascending=False
                )
                .drop(columns=["_abs_change"])
                .head(30)
            )

            st.markdown("### Largest Recommendation Changes")

            display_dataframe(
                largest,
                550
            )


# ============================================================
# NETWORK INTELLIGENCE
# ============================================================

elif page == "Network Intelligence":

    section_header(
        "Network Intelligence",
        "Graph-based view of suspicious user relationships and behavioral structure."
    )

    if graph_features is None:

        st.warning(
            "graph_features.csv could not be found."
        )

    else:

        df = graph_features.copy()

        st.markdown(
            """
            <div class="info-card">

                <div class="info-title">
                    🕸️ Behavioral Network Analysis
                </div>

                <div class="info-text">
                    TrustLens analyzes relationships between users,
                    interactions and suspicious behavioral patterns.
                    High-connectivity or structurally unusual accounts
                    can indicate coordinated activity.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


        degree_col = first_existing_column(
            df,
            [
                "degree",
                "degree_centrality",
                "connections"
            ]
        )

        if degree_col:

            numeric_degree = safe_numeric(
                df,
                degree_col
            )

            c1, c2, c3 = st.columns(3)

            with c1:

                metric_card(
                    "NODES",
                    f"{len(df):,}",
                    "Accounts represented"
                )

            with c2:

                metric_card(
                    "AVG CONNECTIVITY",
                    f"{numeric_degree.mean():.2f}",
                    "Mean connections"
                )

            with c3:

                metric_card(
                    "MAX CONNECTIVITY",
                    f"{numeric_degree.max():.0f}",
                    "Highest connectivity"
                )


            plot_df = df.copy()

            plot_df[degree_col] = pd.to_numeric(
                plot_df[degree_col],
                errors="coerce"
            ).fillna(0)

            user_col = get_user_column(plot_df)

            if user_col:

                top = plot_df.nlargest(
                    25,
                    degree_col
                )

                fig = px.bar(
                    top,
                    x=degree_col,
                    y=user_col,
                    orientation="h",
                    template="plotly_dark",
                    title="Most Connected Accounts"
                )

                fig.update_layout(
                    height=600,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )


        display_dataframe(
            df.head(100),
            550
        )


# ============================================================
# DATA EXPLORER
# ============================================================

elif page == "Data Explorer":

    section_header(
        "Data Explorer",
        "Inspect the underlying TrustLens datasets."
    )

    datasets = {
        "TrustLens Scores": scores,
        "Users": users,
        "Users Scored": users_scored,
        "Comments": comments,
        "Comments Scored": comments_scored,
        "Ratings": ratings,
        "Rating Analysis": rating_analysis,
        "Items": items,
        "Interactions": interactions,
        "Coordination Events": coordination,
        "Graph Features": graph_features,
        "Recommendation Impact": recommendation_impact,
        "Recommendation Ranking": recommendation_ranking
    }

    available = [
        name
        for name, dataframe in datasets.items()
        if dataframe is not None
    ]

    if not available:

        st.error("No TrustLens datasets were found.")

    else:

        selected_dataset = st.selectbox(
            "Select dataset",
            available
        )

        selected_df = datasets[selected_dataset]

        c1, c2, c3 = st.columns(3)

        with c1:

            metric_card(
                "ROWS",
                f"{len(selected_df):,}",
                "Dataset records"
            )

        with c2:

            metric_card(
                "COLUMNS",
                f"{len(selected_df.columns):,}",
                "Dataset fields"
            )

        with c3:

            metric_card(
                "MEMORY",
                f"{selected_df.memory_usage(deep=True).sum() / 1024:.1f} KB",
                "Approximate size"
            )


        st.markdown("### Dataset Preview")

        display_dataframe(
            selected_df.head(200),
            650
        )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        🛡️ TRUSTLENS &nbsp;•&nbsp;
        AI-Powered Social Media Authenticity & Security Analysis
        <br>
        Behavioral Detection • Coordination Analysis •
        Rating Security • Recommendation Integrity
    </div>
    """,
    unsafe_allow_html=True
)