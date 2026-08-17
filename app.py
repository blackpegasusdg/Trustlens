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
import subprocess
import sys


# ============================================================
# CONFIGURATION
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
            rgba(21,35,65,0.95),
            rgba(11,18,33,0.95)
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
    max-width: 800px;
}

.status {
    display: inline-flex;
    align-items: center;
    gap: 9px;
    margin-top: 24px;
    padding: 9px 15px;

    border-radius: 999px;

    background:
        rgba(60,220,150,0.10);

    border:
        1px solid rgba(60,220,150,0.25);

    color: #74f0b6;

    font-size: 13px;
    font-weight: 700;
}

.kpi-card {
    background:
        linear-gradient(
            135deg,
            rgba(20,32,55,0.95),
            rgba(12,19,34,0.95)
        );

    border:
        1px solid rgba(255,255,255,0.08);

    border-radius: 18px;

    padding: 24px;

    min-height: 145px;

    box-shadow:
        0 12px 35px rgba(0,0,0,0.18);
}

.kpi-label {
    color: #8ea0bd;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1px;
}

.kpi-value {
    font-size: 36px;
    font-weight: 800;
    margin-top: 10px;
}

.kpi-description {
    color: #7183a2;
    font-size: 12px;
    margin-top: 6px;
}

.section-title {
    font-size: 25px;
    font-weight: 800;
    margin-top: 35px;
}

.section-subtitle {
    color: #8294b2;
    margin-bottom: 18px;
}

.success-box {
    padding: 16px 20px;

    border-radius: 14px;

    background:
        rgba(40,210,130,0.10);

    border:
        1px solid rgba(40,210,130,0.25);

    color: #7af0ba;
}

.warning-box {
    padding: 16px 20px;

    border-radius: 14px;

    background:
        rgba(255,180,60,0.10);

    border:
        1px solid rgba(255,180,60,0.25);

    color: #ffd17b;
}

.footer {
    margin-top: 60px;
    padding: 30px;

    text-align: center;

    color: #637594;

    border-top:
        1px solid rgba(255,255,255,0.06);
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


def safe_numeric(df, column):

    if (
        df is None
        or column not in df.columns
    ):

        return pd.Series(
            dtype=float
        )

    return pd.to_numeric(
        df[column],
        errors="coerce"
    ).fillna(0)


def normalize_text(value):

    value = str(value)

    value = value.lower()

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value.strip()


# ============================================================
# DATA DIRECTORIES
# ============================================================

def ensure_live_dir():

    LIVE_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


def ensure_attack_dirs():

    ATTACK_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    ATTACK_RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


ensure_live_dir()
ensure_attack_dirs()


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
# LOAD STATIC TRUSTLENS CSV
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
# LOAD LIVE POSTS
# ============================================================

@st.cache_data(ttl=5)
def load_live_posts():

    try:

        response = requests.get(
            f"{RENDER_API}/posts",
            timeout=20
        )

        response.raise_for_status()

        data = response.json()

        if isinstance(data, dict):

            if "posts" in data:
                data = data["posts"]

            elif "data" in data:
                data = data["data"]

        if not data:

            return pd.DataFrame()

        return pd.DataFrame(data)

    except Exception:

        return pd.DataFrame()


# ============================================================
# LOAD LIVE USERS
# ============================================================

@st.cache_data(ttl=5)
def load_live_users():

    try:

        response = requests.get(
            f"{RENDER_API}/users",
            timeout=20
        )

        response.raise_for_status()

        data = response.json()

        if isinstance(data, dict):

            if "users" in data:
                data = data["users"]

            elif "data" in data:
                data = data["data"]

        if not data:

            return pd.DataFrame()

        return pd.DataFrame(data)

    except Exception:

        return pd.DataFrame()


# ============================================================
# LOAD LIVE TRUSTLENS ANALYSIS
# ============================================================

@st.cache_data(ttl=3)
def load_live_analysis():

    try:

        response = requests.get(
            f"{RENDER_API}/analysis",
            timeout=20
        )

        response.raise_for_status()

        data = response.json()

        # ----------------------------------------------------
        # HANDLE DIFFERENT API RESPONSE FORMATS
        # ----------------------------------------------------

        if isinstance(data, dict):

            if "analysis" in data:
                data = data["analysis"]

            elif "data" in data:
                data = data["data"]

            elif "results" in data:
                data = data["results"]

            else:

                # If the API returned one record
                # rather than a list.
                data = [data]

        if not data:

            return pd.DataFrame()

        df = pd.DataFrame(data)

        return df

    except requests.exceptions.RequestException as e:

        st.error(
            f"""
            Unable to connect to TrustLens Live API.

            Render API:
            {RENDER_API}

            Error:
            {e}
            """
        )

        return pd.DataFrame()

    except Exception as e:

        st.error(
            f"Unable to process TrustLens analysis data: {e}"
        )

        return pd.DataFrame()


# ============================================================
# LOAD STATIC TRUSTLENS DATASETS
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


# ============================================================
# LIVE DATA
#
# IMPORTANT:
# These are now loaded from Render API.
# They are NOT loaded from local CSV files.
# ============================================================

live_posts = load_live_posts()

live_analysis = load_live_analysis()

live_users = load_live_users()


# ============================================================
# NORMALIZE LIVE DATAFRAME
# ============================================================

def normalize_live_dataframe(df):

    if df is None:
        return None

    if df.empty:
        return df

    result = df.copy()

    result.columns = [
        str(column).strip()
        for column in result.columns
    ]

    return result


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
            "risk"
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
            "dup_score"
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
            dtype=bool
        )

    suspicious_col = (
        get_live_suspicious_column(df)
    )

    if suspicious_col:

        values = df[
            suspicious_col
        ]

        return (
            values
            .astype(str)
            .str.lower()
            .isin(
                [
                    "true",
                    "1",
                    "yes",
                    "suspicious"
                ]
            )
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
# SIDEBAR
# ============================================================

st.sidebar.markdown(
    """
    # 🛡️ TrustLens

    **AI-Powered Social Media
    Authenticity & Security**
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

        risk_col = get_risk_column(
            scores
        )

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

    rating_attacks = 0

    if rating_analysis is not None:

        rating_attacks = len(
            rating_analysis
        )

    recommendation_changes = 0

    if recommendation_impact is not None:

        recommendation_changes = len(
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

    st.markdown(
        "<br>",
        unsafe_allow_html=True
    )

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
        "Real-time TrustLens analysis of posts submitted through the social platform."
    )

    col_refresh, col_status = st.columns(
        [1, 4]
    )

    with col_refresh:

        if st.button(
            "🔄 Refresh Analysis",
            use_container_width=True
        ):

            load_live_analysis.clear()
            load_live_posts.clear()
            load_live_users.clear()

            st.rerun()

    with col_status:

        if (
            live_analysis is not None
            and not live_analysis.empty
        ):

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
                    🟡 WAITING FOR LIVE ANALYSIS DATA
                </div>
                """
            )

    st.markdown(
        "<br>",
        unsafe_allow_html=True
    )


    # ========================================================
    # NO DATA
    # ========================================================

    if (
        live_analysis is None
        or live_analysis.empty
    ):

        st.info(
            "No live TrustLens analysis records were found."
        )

        st.markdown(
            """
            ### Waiting for social platform data

            Create a post from your React social-media website.

            The live flow is:

            **React → Render FastAPI → PostgreSQL → TrustLens Dashboard**

            The dashboard reads persistent analysis through:

            **GET /analysis**
            """
        )

    else:

        df = normalize_live_dataframe(
            live_analysis
        )


        # ====================================================
        # IDENTIFY COLUMNS
        # ====================================================

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


        # ====================================================
        # SUSPICIOUS POSTS
        # ====================================================

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


        # ====================================================
        # RISK VALUES
        # ====================================================

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


        # ====================================================
        # KPI CARDS
        # ====================================================

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
                "Posts requiring attention"
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


        # ====================================================
        # RISK DISTRIBUTION
        # ====================================================

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

            fig = px.bar(
                risk_counts,
                x="Risk Level",
                y="Posts",
                text="Posts",
                template="plotly_dark",
                title="Live Post Risk Levels"
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


        # ====================================================
        # RISK SCORE DISTRIBUTION
        # ====================================================

        if risk_score_col:

            section_header(
                "Risk Score Distribution",
                "Distribution of TrustLens risk scores across live posts."
            )

            chart_df = df.copy()

            chart_df[
                risk_score_col
            ] = pd.to_numeric(
                chart_df[risk_score_col],
                errors="coerce"
            ).fillna(0)

            fig = px.histogram(
                chart_df,
                x=risk_score_col,
                nbins=20,
                template="plotly_dark",
                title="Live Risk Score Distribution"
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


        # ====================================================
        # SPAM / DUPLICATE ANALYSIS
        # ====================================================

        if spam_col or duplicate_col:

            section_header(
                "Detection Signals",
                "Signals generated by the TrustLens content-analysis engine."
            )

            signal_data = {}

            if spam_col:

                signal_data[
                    "Spam Score"
                ] = pd.to_numeric(
                    df[spam_col],
                    errors="coerce"
                ).fillna(0)

            if duplicate_col:

                signal_data[
                    "Duplicate Score"
                ] = pd.to_numeric(
                    df[duplicate_col],
                    errors="coerce"
                ).fillna(0)

            if (
                "Spam Score" in signal_data
                and "Duplicate Score" in signal_data
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


        # ====================================================
        # RECENT RESULTS
        # ====================================================

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

        if display_columns:

            recent = df[
                display_columns
            ].copy()

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


        # ====================================================
        # SUSPICIOUS POSTS
        # ====================================================

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


        # ====================================================
        # POST LEVEL ANALYSIS
        # ====================================================

        section_header(
            "Post-Level TrustLens Analysis",
            "Detailed analysis of individual posts."
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

            with st.container():

                st.markdown(
                    "---"
                )

                st.markdown(
                    f"### 👤 {user_value}"
                )

                st.write(
                    text_value
                )

                c1, c2, c3, c4 = st.columns(4)

                with c1:

                    metric_card(
                        "SPAM",
                        f"{float(spam_value):.2f}",
                        "Spam score"
                    )

                with c2:

                    metric_card(
                        "DUPLICATE",
                        f"{float(duplicate_value):.2f}",
                        "Duplicate score"
                    )

                with c3:

                    metric_card(
                        "RISK",
                        f"{float(risk_value):.2f}",
                        "Overall risk"
                    )

                with c4:

                    metric_card(
                        "STATUS",
                        (
                            "⚠️ SUSPICIOUS"
                            if row_suspicious
                            else "✅ SAFE"
                        ),
                        str(level_value)
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

        <br>

        Behavioral Detection •
        Coordination Analysis •
        Rating Security •
        Recommendation Integrity

    </div>
    """
)