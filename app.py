import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
from pathlib import Path


# ============================================================
# TRUSTLENS
# AI-POWERED SOCIAL MEDIA AUTHENTICITY &
# RECOMMENDATION SECURITY ANALYZER
# ============================================================


# ============================================================
# 1. PROJECT PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "src" / "data"


# ============================================================
# 2. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="TrustLens Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# 3. CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* Main background */

    .stApp {
        background:
        radial-gradient(
            circle at 20% 10%,
            rgba(40, 80, 140, 0.12),
            transparent 35%
        ),
        radial-gradient(
            circle at 80% 20%,
            rgba(100, 50, 150, 0.10),
            transparent 35%
        ),
        #080b12;
    }


    /* Main content */

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }


    /* Header */

    .hero {

        padding: 25px 30px;

        border-radius: 18px;

        background:
        linear-gradient(
            135deg,
            rgba(20, 28, 45, 0.95),
            rgba(12, 16, 27, 0.95)
        );

        border: 1px solid rgba(255,255,255,0.08);

        box-shadow:
        0 10px 40px rgba(0,0,0,0.35);

        margin-bottom: 25px;
    }


    .hero-title {

        font-size: 44px;

        font-weight: 800;

        letter-spacing: 2px;

        margin-bottom: 5px;
    }


    .hero-subtitle {

        color: #8f9bb3;

        font-size: 17px;

        letter-spacing: 0.5px;
    }


    .status {

        display: inline-block;

        margin-top: 15px;

        padding: 6px 14px;

        border-radius: 20px;

        background: rgba(0, 200, 120, 0.10);

        border: 1px solid rgba(0, 200, 120, 0.30);

        color: #35e09a;

        font-size: 13px;

        font-weight: 600;
    }


    /* KPI cards */

    .kpi {

        padding: 20px;

        border-radius: 15px;

        background:
        linear-gradient(
            145deg,
            rgba(23,30,47,0.95),
            rgba(12,17,28,0.95)
        );

        border: 1px solid rgba(255,255,255,0.07);

        min-height: 125px;

        box-shadow:
        0 8px 25px rgba(0,0,0,0.25);
    }


    .kpi-title {

        color: #8995aa;

        font-size: 13px;

        text-transform: uppercase;

        letter-spacing: 1px;
    }


    .kpi-value {

        font-size: 32px;

        font-weight: 800;

        margin-top: 8px;
    }


    .kpi-description {

        color: #69758a;

        font-size: 12px;

        margin-top: 5px;
    }


    /* Section titles */

    .section-title {

        font-size: 24px;

        font-weight: 700;

        margin-top: 30px;

        margin-bottom: 15px;
    }


    .section-description {

        color: #7f8ba0;

        font-size: 14px;

        margin-bottom: 15px;
    }


    /* Alert cards */

    .alert-card {

        padding: 18px;

        border-radius: 14px;

        background:
        rgba(255, 70, 70, 0.07);

        border:
        1px solid rgba(255,70,70,0.20);

        margin-bottom: 10px;
    }


    .warning-card {

        padding: 18px;

        border-radius: 14px;

        background:
        rgba(255,170,50,0.07);

        border:
        1px solid rgba(255,170,50,0.20);
    }


    /* Tables */

    [data-testid="stDataFrame"] {

        border-radius: 12px;

        overflow: hidden;
    }


    /* Sidebar */

    section[data-testid="stSidebar"] {

        background:
        linear-gradient(
            180deg,
            #0c111d,
            #080b12
        );
    }


    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 4. PLOTLY DARK THEME
# ============================================================

PLOT_BG = "#0c111d"
GRID_COLOR = "rgba(255,255,255,0.06)"
TEXT_COLOR = "#d9e1ef"


def style_plot(fig):

    fig.update_layout(

        paper_bgcolor=PLOT_BG,

        plot_bgcolor=PLOT_BG,

        font=dict(
            color=TEXT_COLOR
        ),

        margin=dict(
            l=20,
            r=20,
            t=55,
            b=20
        ),

        legend=dict(
            bgcolor="rgba(0,0,0,0)"
        )
    )

    fig.update_xaxes(
        gridcolor=GRID_COLOR
    )

    fig.update_yaxes(
        gridcolor=GRID_COLOR
    )

    return fig


# ============================================================
# 5. LOAD DATA
# ============================================================

@st.cache_data
def load_csv(filename):

    path = DATA_DIR / filename

    if not path.exists():
        return pd.DataFrame()

    try:
        return pd.read_csv(path)

    except Exception:
        return pd.DataFrame()


scores = load_csv("trustlens_scores.csv")

impact = load_csv("recommendation_impact.csv")

ratings = load_csv("ratings.csv")

users = load_csv("users.csv")

users_scored = load_csv("users_scored.csv")

comments = load_csv("comments.csv")

comments_scored = load_csv("comments_scored.csv")

coordination = load_csv("coordination_events.csv")

graph_features = load_csv("graph_features.csv")

rating_analysis = load_csv("rating_analysis.csv")

recommendation_ranking = load_csv(
    "recommendation_ranking.csv"
)


# ============================================================
# 6. SAFETY CHECK
# ============================================================

if scores.empty:

    st.error(
        "trustlens_scores.csv could not be loaded."
    )

    st.info(
        f"Expected location:\n{DATA_DIR / 'trustlens_scores.csv'}"
    )

    st.stop()


# ============================================================
# 7. COLUMN DETECTION
# ============================================================

def find_column(df, names):

    if df.empty:
        return None

    for name in names:

        if name in df.columns:
            return name

    return None


USER = find_column(
    scores,
    ["user_id", "userid", "user"]
)

RISK = find_column(
    scores,
    ["risk_score", "risk"]
)

RISK_LEVEL = find_column(
    scores,
    ["risk_level", "risk_category"]
)

BOT = find_column(
    scores,
    ["bot_score", "bot_risk"]
)

SPAM = find_column(
    scores,
    ["spam_score", "spam_risk"]
)

DUPLICATE = find_column(
    scores,
    ["duplicate_score", "duplicate_risk"]
)

COORDINATION = find_column(
    scores,
    ["coordination_score", "coordination_risk"]
)

RATING_ATTACK = find_column(
    scores,
    [
        "rating_attack_score",
        "rating_attack_risk"
    ]
)

CAMPAIGN = find_column(
    scores,
    [
        "campaign_boost",
        "campaign_score"
    ]
)


# ============================================================
# 8. CALCULATE GLOBAL METRICS
# ============================================================

TOTAL_USERS = len(scores)


if RISK_LEVEL:

    risk_series = (
        scores[RISK_LEVEL]
        .astype(str)
        .str.upper()
    )

    HIGH_RISK = (
        risk_series == "HIGH RISK"
    ).sum()

    MEDIUM_RISK = (
        risk_series == "MEDIUM RISK"
    ).sum()

    LOW_RISK = (
        risk_series == "LOW RISK"
    ).sum()

else:

    HIGH_RISK = 0
    MEDIUM_RISK = 0
    LOW_RISK = TOTAL_USERS


SUSPICIOUS = HIGH_RISK + MEDIUM_RISK


# ============================================================
# 9. SIDEBAR
# ============================================================

st.sidebar.markdown(
    """
    <div style="
        font-size:26px;
        font-weight:800;
        padding:10px 0 20px 0;
    ">
        🛡️ TrustLens
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.caption(
    "Social Integrity Intelligence Platform"
)

st.sidebar.markdown("---")

page = st.sidebar.radio(
    "NAVIGATION",
    [
        "◉ Command Center",
        "◉ Account Intelligence",
        "◉ Threat Detection",
        "◉ Coordination Network",
        "◉ Rating Attack Lab",
        "◉ Recommendation Security",
        "◉ Data Explorer"
    ]
)

st.sidebar.markdown("---")

st.sidebar.markdown(
    "**SYSTEM STATUS**"
)

st.sidebar.success(
    "● ANALYSIS ENGINE ONLINE"
)

st.sidebar.caption(
    f"Users: {TOTAL_USERS:,}"
)

st.sidebar.caption(
    f"Suspicious: {SUSPICIOUS:,}"
)

st.sidebar.caption(
    f"High Risk: {HIGH_RISK:,}"
)


# ============================================================
# 10. HERO HEADER
# ============================================================

st.markdown(
    """
    <div class="hero">

        <div class="hero-title">
            🛡️ TRUSTLENS
        </div>

        <div class="hero-subtitle">
            AI-Powered Social Media Authenticity,
            Bias & Recommendation Security Analyzer
        </div>

        <div class="status">
            ● THREAT ANALYSIS ENGINE ACTIVE
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# PAGE 1 — COMMAND CENTER
# ============================================================

if page == "◉ Command Center":

    st.markdown(
        '<div class="section-title">'
        'Command Center'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-description">'
        'Real-time overview of platform integrity and '
        'detected manipulation signals.'
        '</div>',
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------------

    c1, c2, c3, c4, c5 = st.columns(5)


    with c1:

        st.markdown(
            f"""
            <div class="kpi">

                <div class="kpi-title">
                    Users Analyzed
                </div>

                <div class="kpi-value">
                    {TOTAL_USERS:,}
                </div>

                <div class="kpi-description">
                    Accounts evaluated
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    with c2:

        st.markdown(
            f"""
            <div class="kpi">

                <div class="kpi-title">
                    High Risk
                </div>

                <div class="kpi-value"
                     style="color:#ff4b4b">

                    {HIGH_RISK:,}

                </div>

                <div class="kpi-description">
                    Critical accounts
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    with c3:

        st.markdown(
            f"""
            <div class="kpi">

                <div class="kpi-title">
                    Medium Risk
                </div>

                <div class="kpi-value"
                     style="color:#ffad42">

                    {MEDIUM_RISK:,}

                </div>

                <div class="kpi-description">
                    Requires monitoring
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    with c4:

        rating_attacks = 0

        if RATING_ATTACK:

            rating_attacks = (
                scores[RATING_ATTACK] >= 50
            ).sum()


        st.markdown(
            f"""
            <div class="kpi">

                <div class="kpi-title">
                    Rating Attacks
                </div>

                <div class="kpi-value">
                    {rating_attacks:,}
                </div>

                <div class="kpi-description">
                    Suspicious rating behavior
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    with c5:

        recommendation_changes = len(
            impact
        )

        st.markdown(
            f"""
            <div class="kpi">

                <div class="kpi-title">
                    Recommendation Events
                </div>

                <div class="kpi-value">
                    {recommendation_changes:,}
                </div>

                <div class="kpi-description">
                    Items analyzed
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    # --------------------------------------------------------
    # RISK LANDSCAPE
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">'
        'Risk Landscape'
        '</div>',
        unsafe_allow_html=True
    )


    left, right = st.columns([1, 1])


    with left:

        if RISK_LEVEL:

            dist = (
                scores[RISK_LEVEL]
                .value_counts()
                .reset_index()
            )

            dist.columns = [
                "Risk Level",
                "Count"
            ]

            fig = px.pie(
                dist,
                names="Risk Level",
                values="Count",
                hole=0.62,
                title="Platform Risk Distribution"
            )

            fig.update_traces(
                textposition="outside",
                textinfo="label+percent"
            )

            style_plot(fig)

            st.plotly_chart(
                fig,
                use_container_width=True
            )


    with right:

        if RISK:

            fig = px.histogram(
                scores,
                x=RISK,
                nbins=25,
                title="Risk Score Distribution"
            )

            style_plot(fig)

            st.plotly_chart(
                fig,
                use_container_width=True
            )


    # --------------------------------------------------------
    # THREAT COMPONENT BREAKDOWN
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">'
        'Threat Signal Breakdown'
        '</div>',
        unsafe_allow_html=True
    )


    threat_columns = [
        (BOT, "Bot Activity"),
        (SPAM, "Spam"),
        (DUPLICATE, "Duplicate Content"),
        (COORDINATION, "Coordination"),
        (RATING_ATTACK, "Rating Attack")
    ]


    threat_data = []

    for col, name in threat_columns:

        if col:

            threat_data.append(
                {
                    "Threat": name,
                    "Average Score":
                    scores[col].mean()
                }
            )


    if threat_data:

        threat_df = pd.DataFrame(
            threat_data
        )

        fig = px.bar(
            threat_df,
            x="Threat",
            y="Average Score",
            text="Average Score",
            title="Average Threat Scores"
        )

        fig.update_traces(
            texttemplate="%{text:.1f}",
            textposition="outside"
        )

        fig.update_yaxes(
            range=[0, 100]
        )

        style_plot(fig)

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # --------------------------------------------------------
    # TOP THREATS
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">'
        '🚨 Highest Risk Accounts'
        '</div>',
        unsafe_allow_html=True
    )


    if RISK:

        top = (
            scores
            .sort_values(
                RISK,
                ascending=False
            )
            .head(10)
        )

        columns = [
            c for c in [
                USER,
                BOT,
                SPAM,
                DUPLICATE,
                COORDINATION,
                RATING_ATTACK,
                CAMPAIGN,
                RISK,
                RISK_LEVEL
            ]
            if c
        ]

        st.dataframe(
            top[columns],
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# PAGE 2 — ACCOUNT INTELLIGENCE
# ============================================================

elif page == "◉ Account Intelligence":

    st.markdown(
        '<div class="section-title">'
        '👤 Account Intelligence'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        "Investigate individual accounts and understand "
        "why TrustLens considers them suspicious."
    )


    # --------------------------------------------------------
    # USER SEARCH
    # --------------------------------------------------------

    if USER:

        user_list = (
            scores[USER]
            .astype(str)
            .tolist()
        )

        selected_user = st.selectbox(
            "Select account",
            user_list
        )

        user_row = scores[
            scores[USER]
            .astype(str)
            == selected_user
        ].iloc[0]


        # ----------------------------------------------------
        # USER RISK
        # ----------------------------------------------------

        if RISK:

            risk_value = float(
                user_row[RISK]
            )

        else:

            risk_value = 0


        col1, col2 = st.columns(
            [1, 2]
        )


        with col1:

            fig = go.Figure(
                go.Indicator(
                    mode="gauge+number",
                    value=risk_value,
                    title={
                        "text": "Overall Risk"
                    },
                    gauge={
                        "axis": {
                            "range": [0, 100]
                        },
                        "bar": {
                            "color": "#ff4b4b"
                        },
                        "steps": [
                            {
                                "range": [0, 35],
                                "color": "#10261e"
                            },
                            {
                                "range": [35, 65],
                                "color": "#332613"
                            },
                            {
                                "range": [65, 100],
                                "color": "#351616"
                            }
                        ]
                    }
                )
            )

            style_plot(fig)

            st.plotly_chart(
                fig,
                use_container_width=True
            )


        with col2:

            st.subheader(
                f"Threat Profile — {selected_user}"
            )

            radar_names = []

            radar_values = []


            for col, name in [
                (BOT, "Bot"),
                (SPAM, "Spam"),
                (DUPLICATE, "Duplicate"),
                (COORDINATION, "Coordination"),
                (RATING_ATTACK, "Rating Attack")
            ]:

                if col:

                    radar_names.append(name)

                    radar_values.append(
                        float(
                            user_row[col]
                        )
                    )


            if radar_values:

                radar_names.append(
                    radar_names[0]
                )

                radar_values.append(
                    radar_values[0]
                )

                fig = go.Figure()

                fig.add_trace(
                    go.Scatterpolar(
                        r=radar_values,
                        theta=radar_names,
                        fill="toself",
                        name="Threat Profile"
                    )
                )

                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 100]
                        )
                    ),
                    title="Behavioral Threat Fingerprint"
                )

                style_plot(fig)

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )


        # ----------------------------------------------------
        # WHY SUSPICIOUS?
        # ----------------------------------------------------

        st.subheader(
            "🔍 Why is this account suspicious?"
        )

        explanations = []


        if BOT and user_row[BOT] >= 60:

            explanations.append(
                "🤖 Strong bot-like behavioral signals"
            )


        if SPAM and user_row[SPAM] >= 50:

            explanations.append(
                "📨 High spam activity detected"
            )


        if DUPLICATE and user_row[DUPLICATE] >= 50:

            explanations.append(
                "♻️ Repeated/duplicate content detected"
            )


        if COORDINATION and user_row[COORDINATION] >= 50:

            explanations.append(
                "🕸️ Coordinated engagement pattern detected"
            )


        if RATING_ATTACK and user_row[RATING_ATTACK] >= 50:

            explanations.append(
                "⭐ Suspicious rating behavior detected"
            )


        if not explanations:

            explanations.append(
                "🟢 No individual signal crossed "
                "the strong-warning threshold."
            )


        for explanation in explanations:

            st.info(explanation)


# ============================================================
# PAGE 3 — THREAT DETECTION
# ============================================================

elif page == "◉ Threat Detection":

    st.markdown(
        '<div class="section-title">'
        '🤖 Threat Detection Laboratory'
        '</div>',
        unsafe_allow_html=True
    )

    st.write(
        "Explore the individual detection signals used "
        "by the TrustLens scoring engine."
    )


    detection_columns = [
        (BOT, "Bot Detection"),
        (SPAM, "Spam Detection"),
        (DUPLICATE, "Duplicate Detection"),
        (COORDINATION, "Coordination Detection"),
        (RATING_ATTACK, "Rating Attack Detection")
    ]


    for col, name in detection_columns:

        if not col:
            continue

        st.markdown(
            f"### {name}"
        )


        avg = scores[col].mean()

        maximum = scores[col].max()

        suspicious_count = (
            scores[col] >= 50
        ).sum()


        c1, c2, c3 = st.columns(3)


        c1.metric(
            "Average",
            f"{avg:.2f}"
        )

        c2.metric(
            "Maximum",
            f"{maximum:.2f}"
        )

        c3.metric(
            "Above 50",
            f"{suspicious_count:,}"
        )


        fig = px.histogram(
            scores,
            x=col,
            nbins=20,
            title=f"{name} Distribution"
        )

        fig.add_vline(
            x=50,
            line_dash="dash",
            annotation_text="Alert Threshold"
        )

        style_plot(fig)

        st.plotly_chart(
            fig,
            use_container_width=True
        )


# ============================================================
# PAGE 4 — COORDINATION NETWORK
# ============================================================

elif page == "◉ Coordination Network":

    st.markdown(
        '<div class="section-title">'
        '🕸️ Coordinated Activity Network'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        "This view exposes groups of accounts that appear "
        "to interact or behave together."
    )


    if coordination.empty:

        st.warning(
            "coordination_events.csv was not found "
            "or contains no data."
        )

        if not graph_features.empty:

            st.info(
                "Graph feature data is available, "
                "but no event-level network was found."
            )

            st.dataframe(
                graph_features.head(100),
                use_container_width=True
            )

    else:

        st.success(
            f"{len(coordination):,} coordination events loaded."
        )


        # ----------------------------------------------------
        # Automatically identify source / target
        # ----------------------------------------------------

        source_col = find_column(
            coordination,
            [
                "source",
                "source_user",
                "user_id",
                "user1",
                "from_user"
            ]
        )

        target_col = find_column(
            coordination,
            [
                "target",
                "target_user",
                "user2",
                "to_user"
            ]
        )


        if source_col and target_col:

            edges = coordination[
                [source_col, target_col]
            ].dropna()


            G = nx.Graph()


            for _, row in edges.iterrows():

                source = str(
                    row[source_col]
                )

                target = str(
                    row[target_col]
                )

                if source != target:

                    G.add_edge(
                        source,
                        target
                    )


            # ------------------------------------------------
            # Limit to largest connected component
            # ------------------------------------------------

            if len(G.nodes) > 0:

                components = list(
                    nx.connected_components(G)
                )

                largest = max(
                    components,
                    key=len
                )

                G = G.subgraph(
                    largest
                ).copy()


                # Limit for visualization
                if len(G.nodes) > 80:

                    important_nodes = sorted(
                        G.degree,
                        key=lambda x: x[1],
                        reverse=True
                    )[:80]

                    important_nodes = [
                        n for n, d
                        in important_nodes
                    ]

                    G = G.subgraph(
                        important_nodes
                    ).copy()


                pos = nx.spring_layout(
                    G,
                    seed=42,
                    k=0.7
                )


                # --------------------------------------------
                # Edges
                # --------------------------------------------

                edge_x = []
                edge_y = []


                for edge in G.edges():

                    x0, y0 = pos[
                        edge[0]
                    ]

                    x1, y1 = pos[
                        edge[1]
                    ]


                    edge_x.extend(
                        [x0, x1, None]
                    )

                    edge_y.extend(
                        [y0, y1, None]
                    )


                edge_trace = go.Scatter(
                    x=edge_x,
                    y=edge_y,
                    mode="lines",
                    line=dict(
                        width=1,
                        color="rgba(120,140,170,0.35)"
                    ),
                    hoverinfo="none"
                )


                # --------------------------------------------
                # Nodes
                # --------------------------------------------

                node_x = []
                node_y = []
                node_text = []
                node_size = []


                for node in G.nodes():

                    x, y = pos[node]

                    node_x.append(x)

                    node_y.append(y)

                    degree = G.degree(node)

                    node_size.append(
                        8 + degree * 3
                    )

                    node_text.append(
                        f"{node}<br>"
                        f"Connections: {degree}"
                    )


                node_trace = go.Scatter(
                    x=node_x,
                    y=node_y,
                    mode="markers",
                    hoverinfo="text",
                    text=node_text,
                    marker=dict(
                        size=node_size,
                        color=node_size,
                        colorscale="Turbo",
                        showscale=True,
                        colorbar=dict(
                            title="Connections"
                        ),
                        line=dict(
                            width=1,
                            color="white"
                        )
                    )
                )


                fig = go.Figure(
                    data=[
                        edge_trace,
                        node_trace
                    ]
                )


                fig.update_layout(
                    title=(
                        "Coordinated Account Network"
                    ),
                    showlegend=False,
                    hovermode="closest",
                    height=650,
                    xaxis=dict(
                        showgrid=False,
                        zeroline=False,
                        showticklabels=False
                    ),
                    yaxis=dict(
                        showgrid=False,
                        zeroline=False,
                        showticklabels=False
                    )
                )


                style_plot(fig)


                st.plotly_chart(
                    fig,
                    use_container_width=True
                )


                st.info(
                    "Larger nodes represent accounts with "
                    "more connections inside the detected "
                    "coordination cluster."
                )


        else:

            st.warning(
                "Could not automatically identify source "
                "and target user columns."
            )

            st.write(
                "Available columns:"
            )

            st.code(
                ", ".join(
                    coordination.columns
                )
            )


# ============================================================
# PAGE 5 — RATING ATTACK LAB
# ============================================================

elif page == "◉ Rating Attack Lab":

    st.markdown(
        '<div class="section-title">'
        '⭐ Rating Attack Laboratory'
        '</div>',
        unsafe_allow_html=True
    )

    st.write(
        "Identify accounts whose rating behavior "
        "may artificially influence item reputation."
    )


    if RATING_ATTACK:

        threshold = st.slider(
            "Detection threshold",
            0,
            100,
            50
        )


        attacks = scores[
            scores[RATING_ATTACK]
            >= threshold
        ].copy()


        c1, c2, c3 = st.columns(3)


        c1.metric(
            "Suspicious Accounts",
            f"{len(attacks):,}"
        )


        c2.metric(
            "Platform Percentage",
            f"{len(attacks) / len(scores) * 100:.2f}%"
        )


        c3.metric(
            "Threshold",
            threshold
        )


        st.markdown("---")


        if len(attacks) > 0:

            if RISK:

                attacks = attacks.sort_values(
                    RISK,
                    ascending=False
                )


            columns = [
                c for c in [
                    USER,
                    RATING_ATTACK,
                    BOT,
                    SPAM,
                    DUPLICATE,
                    COORDINATION,
                    RISK,
                    RISK_LEVEL
                ]
                if c
            ]


            st.dataframe(
                attacks[columns],
                use_container_width=True,
                hide_index=True
            )


            # ----------------------------------------------
            # Attack severity distribution
            # ----------------------------------------------

            fig = px.histogram(
                attacks,
                x=RATING_ATTACK,
                nbins=15,
                title="Rating Attack Severity"
            )

            style_plot(fig)

            st.plotly_chart(
                fig,
                use_container_width=True
            )


        else:

            st.success(
                "No accounts crossed the selected threshold."
            )


    else:

        st.warning(
            "Rating attack scores are unavailable."
        )


# ============================================================
# PAGE 6 — RECOMMENDATION SECURITY
# ============================================================

elif page == "◉ Recommendation Security":

    st.markdown(
        '<div class="section-title">'
        '🎯 Recommendation Security'
        '</div>',
        unsafe_allow_html=True
    )

    st.write(
        "Measure how suspicious activity changes the "
        "recommendation system."
    )


    if impact.empty:

        st.warning(
            "recommendation_impact.csv is empty."
        )

    else:

        item_col = find_column(
            impact,
            [
                "item_id",
                "item"
            ]
        )

        original_rank = find_column(
            impact,
            [
                "original_rank"
            ]
        )

        clean_rank = find_column(
            impact,
            [
                "clean_rank"
            ]
        )

        rank_change = find_column(
            impact,
            [
                "rank_change"
            ]
        )

        original_score = find_column(
            impact,
            [
                "original_score"
            ]
        )

        clean_score = find_column(
            impact,
            [
                "clean_score"
            ]
        )

        score_change = find_column(
            impact,
            [
                "score_change"
            ]
        )


        # ----------------------------------------------------
        # Metrics
        # ----------------------------------------------------

        c1, c2, c3, c4 = st.columns(4)


        c1.metric(
            "Items Analyzed",
            f"{len(impact):,}"
        )


        if rank_change:

            largest_rank_change = (
                impact[rank_change]
                .abs()
                .max()
            )

        else:

            largest_rank_change = 0


        c2.metric(
            "Largest Rank Shift",
            f"{largest_rank_change:.0f}"
        )


        if score_change:

            largest_score_change = (
                impact[score_change]
                .abs()
                .max()
            )

        else:

            largest_score_change = 0


        c3.metric(
            "Largest Score Shift",
            f"{largest_score_change:.3f}"
        )


        if rank_change:

            affected = (
                impact[rank_change]
                .abs()
                >= 20
            ).sum()

        else:

            affected = 0


        c4.metric(
            "Majorly Affected",
            f"{affected:,}"
        )


        st.markdown("---")


        # ----------------------------------------------------
        # BIGGEST MANIPULATIONS
        # ----------------------------------------------------

        st.subheader(
            "🚨 Largest Recommendation Manipulations"
        )


        if rank_change:

            largest = (
                impact
                .sort_values(
                    rank_change,
                    key=lambda x: x.abs(),
                    ascending=False
                )
                .head(20)
            )


            st.dataframe(
                largest,
                use_container_width=True,
                hide_index=True
            )


        # ----------------------------------------------------
        # RANK SHIFT GRAPH
        # ----------------------------------------------------

        if (
            item_col
            and rank_change
        ):

            chart = (
                impact
                .sort_values(
                    rank_change,
                    key=lambda x: x.abs(),
                    ascending=False
                )
                .head(20)
            )


            fig = px.bar(
                chart,
                x=item_col,
                y=rank_change,
                title="Recommendation Rank Displacement"
            )


            fig.add_hline(
                y=0,
                line_dash="dash"
            )


            style_plot(fig)


            st.plotly_chart(
                fig,
                use_container_width=True
            )


        # ----------------------------------------------------
        # SCORE CHANGE
        # ----------------------------------------------------

        if (
            item_col
            and score_change
        ):

            st.subheader(
                "Recommendation Score Distortion"
            )


            chart = (
                impact
                .sort_values(
                    score_change,
                    key=lambda x: x.abs(),
                    ascending=False
                )
                .head(20)
            )


            fig = px.bar(
                chart,
                x=item_col,
                y=score_change,
                title="Recommendation Score Changes"
            )


            fig.add_hline(
                y=0,
                line_dash="dash"
            )


            style_plot(fig)


            st.plotly_chart(
                fig,
                use_container_width=True
            )


# ============================================================
# PAGE 7 — DATA EXPLORER
# ============================================================

elif page == "◉ Data Explorer":

    st.markdown(
        '<div class="section-title">'
        '📁 Data Explorer'
        '</div>',
        unsafe_allow_html=True
    )


    datasets = {

        "Risk Scores":
            scores,

        "Recommendation Impact":
            impact,

        "Ratings":
            ratings,

        "Users":
            users,

        "Users Scored":
            users_scored,

        "Comments":
            comments,

        "Comments Scored":
            comments_scored,

        "Coordination Events":
            coordination,

        "Graph Features":
            graph_features,

        "Rating Analysis":
            rating_analysis,

        "Recommendation Ranking":
            recommendation_ranking
    }


    selected = st.selectbox(
        "Select dataset",
        list(datasets.keys())
    )


    df = datasets[selected]


    if df.empty:

        st.warning(
            "This dataset is unavailable or empty."
        )

    else:

        c1, c2 = st.columns(2)

        c1.metric(
            "Rows",
            f"{len(df):,}"
        )

        c2.metric(
            "Columns",
            f"{len(df.columns):,}"
        )


        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )


        csv = df.to_csv(
            index=False
        ).encode("utf-8")


        st.download_button(
            "⬇️ Download Dataset",
            csv,
            file_name=(
                selected
                .lower()
                .replace(" ", "_")
                + ".csv"
            ),
            mime="text/csv"
        )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.markdown(
    """
    <div style="
        text-align:center;
        color:#68758a;
        padding:20px;
    ">

        <b>TRUSTLENS</b><br>

        Social Media Integrity &
        Recommendation Security Platform

        <br><br>

        Detection → Scoring → Attack Analysis →
        Network Intelligence → Recommendation Impact

    </div>
    """,
    unsafe_allow_html=True
)