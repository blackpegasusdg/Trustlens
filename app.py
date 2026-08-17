import os
import html
from pathlib import Path
from textwrap import dedent

import pandas as pd
import plotly.express as px
import requests
import streamlit as st


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
    return html.escape(str(value))


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


def display_dataframe(
    df,
    height=430
):
    if df is None or df.empty:
        st.info("No data available.")
        return

    st.dataframe(
        df,
        use_container_width=True,
        height=height,
        hide_index=True
    )


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

        if not isinstance(data, list):
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


# ============================================================
# LIVE ANALYSIS HELPERS
# ============================================================

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


def infer_risk_level(score):

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
# LOAD LIVE DATA
# ============================================================

live_analysis = load_live_analysis()


# ============================================================
# API STATUS
# ============================================================

api_status = check_api_health()


# ============================================================
# SIDEBAR
# ============================================================

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
        check_api_health.clear()
        st.rerun()

    st.markdown("---")

    render_html(
        """
        <div style="
            color:#79aaff;
            font-size:13px;
            font-weight:700;
            margin-bottom:10px;
        ">
            COMMAND CENTER
        </div>

        <div style="
            background:rgba(110,160,255,0.10);
            border:1px solid rgba(110,160,255,0.22);
            border-radius:10px;
            padding:11px 12px;
            color:#eaf0ff;
            font-size:13px;
            font-weight:600;
        ">
            🟢 Live Social Analysis
        </div>
        """
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

            TrustLens analyzes social-media posts
            in real time using behavioral,
            spam, duplicate and risk signals.

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
# LIVE SOCIAL ANALYSIS
# ============================================================

section_header(
    "Live Social Analysis",
    "Real-time TrustLens analysis of posts submitted through the social platform."
)


# ============================================================
# REFRESH + STATUS
# ============================================================

c_refresh, c_status = st.columns(
    [1, 4]
)

with c_refresh:

    if st.button(
        "🔄 Refresh",
        use_container_width=True
    ):

        refresh_live_data()
        check_api_health.clear()
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


# ============================================================
# API UNAVAILABLE
# ============================================================

if live_analysis is None:

    st.warning(
        "TrustLens could not retrieve live analysis from the FastAPI backend."
    )

    st.markdown(
        """
        ### Expected pipeline

        **React → FastAPI → TrustLens Analysis → `/analysis` → Dashboard**

        If your Render backend has just started, wait a few seconds
        and press **Refresh**.
        """
    )


# ============================================================
# NO DATA
# ============================================================

else:

    df = normalize_dataframe(
        live_analysis
    )

    if df.empty:

        st.info(
            "The API is online but no analysis records exist yet."
        )

    else:

        # ====================================================
        # DETECT COLUMNS
        # ====================================================

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


        # ====================================================
        # SUSPICIOUS MASK
        # ====================================================

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


        # ====================================================
        # RISK VALUES
        # ====================================================

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

            risk_values = pd.Series(
                0.0,
                index=df.index
            )

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


        # ====================================================
        # LIVE RISK DISTRIBUTION
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
                risk_counts["Risk Level"]
                .value_counts()
                .reset_index()
            )

            risk_counts.columns = [
                "Risk Level",
                "Posts"
            ]

        else:

            risk_counts = None


        if (
            risk_counts is not None
            and not risk_counts.empty
        ):

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


        # ====================================================
        # RISK SCORE DISTRIBUTION
        # ====================================================

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


        # ====================================================
        # SIGNAL ANALYSIS
        # ====================================================

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

        recent = (
            df.iloc[::-1]
            .head(100)
        )

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


        # ====================================================
        # SUSPICIOUS POSTS
        # ====================================================

        if suspicious_count:

            section_header(
                "⚠️ Suspicious Posts",
                "Posts flagged by the TrustLens detection engine."
            )

            display_dataframe(
                df.loc[
                    suspicious_mask
                ]
                .iloc[::-1]
                .head(100),
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
# FOOTER
# ============================================================

render_html(
    """
    <div class="footer">

        🛡️ TRUSTLENS &nbsp;•&nbsp;
        AI-Powered Social Media Authenticity & Security Analysis

        <br><br>

        Behavioral Detection • Spam Detection •
        Duplicate Detection • Risk Analysis

    </div>
    """
)