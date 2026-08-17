import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from textwrap import dedent
from datetime import datetime
import random
import re
import time


# ============================================================
# TRUSTLENS CONFIGURATION
# ============================================================

RENDER_API = "https://trustlens-9idp.onrender.com"

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
LIVE_DATA_DIR = DATA_DIR / "live"
ATTACK_DATA_DIR = DATA_DIR / "attacks"
ATTACK_RESULTS_DIR = DATA_DIR / "attack_results"


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
            rgba(40, 110, 255, 0.12),
            transparent 28%
        ),
        radial-gradient(
            circle at 90% 10%,
            rgba(130, 70, 255, 0.10),
            transparent 28%
        ),
        linear-gradient(
            180deg,
            #070b14 0%,
            #0a101d 100%
        );

    color: #f5f7fb;
}

/* ============================================================
   SIDEBAR
   ============================================================ */

section[data-testid="stSidebar"] {
    background:
        linear-gradient(
            180deg,
            #0b1220 0%,
            #080d17 100%
        );

    border-right:
        1px solid rgba(255,255,255,0.07);
}

section[data-testid="stSidebar"] * {
    color: #dce5f7;
}

section[data-testid="stSidebar"] .stRadio label {
    padding: 8px 4px;
}

/* ============================================================
   MAIN CONTAINER
   ============================================================ */

.block-container {
    padding-top: 2rem;
    padding-bottom: 4rem;
    max-width: 1500px;
}

/* ============================================================
   HERO
   ============================================================ */

.hero {
    position: relative;

    background:
        linear-gradient(
            135deg,
            rgba(20, 34, 62, 0.98),
            rgba(10, 17, 31, 0.98)
        );

    border:
        1px solid rgba(100, 150, 255, 0.20);

    border-radius: 26px;

    padding: 42px;

    margin-bottom: 28px;

    overflow: hidden;

    box-shadow:
        0 25px 70px rgba(0,0,0,0.35);
}

.hero:after {
    content: "";

    position: absolute;

    width: 260px;
    height: 260px;

    right: -80px;
    top: -100px;

    background:
        radial-gradient(
            circle,
            rgba(75,130,255,0.20),
            transparent 70%
        );
}

.hero-title {
    font-size: 46px;
    font-weight: 800;
    letter-spacing: -1.5px;
    margin-bottom: 8px;
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
    line-height: 1.7;
    max-width: 850px;
}

.status {
    display: inline-flex;
    align-items: center;
    gap: 9px;

    margin-top: 22px;

    padding: 9px 16px;

    border-radius: 999px;

    background:
        rgba(50,220,145,0.09);

    border:
        1px solid rgba(50,220,145,0.25);

    color: #74f0b6;

    font-size: 12px;
    font-weight: 800;

    letter-spacing: 0.5px;
}

/* ============================================================
   SECTION
   ============================================================ */

.section-title {
    font-size: 26px;
    font-weight: 800;

    margin-top: 32px;
    margin-bottom: 4px;
}

.section-subtitle {
    color: #8294b2;

    margin-bottom: 20px;

    font-size: 14px;
}

/* ============================================================
   KPI
   ============================================================ */

.kpi-card {
    background:
        linear-gradient(
            135deg,
            rgba(20,32,55,0.96),
            rgba(11,18,32,0.96)
        );

    border:
        1px solid rgba(255,255,255,0.075);

    border-radius: 18px;

    padding: 22px;

    min-height: 140px;

    box-shadow:
        0 12px 35px rgba(0,0,0,0.20);

    transition:
        transform 0.2s ease,
        border-color 0.2s ease;
}

.kpi-card:hover {
    transform: translateY(-2px);

    border-color:
        rgba(100,150,255,0.25);
}

.kpi-label {
    color: #8295b4;

    font-size: 11px;

    font-weight: 800;

    letter-spacing: 1.2px;
}

.kpi-value {
    font-size: 34px;

    font-weight: 800;

    margin-top: 9px;

    color: #f5f8ff;
}

.kpi-description {
    color: #667995;

    font-size: 12px;

    margin-top: 5px;
}

/* ============================================================
   LIVE CONNECTION
   ============================================================ */

.live-connected {
    padding: 14px 18px;

    border-radius: 14px;

    background:
        rgba(40,210,130,0.08);

    border:
        1px solid rgba(40,210,130,0.25);

    color: #76efb7;

    font-weight: 700;

    font-size: 13px;
}

.live-warning {
    padding: 14px 18px;

    border-radius: 14px;

    background:
        rgba(255,180,60,0.08);

    border:
        1px solid rgba(255,180,60,0.25);

    color: #ffd17b;

    font-weight: 700;

    font-size: 13px;
}

/* ============================================================
   ANALYSIS CARD
   ============================================================ */

.analysis-card {
    background:
        linear-gradient(
            135deg,
            rgba(17,27,47,0.95),
            rgba(10,17,30,0.95)
        );

    border:
        1px solid rgba(255,255,255,0.07);

    border-radius: 20px;

    padding: 24px;

    margin-top: 20px;

    box-shadow:
        0 15px 45px rgba(0,0,0,0.18);
}

.analysis-card h3 {
    margin-top: 0;
}

/* ============================================================
   POST CARD
   ============================================================ */

.post-card {
    background:
        linear-gradient(
            135deg,
            rgba(18,29,49,0.96),
            rgba(10,17,30,0.96)
        );

    border:
        1px solid rgba(255,255,255,0.07);

    border-radius: 20px;

    padding: 22px;

    margin-bottom: 16px;

    box-shadow:
        0 12px 35px rgba(0,0,0,0.18);
}

.post-user {
    font-size: 15px;
    font-weight: 800;
}

.post-text {
    color: #d6deec;

    font-size: 15px;

    line-height: 1.7;

    margin-top: 14px;
}

.post-meta {
    color: #70819d;

    font-size: 12px;
}

/* ============================================================
   BADGES
   ============================================================ */

.badge {
    display: inline-flex;

    padding: 6px 11px;

    border-radius: 999px;

    font-size: 11px;

    font-weight: 800;
}

.badge-safe {
    background:
        rgba(40,210,130,0.10);

    border:
        1px solid rgba(40,210,130,0.25);

    color: #70efb2;
}

.badge-medium {
    background:
        rgba(255,185,60,0.10);

    border:
        1px solid rgba(255,185,60,0.25);

    color: #ffd47d;
}

.badge-high {
    background:
        rgba(255,70,90,0.10);

    border:
        1px solid rgba(255,70,90,0.25);

    color: #ff8998;
}

/* ============================================================
   EMPTY STATE
   ============================================================ */

.empty-state {
    padding: 50px 30px;

    text-align: center;

    background:
        rgba(15,24,42,0.85);

    border:
        1px dashed rgba(255,255,255,0.12);

    border-radius: 20px;

    color: #8294b2;
}

.empty-icon {
    font-size: 42px;
    margin-bottom: 10px;
}

/* ============================================================
   SUCCESS / WARNING
   ============================================================ */

.success-box {
    padding: 16px 20px;

    border-radius: 14px;

    background:
        rgba(40,210,130,0.09);

    border:
        1px solid rgba(40,210,130,0.25);

    color: #7af0ba;
}

.warning-box {
    padding: 16px 20px;

    border-radius: 14px;

    background:
        rgba(255,180,60,0.09);

    border:
        1px solid rgba(255,180,60,0.25);

    color: #ffd17b;
}

/* ============================================================
   FOOTER
   ============================================================ */

.footer {
    margin-top: 60px;

    padding: 30px;

    text-align: center;

    color: #637594;

    border-top:
        1px solid rgba(255,255,255,0.06);

    font-size: 12px;
}

/* ============================================================
   BUTTONS
   ============================================================ */

.stButton > button {
    border-radius: 10px;

    border:
        1px solid rgba(255,255,255,0.10);

    background:
        rgba(30,45,70,0.8);

    color: #eef4ff;

    font-weight: 700;
}

.stButton > button:hover {
    border-color:
        rgba(100,150,255,0.35);
}

/* ============================================================
   DATAFRAME
   ============================================================ */

div[data-testid="stDataFrame"] {
    border-radius: 14px;
    overflow: hidden;
}

/* ============================================================
   MOBILE
   ============================================================ */

@media (max-width: 900px) {

    .hero {
        padding: 28px;
    }

    .hero-title {
        font-size: 34px;
    }

    .hero-subtitle {
        font-size: 15px;
    }

}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# BASIC HELPERS
# ============================================================

def render_html(html):
    st.markdown(
        dedent(html),
        unsafe_allow_html=True
    )


def section_header(title, subtitle=""):
    render_html(
        f"""
        <div class="section-title">
            {title}
        </div>

        <div class="section-subtitle">
            {subtitle}
        </div>
        """
    )


def metric_card(label, value, description=""):
    render_html(
        f"""
        <div class="kpi-card">

            <div class="kpi-label">
                {label}
            </div>

            <div class="kpi-value">
                {value}
            </div>

            <div class="kpi-description">
                {description}
            </div>

        </div>
        """
    )


def display_dataframe(df, height=430):

    if df is None or df.empty:

        st.info(
            "No data available for this section."
        )

        return

    st.dataframe(
        df,
        use_container_width=True,
        height=height,
        hide_index=True
    )


def first_existing_column(df, candidates):

    if df is None:
        return None

    for column in candidates:

        if column in df.columns:
            return column

    return None


def normalize_text(value):

    value = str(value)

    value = value.lower()

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value.strip()


def safe_float(value, default=0.0):

    try:

        if value is None:
            return default

        return float(value)

    except Exception:

        return default


# ============================================================
# DIRECTORIES
# ============================================================

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
# FIND DATA FILE
# ============================================================

def find_data_file(filename):

    possible_paths = [

        BASE_DIR / filename,

        DATA_DIR / filename,

        BASE_DIR / "data" / filename,

        BASE_DIR / "datasets" / filename,

        BASE_DIR / "data" / "processed" / filename

    ]

    for path in possible_paths:

        if path.exists():

            return path

    return None


# ============================================================
# STATIC CSV LOADER
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
# API REQUEST HELPER
# ============================================================

def api_get(endpoint):

    try:

        response = requests.get(
            f"{RENDER_API}{endpoint}",
            timeout=30
        )

        response.raise_for_status()

        return response.json()

    except Exception as error:

        print(
            f"TrustLens API GET {endpoint} failed:",
            error
        )

        return None


# ============================================================
# NORMALIZE API LIST RESPONSE
# ============================================================

def normalize_api_list(data):

    if data is None:
        return []

    if isinstance(data, list):
        return data

    if isinstance(data, dict):

        for key in [
            "posts",
            "analysis",
            "results",
            "users",
            "data"
        ]:

            if key in data:

                value = data[key]

                if isinstance(value, list):
                    return value

                if isinstance(value, dict):
                    return [value]

        return [data]

    return []


# ============================================================
# LOAD LIVE POSTS
#
# IMPORTANT:
# No Streamlit cache here.
#
# This guarantees that the dashboard sees new
# PostgreSQL records immediately after refresh.
# ============================================================

def load_live_posts():

    data = api_get("/posts")

    records = normalize_api_list(data)

    if not records:
        return pd.DataFrame()

    return pd.DataFrame(records)


# ============================================================
# LOAD LIVE USERS
# ============================================================

def load_live_users():

    data = api_get("/users")

    records = normalize_api_list(data)

    if not records:
        return pd.DataFrame()

    return pd.DataFrame(records)


# ============================================================
# LOAD LIVE ANALYSIS
# ============================================================

def load_live_analysis():

    data = api_get("/analysis")

    records = normalize_api_list(data)

    if not records:
        return pd.DataFrame()

    return pd.DataFrame(records)


# ============================================================
# LOAD STATIC TRUSTLENS DATASETS
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

recommendation_impact = load_csv(
    "recommendation_impact.csv"
)

recommendation_ranking = load_csv(
    "recommendation_ranking.csv"
)


# ============================================================
# LIVE DATA
# ============================================================

live_posts = load_live_posts()

live_analysis = load_live_analysis()

live_users = load_live_users()


# ============================================================
# LIVE COLUMN HELPERS
# ============================================================

def get_live_risk_score_column(df):

    return first_existing_column(
        df,
        [
            "risk_score",
            "overall_risk",
            "risk",
            "score"
        ]
    )


def get_live_risk_level_column(df):

    return first_existing_column(
        df,
        [
            "risk_level",
            "risk_category",
            "level"
        ]
    )


def get_live_spam_column(df):

    return first_existing_column(
        df,
        [
            "spam_score",
            "spam_risk"
        ]
    )


def get_live_duplicate_column(df):

    return first_existing_column(
        df,
        [
            "duplicate_score",
            "dup_score",
            "duplicate_risk"
        ]
    )


def get_live_suspicious_column(df):

    return first_existing_column(
        df,
        [
            "suspicious",
            "is_suspicious",
            "flagged"
        ]
    )


def get_live_user_column(df):

    return first_existing_column(
        df,
        [
            "user",
            "user_id",
            "userid",
            "username"
        ]
    )


def get_live_text_column(df):

    return first_existing_column(
        df,
        [
            "text",
            "content",
            "post",
            "message"
        ]
    )


def get_live_post_id_column(df):

    return first_existing_column(
        df,
        [
            "post_id",
            "id"
        ]
    )


# ============================================================
# SUSPICIOUS MASK
# ============================================================

def get_live_suspicious_mask(df):

    if df is None or df.empty:

        return pd.Series(
            False,
            index=df.index if df is not None else []
        )

    suspicious_col = (
        get_live_suspicious_column(df)
    )

    if suspicious_col:

        values = (
            df[suspicious_col]
            .astype(str)
            .str.lower()
            .str.strip()
        )

        return values.isin(
            [
                "true",
                "1",
                "yes",
                "suspicious",
                "high"
            ]
        )

    risk_col = (
        get_live_risk_score_column(df)
    )

    if risk_col:

        scores = pd.to_numeric(
            df[risk_col],
            errors="coerce"
        ).fillna(0)

        return scores >= 40

    return pd.Series(
        False,
        index=df.index
    )


# ============================================================
# STATIC RISK HELPERS
# ============================================================

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


# ============================================================
# RISK BADGE
# ============================================================

def render_risk_badge(
    risk_level=None,
    suspicious=False,
    risk_score=0
):

    level = str(
        risk_level or ""
    ).upper()

    score = safe_float(
        risk_score
    )

    if (
        suspicious
        or level == "HIGH"
        or score >= 70
    ):

        return (
            '<span class="badge badge-high">'
            '⚠️ HIGH RISK'
            '</span>'
        )

    if (
        level == "MEDIUM"
        or score >= 40
    ):

        return (
            '<span class="badge badge-medium">'
            '⚠️ MEDIUM RISK'
            '</span>'
        )

    return (
        '<span class="badge badge-safe">'
        '✓ SAFE'
        '</span>'
    )


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown(
    """
    # 🛡️ TrustLens

    **AI-Powered Social Media
    Authenticity & Security**

    ---
    """
)

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Live Social Analysis",
        "Attack Simulation",
        "Data Explorer"
    ]
)

st.sidebar.markdown("---")

st.sidebar.markdown(
    """
    **System**

    🟢 API Connected

    PostgreSQL-backed live analysis

    `trustlens-9idp.onrender.com`
    """
)


# ============================================================
# DASHBOARD
# ============================================================

if page == "Dashboard":

    render_html(
        """
        <div class="hero">

            <div class="hero-title">
                🛡️ <span>TrustLens</span>
            </div>

            <div class="hero-subtitle">

                AI-powered social media authenticity,
                bias and recommendation security analyzer.

                Detect suspicious content, coordinated behavior,
                manipulation and abnormal engagement patterns.

            </div>

            <div class="status">
                ● TRUSTLENS ENGINE ONLINE
            </div>

        </div>
        """
    )

    total_users = (
        len(users)
        if users is not None
        else 0
    )

    high_risk = 0
    medium_risk = 0

    if scores is not None:

        risk_col = get_risk_column(scores)

        if risk_col:

            risk_values = (
                scores[risk_col]
                .astype(str)
                .str.upper()
            )

            high_risk = int(
                risk_values.eq("HIGH").sum()
            )

            medium_risk = int(
                risk_values.eq("MEDIUM").sum()
            )

    rating_attacks = (
        len(rating_analysis)
        if rating_analysis is not None
        else 0
    )

    recommendation_changes = (
        len(recommendation_impact)
        if recommendation_impact is not None
        else 0
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

            fig.update_layout(
                height=420,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    section_header(
        "Most Suspicious Accounts",
        "Accounts with the highest combined threat scores."
    )

    if scores is not None:

        risk_score_col = (
            get_risk_score_column(scores)
        )

        if risk_score_col:

            top = (
                scores
                .sort_values(
                    risk_score_col,
                    ascending=False
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
        "Real-time analysis of posts submitted through your social-media platform."
    )

    # --------------------------------------------------------
    # CONTROLS
    # --------------------------------------------------------

    col_refresh, col_auto, col_status = st.columns(
        [1.4, 1.4, 4]
    )

    with col_refresh:

        refresh_clicked = st.button(
            "🔄 Refresh Now",
            use_container_width=True
        )

    with col_auto:

        auto_refresh = st.checkbox(
            "Auto Refresh",
            value=False
        )

    if refresh_clicked:

        st.rerun()

    if auto_refresh:

        time.sleep(2)
        st.rerun()

    # --------------------------------------------------------
    # API STATUS
    # --------------------------------------------------------

    with col_status:

        test_data = api_get("/analysis")

        if test_data is not None:

            render_html(
                """
                <div class="live-connected">
                    🟢 LIVE TRUSTLENS API CONNECTED
                    &nbsp; • &nbsp;
                    PostgreSQL data available
                </div>
                """
            )

        else:

            render_html(
                """
                <div class="live-warning">
                    🟡 TrustLens API is currently unavailable.
                </div>
                """
            )

    # --------------------------------------------------------
    # RELOAD LIVE DATA
    # --------------------------------------------------------

    live_posts = load_live_posts()

    live_analysis = load_live_analysis()

    live_users = load_live_users()

    # --------------------------------------------------------
    # NO DATA
    # --------------------------------------------------------

    if live_analysis.empty:

        render_html(
            """
            <div class="empty-state">

                <div class="empty-icon">
                    🛡️
                </div>

                <h2>
                    Waiting for TrustLens analysis
                </h2>

                <p>
                    Create a post on your React social-media
                    application and refresh this dashboard.
                </p>

                <p>
                    React → Render FastAPI → PostgreSQL
                    → TrustLens Dashboard
                </p>

            </div>
            """
        )

    else:

        df = live_analysis.copy()

        df.columns = [
            str(column).strip()
            for column in df.columns
        ]

        # ----------------------------------------------------
        # COLUMN DETECTION
        # ----------------------------------------------------

        risk_score_col = (
            get_live_risk_score_column(df)
        )

        risk_level_col = (
            get_live_risk_level_column(df)
        )

        spam_col = (
            get_live_spam_column(df)
        )

        duplicate_col = (
            get_live_duplicate_column(df)
        )

        suspicious_col = (
            get_live_suspicious_column(df)
        )

        user_col = (
            get_live_user_column(df)
        )

        text_col = (
            get_live_text_column(df)
        )

        post_id_col = (
            get_live_post_id_column(df)
        )

        # ----------------------------------------------------
        # SUSPICIOUS
        # ----------------------------------------------------

        suspicious_mask = (
            get_live_suspicious_mask(df)
        )

        suspicious_posts = int(
            suspicious_mask.sum()
        )

        total_posts = len(df)

        safe_posts = (
            total_posts
            - suspicious_posts
        )

        # ----------------------------------------------------
        # RISK
        # ----------------------------------------------------

        if risk_score_col:

            risk_values = pd.to_numeric(
                df[risk_score_col],
                errors="coerce"
            ).fillna(0)

            average_risk = float(
                risk_values.mean()
            )

            maximum_risk = float(
                risk_values.max()
            )

        else:

            average_risk = 0

            maximum_risk = 0

        # ----------------------------------------------------
        # KPI
        # ----------------------------------------------------

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
                f"{suspicious_posts:,}",
                "Requires attention"
            )

        with c3:

            metric_card(
                "SAFE",
                f"{safe_posts:,}",
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

        # ----------------------------------------------------
        # RISK LEVEL
        # ----------------------------------------------------

        section_header(
            "Live Risk Distribution",
            "Current risk levels across posts."
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

            fig = px.bar(
                risk_counts,
                x="Risk Level",
                y="Posts",
                text="Posts",
                template="plotly_dark",
                title="Post Risk Levels"
            )

            fig.update_traces(
                textposition="outside"
            )

            fig.update_layout(
                height=420,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        # ----------------------------------------------------
        # RISK SCORE DISTRIBUTION
        # ----------------------------------------------------

        if risk_score_col:

            section_header(
                "Risk Score Distribution",
                "Distribution of TrustLens risk scores."
            )

            chart_df = df.copy()

            chart_df[risk_score_col] = pd.to_numeric(
                chart_df[risk_score_col],
                errors="coerce"
            ).fillna(0)

            fig = px.histogram(
                chart_df,
                x=risk_score_col,
                nbins=20,
                template="plotly_dark",
                title="Live Risk Scores"
            )

            fig.update_layout(
                height=420,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        # ----------------------------------------------------
        # DETECTION SIGNALS
        # ----------------------------------------------------

        if spam_col or duplicate_col:

            section_header(
                "Detection Signals",
                "Signals generated by the TrustLens content-analysis engine."
            )

            signal_data = {}

            if spam_col:

                signal_data["Spam Score"] = pd.to_numeric(
                    df[spam_col],
                    errors="coerce"
                ).fillna(0)

            if duplicate_col:

                signal_data["Duplicate Score"] = pd.to_numeric(
                    df[duplicate_col],
                    errors="coerce"
                ).fillna(0)

            if (
                "Spam Score" in signal_data
                and
                "Duplicate Score" in signal_data
            ):

                signal_df = pd.DataFrame(
                    signal_data
                )

                fig = px.scatter(
                    signal_df,
                    x="Spam Score",
                    y="Duplicate Score",
                    template="plotly_dark",
                    title="Spam vs Duplicate Signals"
                )

                fig.update_layout(
                    height=420,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

        # ----------------------------------------------------
        # RECENT RESULTS TABLE
        # ----------------------------------------------------

        section_header(
            "Recent TrustLens Results",
            "Latest posts received from the PostgreSQL-backed API."
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

        if display_columns:

            recent = df[
                display_columns
            ].copy()

            # Newest first.
            recent = recent.iloc[::-1]

            display_dataframe(
                recent.head(100),
                600
            )

        else:

            display_dataframe(
                df.head(100),
                600
            )

        # ----------------------------------------------------
        # SUSPICIOUS POSTS
        # ----------------------------------------------------

        if suspicious_posts > 0:

            section_header(
                "⚠️ Suspicious Posts",
                "Posts flagged by the TrustLens detection engine."
            )

            suspicious_df = df[
                suspicious_mask
            ].copy()

            suspicious_df = (
                suspicious_df
                .iloc[::-1]
            )

            display_dataframe(
                suspicious_df.head(100),
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

        # ----------------------------------------------------
        # POST LEVEL ANALYSIS
        # ----------------------------------------------------

        section_header(
            "Post-Level TrustLens Analysis",
            "Detailed analysis of individual social-media posts."
        )

        recent_rows = (
            df.iloc[::-1]
            .head(20)
        )

        for index, row in recent_rows.iterrows():

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

            level_value = (
                row[risk_level_col]
                if risk_level_col
                else "UNKNOWN"
            )

            row_suspicious = (
                bool(
                    suspicious_mask.loc[index]
                )
                if index in suspicious_mask.index
                else False
            )

            # -----------------------------------------------
            # POST CARD
            # -----------------------------------------------

            badge = render_risk_badge(
                level_value,
                row_suspicious,
                risk_value
            )

            render_html(
                f"""
                <div class="post-card">

                    <div style="
                        display:flex;
                        justify-content:space-between;
                        align-items:center;
                        gap:20px;
                    ">

                        <div>

                            <div class="post-user">
                                👤 {user_value}
                            </div>

                            <div class="post-meta">
                                TrustLens monitored post
                            </div>

                        </div>

                        <div>
                            {badge}
                        </div>

                    </div>

                    <div class="post-text">
                        {text_value}
                    </div>

                </div>
                """
            )

            # -----------------------------------------------
            # METRICS
            # -----------------------------------------------

            c1, c2, c3, c4 = st.columns(4)

            with c1:

                metric_card(
                    "SPAM",
                    f"{safe_float(spam_value):.2f}",
                    "Spam signal"
                )

            with c2:

                metric_card(
                    "DUPLICATE",
                    f"{safe_float(duplicate_value):.2f}",
                    "Similarity signal"
                )

            with c3:

                metric_card(
                    "RISK",
                    f"{safe_float(risk_value):.2f}",
                    "Overall risk"
                )

            with c4:

                metric_card(
                    "LEVEL",
                    str(level_value).upper(),
                    "TrustLens classification"
                )


# ============================================================
# ATTACK SIMULATION
# ============================================================

elif page == "Attack Simulation":

    section_header(
        "Attack Simulation",
        "Generate controlled synthetic attacks for TrustLens testing."
    )

    st.info(
        "Your existing attack-simulation modules can remain here. "
        "This section does not affect the persistent social-media database."
    )

    tab_comment, tab_rating = st.tabs(
        [
            "Comment Attack",
            "Rating Attack"
        ]
    )

    with tab_comment:

        st.markdown(
            "### Comment Manipulation Injection"
        )

        comment_count = st.slider(
            "Number of synthetic comments",
            min_value=1,
            max_value=300,
            value=100,
            step=1
        )

        st.info(
            "Use your existing comment attack detector "
            "from the project's src/ directory."
        )

    with tab_rating:

        st.markdown(
            "### Rating Manipulation Injection"
        )

        rating_count = st.slider(
            "Number of synthetic ratings",
            min_value=1,
            max_value=300,
            value=60,
            step=1
        )

        st.info(
            "Use your existing rating attack detector "
            "from the project's src/ directory."
        )


# ============================================================
# DATA EXPLORER
# ============================================================

elif page == "Data Explorer":

    section_header(
        "Data Explorer",
        "Inspect the underlying TrustLens datasets."
    )

    # Refresh live API data whenever this page opens.
    live_posts = load_live_posts()
    live_analysis = load_live_analysis()
    live_users = load_live_users()

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
        ]

        if selected_df is None:

            st.warning(
                "No data available."
            )

        else:

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

                memory = (
                    selected_df
                    .memory_usage(deep=True)
                    .sum()
                    / 1024
                )

                metric_card(
                    "MEMORY",
                    f"{memory:.1f} KB",
                    "Approximate size"
                )

            st.markdown(
                "### Dataset Preview"
            )

            display_dataframe(
                selected_df.head(200),
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

        Behavioral Detection •
        Coordination Analysis •
        Rating Security •
        Recommendation Integrity

        <br><br>

        <span style="opacity:0.6;">
            Live data powered by Render + PostgreSQL
        </span>

    </div>
    """
)