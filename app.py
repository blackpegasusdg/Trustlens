import os
import re
import html
import subprocess
import sys
from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from textwrap import dedent


# ============================================================
# CONFIGURATION
# ============================================================

DEFAULT_RENDER_API = "https://trustlens-9idp.onrender.com"

RENDER_API = os.getenv(
    "TRUSTLENS_API_URL",
    DEFAULT_RENDER_API
).rstrip("/")

API_TIMEOUT = int(
    os.getenv("TRUSTLENS_API_TIMEOUT", "20")
)

DETECTOR_TIMEOUT = int(
    os.getenv("TRUSTLENS_DETECTOR_TIMEOUT", "120")
)


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

st.markdown(
    """
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(
            circle at 10% 10%,
            rgba(30,100,255,0.10),
            transparent 30%
        ),
        radial-gradient(
            circle at 90% 20%,
            rgba(120,60,255,0.08),
            transparent 30%
        ),
        #080d18;
    color: #f5f7fb;
}

section[data-testid="stSidebar"] {
    background:
        linear-gradient(
            180deg,
            #0c1322 0%,
            #080d18 100%
        );
    border-right:
        1px solid rgba(255,255,255,0.08);
}

section[data-testid="stSidebar"] * {
    color: #dce5f7;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1500px;
}

.hero {
    background:
        linear-gradient(
            135deg,
            rgba(21,35,65,0.97),
            rgba(11,18,33,0.97)
        );
    border:
        1px solid rgba(110,160,255,0.18);
    border-radius: 24px;
    padding: 42px;
    margin-bottom: 30px;
    box-shadow:
        0 20px 60px rgba(0,0,0,0.30);
}

.hero-title {
    font-size: 44px;
    font-weight: 800;
    letter-spacing: -1px;
    margin-bottom: 10px;
}

.hero-title span {
    background:
        linear-gradient(
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
    max-width: 850px;
}

.status {
    display: inline-flex;
    align-items: center;
    gap: 9px;
    margin-top: 24px;
    padding: 9px 15px;
    border-radius: 999px;
    background: rgba(43,210,130,0.08);
    border: 1px solid rgba(43,210,130,0.25);
    color: #65e6a3;
    font-size: 13px;
    font-weight: 600;
}

.status-dot {
    width: 8px;
    height: 8px;
    background: #45e493;
    border-radius: 50%;
    box-shadow:
        0 0 12px rgba(69,228,147,0.8);
}

.status-dot.offline {
    background: #ff6666;
    box-shadow:
        0 0 12px rgba(255,80,80,0.8);
}

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

.kpi-card {
    background:
        linear-gradient(
            145deg,
            rgba(24,34,55,0.98),
            rgba(14,22,38,0.98)
        );
    border:
        1px solid rgba(255,255,255,0.07);
    border-radius: 18px;
    padding: 23px;
    min-height: 135px;
    box-shadow:
        0 10px 35px rgba(0,0,0,0.20);
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

.info-card {
    background:
        rgba(20,29,47,0.80);
    border:
        1px solid rgba(255,255,255,0.07);
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

.attack-card {
    background:
        linear-gradient(
            145deg,
            rgba(20,32,55,0.98),
            rgba(12,20,36,0.98)
        );
    border:
        1px solid rgba(105,150,255,0.18);
    border-radius: 20px;
    padding: 25px;
    margin-bottom: 20px;
}

.attack-card-title {
    font-size: 20px;
    font-weight: 750;
    margin-bottom: 6px;
}

.attack-card-text {
    color: #8193b3;
    font-size: 13px;
    line-height: 1.6;
}

.warning-box {
    background: rgba(255,185,65,0.08);
    border: 1px solid rgba(255,185,65,0.25);
    border-radius: 14px;
    padding: 15px;
    color: #ffd27a;
}

.success-box {
    background: rgba(60,220,140,0.08);
    border: 1px solid rgba(60,220,140,0.25);
    border-radius: 14px;
    padding: 15px;
    color: #6ce6a4;
}

.danger-box {
    background: rgba(255,70,70,0.08);
    border: 1px solid rgba(255,70,70,0.25);
    border-radius: 14px;
    padding: 15px;
    color: #ff8585;
}

.live-post-card {
    background:
        linear-gradient(
            145deg,
            rgba(20,31,52,0.98),
            rgba(11,19,34,0.98)
        );
    border:
        1px solid rgba(110,160,255,0.14);
    border-radius: 18px;
    padding: 22px;
    margin-bottom: 15px;
}

.live-post-user {
    font-size: 16px;
    font-weight: 700;
    color: #f3f6ff;
}

.live-post-text {
    color: #aab9d1;
    font-size: 14px;
    line-height: 1.6;
    margin-top: 8px;
    margin-bottom: 15px;
}

.live-badge-safe,
.live-badge-warning,
.live-badge-danger {
    display: inline-block;
    padding: 6px 12px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 700;
}

.live-badge-safe {
    background: rgba(50,220,130,0.10);
    border: 1px solid rgba(50,220,130,0.25);
    color: #6ce6a4;
}

.live-badge-warning {
    background: rgba(255,185,65,0.10);
    border: 1px solid rgba(255,185,65,0.25);
    color: #ffd27a;
}

.live-badge-danger {
    background: rgba(255,70,70,0.10);
    border: 1px solid rgba(255,70,70,0.25);
    color: #ff8585;
}

.footer {
    text-align: center;
    color: #536683;
    font-size: 12px;
    margin-top: 60px;
    padding: 25px;
    border-top: 1px solid rgba(255,255,255,0.06);
}

div[data-testid="stButton"] > button {
    border-radius: 10px;
    border: 1px solid rgba(110,160,255,0.25);
    background: rgba(25,40,70,0.85);
    color: #eaf0ff;
    font-weight: 650;
}

div[data-testid="stButton"] > button:hover {
    border-color: rgba(110,160,255,0.55);
    color: white;
}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# HTML HELPERS
# ============================================================

def render_html(content):
    content = dedent(content).strip()

    if hasattr(st, "html"):
        st.html(content)
    else:
        st.markdown(
            content,
            unsafe_allow_html=True
        )


def safe_html(value):
    return html.escape(
        str(value)
    )


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_LOCATIONS = [
    BASE_DIR / "data",
    BASE_DIR / "src" / "data"
]

LIVE_DATA_DIR = (
    BASE_DIR /
    "data" /
    "live"
)

ATTACK_DATA_DIR = (
    BASE_DIR /
    "data" /
    "simulated_attacks"
)

ATTACK_RESULTS_DIR = (
    BASE_DIR /
    "data" /
    "attack_results"
)


def ensure_directories():

    LIVE_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    ATTACK_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    ATTACK_RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


ensure_directories()


# ============================================================
# GENERAL DATA HELPERS
# ============================================================

def find_data_file(filename):

    for directory in DATA_LOCATIONS:

        path = directory / filename

        if path.exists():
            return path

    return None


@st.cache_data(ttl=30)
def load_csv(filename):

    path = find_data_file(filename)

    if path is None:
        return None

    try:

        return pd.read_csv(
            path,
            low_memory=False
        )

    except Exception:
        return None


@st.cache_data(ttl=5)
def load_live_csv(filename):

    path = LIVE_DATA_DIR / filename

    if not path.exists():
        return None

    try:

        return pd.read_csv(
            path,
            low_memory=False
        )

    except Exception:
        return None


def first_existing_column(
    df,
    candidates
):

    if df is None:
        return None

    normalized = {
        str(c).strip().lower(): c
        for c in df.columns
    }

    for candidate in candidates:

        key = str(candidate).strip().lower()

        if key in normalized:
            return normalized[key]

    return None


def safe_numeric(
    df,
    column
):

    if (
        df is None
        or column is None
        or column not in df.columns
    ):
        return pd.Series(
            0.0,
            index=(
                df.index
                if df is not None
                else []
            )
        )

    values = (
        df[column]
        .astype(str)
        .str.replace(
            "%",
            "",
            regex=False
        )
    )

    return pd.to_numeric(
        values,
        errors="coerce"
    ).fillna(0)


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


def normalize_dataframe(df):

    if df is None:
        return None

    result = df.copy()

    result.columns = [
        str(column)
        .strip()
        .lower()
        for column in result.columns
    ]

    return result


def display_dataframe(
    df,
    height=430
):

    if (
        df is None
        or df.empty
    ):

        st.info(
            "No data available."
        )

        return

    st.dataframe(
        df,
        use_container_width=True,
        height=height,
        hide_index=True
    )


# ============================================================
# UI HELPERS
# ============================================================

def metric_card(
    label,
    value,
    description=""
):

    render_html(
        f"""
        <div class="kpi-card">

            <div class="kpi-label">
                {safe_html(label)}
            </div>

            <div class="kpi-value">
                {safe_html(value)}
            </div>

            <div class="kpi-description">
                {safe_html(description)}
            </div>

        </div>
        """
    )


def section_header(
    title,
    subtitle=""
):

    render_html(
        f"""
        <div class="section-title">
            {safe_html(title)}
        </div>

        <div class="section-subtitle">
            {safe_html(subtitle)}
        </div>
        """
    )


def make_chart_layout(
    fig,
    height=430
):

    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(
            l=30,
            r=30,
            t=60,
            b=30
        ),
        font=dict(
            color="#dce5f7"
        )
    )

    return fig


# ============================================================
# LIVE API
# ============================================================

@st.cache_data(
    ttl=10,
    show_spinner=False
)
def check_api_health():

    try:

        response = requests.get(
            f"{RENDER_API}/",
            timeout=8
        )

        return {
            "online": True,
            "status": response.status_code,
            "message": "API reachable"
        }

    except requests.exceptions.Timeout:

        return {
            "online": False,
            "status": None,
            "message": "API timeout"
        }

    except Exception as exc:

        return {
            "online": False,
            "status": None,
            "message": str(exc)
        }


@st.cache_data(
    ttl=5,
    show_spinner=False
)
def load_live_analysis():

    try:

        response = requests.get(
            f"{RENDER_API}/analysis",
            timeout=API_TIMEOUT
        )

        response.raise_for_status()

        data = response.json()

        if data is None:
            return pd.DataFrame()

        if isinstance(data, dict):

            if "data" in data:
                data = data["data"]

            elif "analysis" in data:
                data = data["analysis"]

            else:
                data = [data]

        if not isinstance(
            data,
            list
        ):

            return pd.DataFrame()

        return pd.DataFrame(data)

    except requests.exceptions.Timeout:

        return None

    except requests.exceptions.ConnectionError:

        return None

    except Exception:

        return None


def refresh_live_data():

    load_live_analysis.clear()
    load_live_csv.clear()


# ============================================================
# LIVE ANALYSIS HELPERS
# ============================================================

def get_live_suspicious_mask(df):

    if (
        df is None
        or df.empty
    ):

        return pd.Series(
            False,
            index=(
                df.index
                if df is not None
                else []
            )
        )

    suspicious_col = first_existing_column(
        df,
        [
            "suspicious",
            "is_suspicious",
            "flagged"
        ]
    )

    if suspicious_col:

        return (
            df[suspicious_col]
            .astype(str)
            .str.lower()
            .isin(
                [
                    "true",
                    "1",
                    "yes",
                    "suspicious",
                    "high",
                    "medium"
                ]
            )
        )

    risk_col = first_existing_column(
        df,
        [
            "risk_level",
            "risk_category"
        ]
    )

    if risk_col:

        return (
            df[risk_col]
            .astype(str)
            .str.upper()
            .isin(
                [
                    "MEDIUM",
                    "HIGH",
                    "CRITICAL"
                ]
            )
        )

    score_col = first_existing_column(
        df,
        [
            "risk_score",
            "overall_risk",
            "score"
        ]
    )

    if score_col:

        scores = safe_numeric(
            df,
            score_col
        )

        maximum = scores.max()

        threshold = (
            70
            if maximum > 10
            else 0.70
        )

        return scores >= threshold

    return pd.Series(
        False,
        index=df.index
    )


def infer_risk_level(
    score
):

    try:

        value = float(score)

    except Exception:

        return "UNKNOWN"

    if value <= 1:
        value *= 100

    if value >= 80:
        return "CRITICAL"

    if value >= 60:
        return "HIGH"

    if value >= 30:
        return "MEDIUM"

    return "LOW"


def get_risk_badge_html(
    risk_level,
    suspicious=False
):

    level = str(
        risk_level or "UNKNOWN"
    ).upper()

    if (
        suspicious
        or level in [
            "HIGH",
            "CRITICAL"
        ]
    ):

        return (
            '<span class="live-badge-danger">'
            '⚠️ SUSPICIOUS'
            '</span>'
        )

    if level == "MEDIUM":

        return (
            '<span class="live-badge-warning">'
            '⚠️ MEDIUM RISK'
            '</span>'
        )

    return (
        '<span class="live-badge-safe">'
        '✅ SAFE'
        '</span>'
    )


# ============================================================
# DATASETS
# ============================================================

scores = load_csv(
    "trustlens_scores.csv"
)

users = load_csv(
    "users.csv"
)

users_scored = load_csv(
    "users_scored.csv"
)

comments = load_csv(
    "comments.csv"
)

comments_scored = load_csv(
    "comments_scored.csv"
)

ratings = load_csv(
    "ratings.csv"
)

rating_analysis = load_csv(
    "rating_analysis.csv"
)

items = load_csv(
    "items.csv"
)

interactions = load_csv(
    "interactions.csv"
)

coordination = load_csv(
    "coordination_events.csv"
)

graph_features = load_csv(
    "graph_features.csv"
)

recommendation_impact = load_csv(
    "recommendation_impact.csv"
)

recommendation_ranking = load_csv(
    "recommendation_ranking.csv"
)

live_posts = load_live_csv(
    "posts.csv"
)

live_analysis = load_live_analysis()

live_users = load_live_csv(
    "users.csv"
)


# ============================================================
# SIDEBAR
# ============================================================

api_status = check_api_health()

with st.sidebar:

    render_html(
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
            margin-bottom:20px;
        ">
            Social Platform Security Intelligence
        </div>
        """
    )

    if api_status["online"]:

        render_html(
            """
            <div class="success-box"
                 style="font-size:12px;">
                🟢 FastAPI backend online
            </div>
            """
        )

    else:

        render_html(
            """
            <div class="danger-box"
                 style="font-size:12px;">
                🔴 FastAPI backend unavailable
            </div>
            """
        )

    if st.button(
        "🔄 Refresh Live Data",
        use_container_width=True
    ):

        refresh_live_data()
        st.rerun()

    st.markdown("---")

    page = st.radio(
        "COMMAND CENTER",
        [
            "Overview",
            "Live Social Analysis",
            "Risk Intelligence",
            "Account Detection",
            "Comment Analysis",
            "Rating Attacks",
            "Coordination",
            "Recommendation Impact",
            "Network Intelligence",
            "Controlled Attack Lab",
            "Data Explorer"
        ]
    )

    st.markdown("---")

    render_html(
        f"""
        <div style="
            color:#617594;
            font-size:11px;
            line-height:1.6;
        ">

            <b>Backend</b><br>
            {safe_html(RENDER_API)}

            <br><br>

            TrustLens combines behavioral analysis,
            anomaly detection, coordination analysis,
            rating manipulation detection and
            recommendation-impact analysis.

        </div>
        """
    )


# ============================================================
# HERO
# ============================================================

hero_status_class = (
    ""
    if api_status["online"]
    else "offline"
)

hero_status_text = (
    "THREAT ANALYSIS ENGINE ACTIVE"
    if api_status["online"]
    else "LIVE API CONNECTION DEGRADED"
)

render_html(
    f"""
    <div class="hero">

        <div class="hero-title">
            🛡️ TRUST<span>LENS</span>
        </div>

        <div class="hero-subtitle">
            AI-Powered Social Media Authenticity,
            Bias & Recommendation Security Analyzer
        </div>

        <div class="status">

            <div class="status-dot
                {hero_status_class}">
            </div>

            {safe_html(hero_status_text)}

        </div>

    </div>
    """
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
    recommendation_events = 0
    live_posts_count = (
        len(live_analysis)
        if live_analysis is not None
        else 0
    )

    if scores is not None:

        total_users = len(scores)

        risk_col = get_risk_column(
            scores
        )

        if risk_col:

            risk_values = (
                scores[risk_col]
                .astype(str)
                .str.upper()
            )

            high_risk = (
                risk_values
                .str.contains(
                    "HIGH|CRITICAL",
                    regex=True
                )
                .sum()
            )

            medium_risk = (
                risk_values
                .eq("MEDIUM")
                .sum()
            )

    if rating_analysis is not None:

        rating_attacks = len(
            rating_analysis
        )

    if recommendation_impact is not None:

        recommendation_events = len(
            recommendation_impact
        )

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
            "High / critical accounts"
        )

    with c3:

        metric_card(
            "MEDIUM RISK",
            f"{medium_risk:,}",
            "Requires monitoring"
        )

    with c4:

        metric_card(
            "RATING EVENTS",
            f"{rating_attacks:,}",
            "Rating records analyzed"
        )

    with c5:

        metric_card(
            "LIVE POSTS",
            f"{live_posts_count:,}",
            "Posts received by TrustLens"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # --------------------------------------------------------
    # RISK DISTRIBUTION
    # --------------------------------------------------------

    section_header(
        "Risk Distribution",
        "Distribution of accounts across TrustLens risk categories."
    )

    if scores is not None:

        risk_col = get_risk_column(
            scores
        )

        if risk_col:

            risk_counts = (
                scores[risk_col]
                .astype(str)
                .str.upper()
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

            make_chart_layout(
                fig,
                420
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    # --------------------------------------------------------
    # TOP ACCOUNTS
    # --------------------------------------------------------

    section_header(
        "Most Suspicious Accounts",
        "Accounts with the highest combined threat scores."
    )

    if scores is not None:

        score_col = get_risk_score_column(
            scores
        )

        if score_col:

            top = (
                scores
                .assign(
                    _risk_numeric=safe_numeric(
                        scores,
                        score_col
                    )
                )
                .sort_values(
                    "_risk_numeric",
                    ascending=False
                )
                .drop(
                    columns="_risk_numeric"
                )
                .head(10)
            )

            display_dataframe(
                top,
                400
            )


# ============================================================
# LIVE SOCIAL ANALYSIS
# ============================================================

elif page == "Live Social Analysis":

    section_header(
        "Live Social Analysis",
        "Real-time TrustLens analysis of posts submitted through the social platform."
    )

    c_refresh, c_status = st.columns(
        [1, 4]
    )

    with c_refresh:

        if st.button(
            "🔄 Refresh",
            use_container_width=True
        ):

            refresh_live_data()
            st.rerun()

    with c_status:

        if live_analysis is not None:

            render_html(
                """
                <div class="success-box">
                    🟢 LIVE TRUSTLENS ANALYSIS CONNECTED
                </div>
                """
            )

        else:

            render_html(
                """
                <div class="warning-box">
                    🟡 LIVE ANALYSIS DATA UNAVAILABLE
                </div>
                """
            )

    st.markdown(
        "<br>",
        unsafe_allow_html=True
    )

    if live_analysis is None:

        st.warning(
            "TrustLens could not retrieve live analysis from the FastAPI backend."
        )

        st.markdown(
            """
            ### Expected pipeline

            **React → FastAPI → TrustLens Analysis → `/analysis` → Dashboard**

            If your Render backend has just started, wait a few seconds and
            press **Refresh**.
            """
        )

    else:

        df = normalize_dataframe(
            live_analysis
        )

        if df.empty:

            st.info(
                "The API is online but no analysis records exist yet."
            )

        else:

            risk_score_col = first_existing_column(
                df,
                [
                    "risk_score",
                    "overall_risk",
                    "risk",
                    "score"
                ]
            )

            risk_level_col = first_existing_column(
                df,
                [
                    "risk_level",
                    "risk_category"
                ]
            )

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

            suspicious_col = first_existing_column(
                df,
                [
                    "suspicious",
                    "is_suspicious",
                    "flagged"
                ]
            )

            user_col = first_existing_column(
                df,
                [
                    "user",
                    "user_id",
                    "userid",
                    "username"
                ]
            )

            text_col = first_existing_column(
                df,
                [
                    "text",
                    "content",
                    "post",
                    "message",
                    "caption"
                ]
            )

            post_id_col = first_existing_column(
                df,
                [
                    "post_id",
                    "id"
                ]
            )

            suspicious_mask = (
                get_live_suspicious_mask(df)
            )

            suspicious_count = int(
                suspicious_mask.sum()
            )

            total_posts = len(df)

            safe_count = max(
                0,
                total_posts - suspicious_count
            )

            if risk_score_col:

                risk_values = safe_numeric(
                    df,
                    risk_score_col
                )

                average_risk = float(
                    risk_values.mean()
                )

                maximum_risk = float(
                    risk_values.max()
                )

            else:

                average_risk = 0
                maximum_risk = 0

            # ------------------------------------------------
            # KPIs
            # ------------------------------------------------

            c1, c2, c3, c4, c5 = st.columns(5)

            with c1:

                metric_card(
                    "LIVE POSTS",
                    f"{total_posts:,}",
                    "Posts analyzed"
                )

            with c2:

                metric_card(
                    "SUSPICIOUS",
                    f"{suspicious_count:,}",
                    "Posts requiring attention"
                )

            with c3:

                metric_card(
                    "SAFE",
                    f"{safe_count:,}",
                    "No major threat detected"
                )

            with c4:

                metric_card(
                    "AVERAGE RISK",
                    f"{average_risk:.2f}",
                    "Mean TrustLens risk"
                )

            with c5:

                metric_card(
                    "MAX RISK",
                    f"{maximum_risk:.2f}",
                    "Highest detected risk"
                )

            st.markdown(
                "<br>",
                unsafe_allow_html=True
            )

            # ------------------------------------------------
            # RISK LEVEL
            # ------------------------------------------------

            section_header(
                "Live Risk Distribution",
                "Current risk levels across posts received from the social platform."
            )

            if risk_level_col:

                risk_counts = (
                    df[risk_level_col]
                    .astype(str)
                    .str.upper()
                    .value_counts()
                    .reset_index()
                )

                risk_counts.columns = [
                    "Risk Level",
                    "Posts"
                ]

            elif risk_score_col:

                risk_counts = pd.DataFrame(
                    {
                        "Risk Level": [
                            infer_risk_level(x)
                            for x in risk_values
                        ]
                    }
                )

                risk_counts = (
                    risk_counts
                    ["Risk Level"]
                    .value_counts()
                    .reset_index()
                )

                risk_counts.columns = [
                    "Risk Level",
                    "Posts"
                ]

            else:

                risk_counts = None

            if risk_counts is not None:

                fig = px.bar(
                    risk_counts,
                    x="Risk Level",
                    y="Posts",
                    text="Posts",
                    template="plotly_dark"
                )

                fig.update_traces(
                    textposition="outside"
                )

                make_chart_layout(
                    fig,
                    420
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            # ------------------------------------------------
            # SCORE DISTRIBUTION
            # ------------------------------------------------

            if risk_score_col:

                section_header(
                    "Risk Score Distribution",
                    "Distribution of TrustLens risk scores across live posts."
                )

                chart_df = pd.DataFrame(
                    {
                        "Risk Score":
                            risk_values
                    }
                )

                fig = px.histogram(
                    chart_df,
                    x="Risk Score",
                    nbins=20,
                    template="plotly_dark"
                )

                make_chart_layout(
                    fig,
                    420
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            # ------------------------------------------------
            # SIGNAL ANALYSIS
            # ------------------------------------------------

            if spam_col or duplicate_col:

                section_header(
                    "Detection Signals",
                    "Signals generated by the TrustLens content-analysis engine."
                )

                signal_frames = []

                if spam_col:

                    signal_frames.append(
                        pd.DataFrame(
                            {
                                "Signal": "Spam Score",
                                "Value":
                                    safe_numeric(
                                        df,
                                        spam_col
                                    )
                            }
                        )
                    )

                if duplicate_col:

                    signal_frames.append(
                        pd.DataFrame(
                            {
                                "Signal":
                                    "Duplicate Score",
                                "Value":
                                    safe_numeric(
                                        df,
                                        duplicate_col
                                    )
                            }
                        )
                    )

                signal_df = pd.concat(
                    signal_frames,
                    ignore_index=True
                )

                fig = px.box(
                    signal_df,
                    x="Signal",
                    y="Value",
                    template="plotly_dark"
                )

                make_chart_layout(
                    fig,
                    420
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            # ------------------------------------------------
            # RECENT RESULTS
            # ------------------------------------------------

            section_header(
                "Recent TrustLens Results",
                "Latest posts analyzed by the TrustLens detection engine."
            )

            display_columns = []

            for column in [
                post_id_col,
                user_col,
                text_col,
                spam_col,
                duplicate_col,
                risk_score_col,
                risk_level_col,
                suspicious_col
            ]:

                if (
                    column
                    and column in df.columns
                    and column not in display_columns
                ):

                    display_columns.append(
                        column
                    )

            recent = df.iloc[::-1].head(100)

            if display_columns:

                display_dataframe(
                    recent[
                        display_columns
                    ],
                    600
                )

            else:

                display_dataframe(
                    recent,
                    600
                )

            # ------------------------------------------------
            # SUSPICIOUS
            # ------------------------------------------------

            if suspicious_count:

                section_header(
                    "⚠️ Suspicious Posts",
                    "Posts flagged by the TrustLens detection engine."
                )

                display_dataframe(
                    df.loc[
                        suspicious_mask
                    ].iloc[::-1].head(100),
                    550
                )

            else:

                render_html(
                    """
                    <div class="success-box">
                        ✅ No suspicious live posts detected.
                    </div>
                    """
                )

            # ------------------------------------------------
            # POST CARDS
            # ------------------------------------------------

            section_header(
                "Post-Level TrustLens Analysis",
                "Detailed analysis of individual posts."
            )

            for _, row in (
                df.iloc[::-1]
                .head(20)
                .iterrows()
            ):

                user_value = (
                    row[user_col]
                    if user_col
                    else "Unknown User"
                )

                text_value = (
                    row[text_col]
                    if text_col
                    else "No post text available"
                )

                spam_value = (
                    row[spam_col]
                    if spam_col
                    else 0
                )

                duplicate_value = (
                    row[duplicate_col]
                    if duplicate_col
                    else 0
                )

                risk_value = (
                    row[risk_score_col]
                    if risk_score_col
                    else 0
                )

                if risk_level_col:

                    level_value = (
                        row[risk_level_col]
                    )

                else:

                    level_value = infer_risk_level(
                        risk_value
                    )

                row_suspicious = bool(
                    suspicious_mask.loc[
                        row.name
                    ]
                )

                badge = get_risk_badge_html(
                    level_value,
                    row_suspicious
                )

                render_html(
                    f"""
                    <div class="live-post-card">

                        <div class="live-post-user">
                            👤 {safe_html(user_value)}
                        </div>

                        <div class="live-post-text">
                            {safe_html(text_value)}
                        </div>

                        <div style="
                            margin-bottom:15px;
                        ">
                            {badge}
                        </div>

                        <div style="
                            display:grid;
                            grid-template-columns:
                            repeat(4,1fr);
                            gap:12px;
                        ">

                            <div class="info-card">
                                <div class="info-title">
                                    Spam Score
                                </div>
                                <div class="info-text">
                                    {safe_html(spam_value)}
                                </div>
                            </div>

                            <div class="info-card">
                                <div class="info-title">
                                    Duplicate Score
                                </div>
                                <div class="info-text">
                                    {safe_html(duplicate_value)}
                                </div>
                            </div>

                            <div class="info-card">
                                <div class="info-title">
                                    Risk Score
                                </div>
                                <div class="info-text">
                                    {safe_html(risk_value)}
                                </div>
                            </div>

                            <div class="info-card">
                                <div class="info-title">
                                    Risk Level
                                </div>
                                <div class="info-text">
                                    {safe_html(level_value)}
                                </div>
                            </div>

                        </div>

                    </div>
                    """
                )


# ============================================================
# RISK INTELLIGENCE
# ============================================================

elif page == "Risk Intelligence":

    section_header(
        "Risk Intelligence",
        "Combined threat scoring across multiple manipulation signals."
    )

    if scores is None:

        st.error(
            "trustlens_scores.csv could not be found."
        )

    else:

        risk_score_col = get_risk_score_column(
            scores
        )

        risk_values = safe_numeric(
            scores,
            risk_score_col
        )

        c1, c2, c3 = st.columns(3)

        with c1:

            metric_card(
                "AVERAGE RISK",
                f"{risk_values.mean():.2f}",
                "Mean platform risk"
            )

        with c2:

            metric_card(
                "MAX RISK",
                f"{risk_values.max():.2f}",
                "Highest detected risk"
            )

        with c3:

            metric_card(
                "ACCOUNTS",
                f"{len(scores):,}",
                "Total analyzed"
            )

        if risk_score_col:

            chart_df = pd.DataFrame(
                {
                    "Risk Score":
                        risk_values
                }
            )

            fig = px.histogram(
                chart_df,
                x="Risk Score",
                nbins=25,
                template="plotly_dark"
            )

            make_chart_layout(
                fig,
                430
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            st.markdown(
                "### Risk Table"
            )

            display_cols = [
                col
                for col in [
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

            table = (
                scores
                .assign(
                    _sort=risk_values
                )
                .sort_values(
                    "_sort",
                    ascending=False
                )
                .drop(
                    columns="_sort"
                )
            )

            if display_cols:

                display_dataframe(
                    table[
                        display_cols
                    ].head(50),
                    550
                )

            else:

                display_dataframe(
                    table.head(50),
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

    df = (
        scores
        if scores is not None
        else users_scored
    )

    if df is None:

        st.error(
            "Account scoring data is unavailable."
        )

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

            bot_values = safe_numeric(
                df,
                bot_col
            )

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

            fig = px.histogram(
                pd.DataFrame(
                    {
                        "Bot Score":
                            bot_values
                    }
                ),
                x="Bot Score",
                nbins=20,
                template="plotly_dark"
            )

            make_chart_layout(
                fig,
                400
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            display_dataframe(
                df.assign(
                    _bot_sort=bot_values
                )
                .sort_values(
                    "_bot_sort",
                    ascending=False
                )
                .drop(
                    columns="_bot_sort"
                )
                .head(50),
                550
            )

        else:

            st.warning(
                "No bot-score column was found in the available account dataset."
            )

            display_dataframe(
                df.head(50),
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

    df = (
        comments_scored
        if comments_scored is not None
        else comments
    )

    if df is None:

        st.error(
            "Comment data is unavailable."
        )

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
                f"{safe_numeric(df, spam_col).mean():.2f}",
                "Average spam score"
            )

        with c3:

            metric_card(
                "DUPLICATE SIGNAL",
                f"{safe_numeric(df, duplicate_col).mean():.2f}",
                "Average duplicate score"
            )

        if spam_col and duplicate_col:

            plot_df = pd.DataFrame(
                {
                    "Spam Score":
                        safe_numeric(
                            df,
                            spam_col
                        ),
                    "Duplicate Score":
                        safe_numeric(
                            df,
                            duplicate_col
                        )
                }
            )

            fig = px.scatter(
                plot_df,
                x="Spam Score",
                y="Duplicate Score",
                template="plotly_dark"
            )

            make_chart_layout(
                fig,
                450
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

        st.error(
            "rating_analysis.csv could not be found."
        )

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

        attack_values = safe_numeric(
            df,
            attack_col
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
                f"{attack_values.mean():.2f}",
                "Average manipulation signal"
            )

        with c3:

            metric_card(
                "HIGH ATTACK SIGNAL",
                f"{(attack_values >= 70).sum():,}",
                "Score ≥ 70"
            )

        if attack_col:

            fig = px.histogram(
                pd.DataFrame(
                    {
                        "Attack Score":
                            attack_values
                    }
                ),
                x="Attack Score",
                nbins=20,
                template="plotly_dark"
            )

            make_chart_layout(
                fig,
                400
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            display_dataframe(
                df.assign(
                    _attack_sort=attack_values
                )
                .sort_values(
                    "_attack_sort",
                    ascending=False
                )
                .drop(
                    columns="_attack_sort"
                )
                .head(100),
                550
            )

        else:

            display_dataframe(
                df.head(100),
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

        if (
            scores is not None
            and "coordination_score"
            in scores.columns
        ):

            st.info(
                "Showing coordination scores from the TrustLens scoring dataset."
            )

            coord_df = (
                scores[
                    [
                        c
                        for c in [
                            "user_id",
                            "coordination_score",
                            "risk_score",
                            "risk_level"
                        ]
                        if c in scores.columns
                    ]
                ]
                .sort_values(
                    "coordination_score",
                    ascending=False
                )
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

        rank_values = safe_numeric(
            df,
            rank_change_col
        )

        score_values = safe_numeric(
            df,
            score_change_col
        )

        c1, c2, c3 = st.columns(3)

        with c1:

            metric_card(
                "ITEMS ANALYZED",
                f"{len(df):,}",
                "Recommendation candidates"
            )

        with c2:

            metric_card(
                "LARGEST RANK SHIFT",
                f"{rank_values.abs().max():.0f}",
                "Absolute rank change"
            )

        with c3:

            metric_card(
                "MAX SCORE CHANGE",
                f"{score_values.abs().max():.3f}",
                "Recommendation score"
            )

        if rank_change_col:

            plot_df = df.copy()

            plot_df[
                rank_change_col
            ] = rank_values

            if score_change_col:

                plot_df[
                    score_change_col
                ] = score_values

            else:

                plot_df[
                    "_score"
                ] = rank_values

                score_change_col = "_score"

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
                y=score_change_col,
                color="Direction",
                template="plotly_dark"
            )

            make_chart_layout(
                fig,
                450
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            largest = (
                df.assign(
                    _abs_change=
                        rank_values.abs()
                )
                .sort_values(
                    "_abs_change",
                    ascending=False
                )
                .drop(
                    columns="_abs_change"
                )
                .head(30)
            )

            st.markdown(
                "### Largest Recommendation Changes"
            )

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

        render_html(
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
            """
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

            degree_values = safe_numeric(
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
                    f"{degree_values.mean():.2f}",
                    "Mean connections"
                )

            with c3:

                metric_card(
                    "MAX CONNECTIVITY",
                    f"{degree_values.max():.0f}",
                    "Highest connectivity"
                )

            user_col = get_user_column(
                df
            )

            if user_col:

                top = (
                    df.assign(
                        _degree=degree_values
                    )
                    .sort_values(
                        "_degree",
                        ascending=False
                    )
                    .head(25)
                )

                fig = px.bar(
                    top,
                    x="_degree",
                    y=user_col,
                    orientation="h",
                    template="plotly_dark"
                )

                fig.update_yaxes(
                    categoryorder="total ascending"
                )

                make_chart_layout(
                    fig,
                    600
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
# CONTROLLED ATTACK LAB
# ============================================================

elif page == "Controlled Attack Lab":

    section_header(
        "Controlled Attack Lab",
        "Create synthetic bot, comment and rating attacks and test the TrustLens detection pipeline."
    )

    render_html(
        """
        <div class="attack-card">

            <div class="attack-card-title">
                ⚔️ Controlled Security Testing
            </div>

            <div class="attack-card-text">

                Configure an attack, generate synthetic records
                inside the local TrustLens dataset, then send
                the generated data through the existing detection
                scripts.

                Nothing is posted to a real platform.

            </div>

        </div>
        """
    )

    tab_bot, tab_comment, tab_rating = st.tabs(
        [
            "🤖 Bot Attack",
            "💬 Comment Attack",
            "⭐ Rating Attack"
        ]
    )

    # ========================================================
    # BOT ATTACK
    # ========================================================

    with tab_bot:

        st.markdown(
            "### Bot Injection"
        )

        bot_count = st.slider(
            "Number of synthetic bots",
            1,
            200,
            20,
            key="bot_count"
        )

        bot_activity = st.slider(
            "Bot activity intensity",
            1,
            10,
            7,
            key="bot_activity"
        )

        bot_mode = st.selectbox(
            "Bot behavior",
            [
                "Coordinated cluster",
                "High-frequency activity",
                "Mixed suspicious behavior"
            ],
            key="bot_mode"
        )

        run_detector = st.checkbox(
            "Run existing bot detector",
            True,
            key="run_bot_detector"
        )

        if st.button(
            "🚨 Simulate Bot Attack",
            use_container_width=True
        ):

            if users is None:

                st.error(
                    "users.csv was not found."
                )

            else:

                base = users.copy()

                user_col = first_existing_column(
                    base,
                    [
                        "user_id",
                        "userid",
                        "user"
                    ]
                )

                if user_col is None:

                    st.error(
                        "Could not find user_id column."
                    )

                else:

                    rows = []

                    for i in range(
                        1,
                        bot_count + 1
                    ):

                        row = {
                            col: ""
                            for col in base.columns
                        }

                        row[user_col] = (
                            f"BOT_{i:03d}"
                        )

                        for col in base.columns:

                            low = col.lower()

                            if "bot" in low:
                                row[col] = 1

                            elif "activity" in low:
                                row[col] = bot_activity

                            elif "real" in low:
                                row[col] = False

                        rows.append(row)

                    injected = pd.DataFrame(
                        rows,
                        columns=base.columns
                    )

                    result_df = pd.concat(
                        [
                            base,
                            injected
                        ],
                        ignore_index=True
                    )

                    result_df.to_csv(
                        ATTACK_DATA_DIR /
                        "users_attacked.csv",
                        index=False
                    )

                    injected.to_csv(
                        ATTACK_DATA_DIR /
                        "injected_bots.csv",
                        index=False
                    )

                    manifest = pd.DataFrame(
                        [
                            {
                                "attack_id":
                                    datetime.now()
                                    .strftime(
                                        "%Y%m%d_%H%M%S"
                                    ),
                                "attack_type":
                                    "BOT",
                                "bot_count":
                                    bot_count,
                                "activity_intensity":
                                    bot_activity,
                                "behavior":
                                    bot_mode,
                                "created_at":
                                    datetime.now()
                                    .isoformat()
                            }
                        ]
                    )

                    manifest_path = (
                        ATTACK_DATA_DIR /
                        "attack_manifest.csv"
                    )

                    manifest.to_csv(
                        manifest_path,
                        mode="a",
                        header=not manifest_path.exists(),
                        index=False
                    )

                    st.success(
                        f"Created {bot_count} synthetic bots."
                    )

                    c1, c2, c3 = st.columns(3)

                    with c1:
                        metric_card(
                            "ORIGINAL USERS",
                            f"{len(base):,}",
                            "Before attack"
                        )

                    with c2:
                        metric_card(
                            "BOTS INJECTED",
                            f"{bot_count:,}",
                            "Synthetic accounts"
                        )

                    with c3:
                        metric_card(
                            "FINAL USERS",
                            f"{len(result_df):,}",
                            "After attack"
                        )

                    display_dataframe(
                        injected.head(50),
                        350
                    )

                    if run_detector:

                        detector = (
                            BASE_DIR /
                            "src" /
                            "detect_bot_attack.py"
                        )

                        if detector.exists():

                            run_detector_process(
                                detector,
                                "Bot detector"
                            )

                        else:

                            st.info(
                                "Bot detector script was not found."
                            )


    # ========================================================
    # COMMENT ATTACK
    # ========================================================

    with tab_comment:

        st.markdown(
            "### Fake Comment Injection"
        )

        comment_count = st.slider(
            "Number of fake comments",
            1,
            500,
            100,
            key="comment_count"
        )

        comment_style = st.selectbox(
            "Comment attack type",
            [
                "Exact duplicate",
                "Near duplicate",
                "Spam",
                "Mixed attack"
            ],
            key="comment_style"
        )

        comment_text = st.text_input(
            "Attack comment",
            "Amazing product! Highly recommended!",
            key="comment_text"
        )

        target_count = st.slider(
            "Number of target items",
            1,
            50,
            10,
            key="target_count"
        )

        run_detector = st.checkbox(
            "Run existing comment detector",
            True,
            key="run_comment_detector"
        )

        if st.button(
            "🚨 Simulate Comment Attack",
            use_container_width=True
        ):

            if comments is None:

                st.error(
                    "comments.csv was not found."
                )

            else:

                base = comments.copy()

                user_col = first_existing_column(
                    base,
                    [
                        "user_id",
                        "userid",
                        "user"
                    ]
                )

                item_col = first_existing_column(
                    base,
                    [
                        "item_id",
                        "item",
                        "product_id"
                    ]
                )

                text_col = first_existing_column(
                    base,
                    [
                        "text",
                        "comment",
                        "content",
                        "body"
                    ]
                )

                id_col = first_existing_column(
                    base,
                    [
                        "comment_id",
                        "id"
                    ]
                )

                if text_col is None:

                    st.error(
                        "Comment text column could not be identified."
                    )

                else:

                    if item_col:

                        targets = (
                            base[item_col]
                            .dropna()
                            .astype(str)
                            .drop_duplicates()
                            .head(target_count)
                            .tolist()
                        )

                    else:

                        targets = ["I001"]

                    if not targets:
                        targets = ["I001"]

                    rows = []

                    for i in range(
                        comment_count
                    ):

                        row = {
                            col: ""
                            for col in base.columns
                        }

                        if id_col:
                            row[id_col] = (
                                f"ATTACK_C{i}"
                            )

                        if user_col:
                            row[user_col] = (
                                f"CBOT_{(i % 20) + 1:03d}"
                            )

                        if item_col:
                            row[item_col] = (
                                targets[
                                    i % len(targets)
                                ]
                            )

                        if comment_style == "Exact duplicate":

                            text = comment_text

                        elif comment_style == "Near duplicate":

                            variants = [
                                comment_text,
                                comment_text.replace(
                                    "!",
                                    "!!"
                                ),
                                comment_text.replace(
                                    "!",
                                    ""
                                ),
                                comment_text.replace(
                                    "!",
                                    ","
                                ),
                                comment_text.replace(
                                    "Highly",
                                    "highly"
                                )
                            ]

                            text = variants[
                                i % len(variants)
                            ]

                        elif comment_style == "Spam":

                            variants = [
                                "click here for amazing deals",
                                "buy now amazing offer",
                                "best deal available now",
                                "limited offer click here",
                                "amazing product buy now"
                            ]

                            text = variants[
                                i % len(variants)
                            ]

                        else:

                            variants = [
                                comment_text,
                                comment_text.replace(
                                    "!",
                                    "!!"
                                ),
                                "amazing product buy now",
                                "click here for amazing deals",
                                comment_text.replace(
                                    "Highly",
                                    "highly"
                                )
                            ]

                            text = variants[
                                i % len(variants)
                            ]

                        row[text_col] = text

                        rows.append(row)

                    injected = pd.DataFrame(
                        rows,
                        columns=base.columns
                    )

                    result_df = pd.concat(
                        [
                            base,
                            injected
                        ],
                        ignore_index=True
                    )

                    result_df.to_csv(
                        ATTACK_DATA_DIR /
                        "comments_attacked.csv",
                        index=False
                    )

                    injected.to_csv(
                        ATTACK_DATA_DIR /
                        "injected_comments.csv",
                        index=False
                    )

                    st.success(
                        f"Created {comment_count} synthetic comments."
                    )

                    display_dataframe(
                        injected.head(100),
                        400
                    )

                    if run_detector:

                        detector_candidates = [
                            BASE_DIR /
                            "src" /
                            "detect_comment_attack.py",

                            BASE_DIR /
                            "src" /
                            "detect_advanced_comment_attack.py",

                            BASE_DIR /
                            "src" /
                            "detect_coordinated_comment_attack.py"
                        ]

                        detector = next(
                            (
                                p
                                for p in detector_candidates
                                if p.exists()
                            ),
                            None
                        )

                        if detector:

                            run_detector_process(
                                detector,
                                "Comment detector"
                            )

                        else:

                            st.info(
                                "No compatible comment detector was found."
                            )


    # ========================================================
    # RATING ATTACK
    # ========================================================

    with tab_rating:

        st.markdown(
            "### Rating Manipulation Injection"
        )

        rating_count = st.slider(
            "Number of synthetic ratings",
            1,
            300,
            60,
            key="rating_count"
        )

        rating_value = st.selectbox(
            "Injected rating",
            [5, 1],
            key="rating_value"
        )

        target_item = st.text_input(
            "Target item ID",
            "I100",
            key="target_item"
        )

        run_detector = st.checkbox(
            "Run existing rating detector",
            True,
            key="run_rating_detector"
        )

        if st.button(
            "🚨 Simulate Rating Attack",
            use_container_width=True
        ):

            if ratings is None:

                st.error(
                    "ratings.csv was not found."
                )

            else:

                base = ratings.copy()

                user_col = first_existing_column(
                    base,
                    [
                        "user_id",
                        "userid",
                        "user"
                    ]
                )

                item_col = first_existing_column(
                    base,
                    [
                        "item_id",
                        "item",
                        "product_id"
                    ]
                )

                rating_col = first_existing_column(
                    base,
                    [
                        "rating",
                        "score",
                        "stars"
                    ]
                )

                id_col = first_existing_column(
                    base,
                    [
                        "rating_id",
                        "id"
                    ]
                )

                if rating_col is None:

                    st.error(
                        "Rating column could not be identified."
                    )

                else:

                    rows = []

                    for i in range(
                        rating_count
                    ):

                        row = {
                            col: ""
                            for col in base.columns
                        }

                        if id_col:
                            row[id_col] = (
                                f"ATTACK_R{i}"
                            )

                        if user_col:
                            row[user_col] = (
                                f"BOT_{(i % 20) + 1:03d}"
                            )

                        if item_col:
                            row[item_col] = target_item

                        row[rating_col] = rating_value

                        rows.append(row)

                    injected = pd.DataFrame(
                        rows,
                        columns=base.columns
                    )

                    result_df = pd.concat(
                        [
                            base,
                            injected
                        ],
                        ignore_index=True
                    )

                    result_df.to_csv(
                        ATTACK_DATA_DIR /
                        "ratings_attacked.csv",
                        index=False
                    )

                    injected.to_csv(
                        ATTACK_DATA_DIR /
                        "injected_ratings.csv",
                        index=False
                    )

                    st.success(
                        f"Created {rating_count} synthetic ratings."
                    )

                    display_dataframe(
                        injected.head(100),
                        400
                    )

                    if run_detector:

                        detector_candidates = [
                            BASE_DIR /
                            "src" /
                            "detect_rating_attack.py",

                            BASE_DIR /
                            "src" /
                            "detect_rating_attacks.py"
                        ]

                        detector = next(
                            (
                                p
                                for p in detector_candidates
                                if p.exists()
                            ),
                            None
                        )

                        if detector:

                            run_detector_process(
                                detector,
                                "Rating detector"
                            )

                        else:

                            st.info(
                                "No compatible rating detector was found."
                            )

    # ========================================================
    # GENERATED FILES
    # ========================================================

    st.markdown("---")

    st.markdown(
        "### Generated Attack Files"
    )

    files = sorted(
        ATTACK_DATA_DIR.glob("*.csv"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )

    if files:

        rows = []

        for path in files:

            rows.append(
                {
                    "File": path.name,
                    "Size (KB)":
                        round(
                            path.stat().st_size / 1024,
                            2
                        ),
                    "Modified":
                        datetime.fromtimestamp(
                            path.stat().st_mtime
                        ).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                }
            )

        display_dataframe(
            pd.DataFrame(rows),
            300
        )

    else:

        st.info(
            "No controlled attack files have been generated yet."
        )


# ============================================================
# DATA EXPLORER
# ============================================================

elif page == "Data Explorer":

    section_header(
        "Data Explorer",
        "Inspect and filter the underlying TrustLens datasets."
    )

    datasets = {
        "TrustLens Scores":
            scores,

        "Users":
            users,

        "Users Scored":
            users_scored,

        "Comments":
            comments,

        "Comments Scored":
            comments_scored,

        "Ratings":
            ratings,

        "Rating Analysis":
            rating_analysis,

        "Items":
            items,

        "Interactions":
            interactions,

        "Coordination Events":
            coordination,

        "Graph Features":
            graph_features,

        "Recommendation Impact":
            recommendation_impact,

        "Recommendation Ranking":
            recommendation_ranking,

        "Live Posts":
            live_posts,

        "Live Analysis":
            live_analysis,

        "Live Users":
            live_users
    }

    available = [
        name
        for name, dataframe
        in datasets.items()
        if dataframe is not None
    ]

    if not available:

        st.error(
            "No TrustLens datasets were found."
        )

    else:

        selected_dataset = st.selectbox(
            "Select dataset",
            available
        )

        selected_df = datasets[
            selected_dataset
        ].copy()

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

        # ----------------------------------------------------
        # SEARCH
        # ----------------------------------------------------

        search = st.text_input(
            "🔎 Search dataset",
            placeholder="Search across all columns..."
        )

        if search:

            mask = pd.Series(
                False,
                index=selected_df.index
            )

            for column in selected_df.columns:

                mask |= (
                    selected_df[column]
                    .astype(str)
                    .str.contains(
                        search,
                        case=False,
                        na=False,
                        regex=False
                    )
                )

            filtered_df = selected_df[
                mask
            ]

        else:

            filtered_df = selected_df

        st.caption(
            f"Showing {len(filtered_df):,} matching records."
        )

        display_dataframe(
            filtered_df.head(500),
            650
        )


# ============================================================
# FOOTER
# ============================================================

render_html(
    """
    <div class="footer">

        🛡️ TRUSTLENS &nbsp;•&nbsp;
        AI-Powered Social Media Authenticity & Security Analysis

        <br><br>

        Behavioral Detection • Coordination Analysis •
        Rating Security • Recommendation Integrity

    </div>
    """
)