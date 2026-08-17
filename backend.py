from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
from datetime import datetime
import pandas as pd
import uuid
import re


# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="TrustLens Live Detection API",
    description="Backend connecting the TrustLens social demo with the TrustLens detection engine",
    version="1.1"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:5176",

        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
        "http://127.0.0.1:5176",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# DIRECTORIES
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
LIVE_DIR = DATA_DIR / "live"

LIVE_DIR.mkdir(parents=True, exist_ok=True)

POSTS_FILE = LIVE_DIR / "posts.csv"
USERS_FILE = LIVE_DIR / "users.csv"
ANALYSIS_FILE = LIVE_DIR / "live_analysis.csv"


# ============================================================
# DATA MODELS
# ============================================================

class Post(BaseModel):
    user: str
    text: str


class User(BaseModel):
    username: str


# ============================================================
# INITIALIZE FILES
# ============================================================

def initialize_files():

    if not POSTS_FILE.exists():

        posts_df = pd.DataFrame(
            columns=[
                "post_id",
                "user_id",
                "text",
                "timestamp",
                "likes",
                "comments",
                "source"
            ]
        )

        posts_df.to_csv(
            POSTS_FILE,
            index=False
        )

    if not USERS_FILE.exists():

        users_df = pd.DataFrame(
            columns=[
                "user_id",
                "timestamp",
                "source"
            ]
        )

        users_df.to_csv(
            USERS_FILE,
            index=False
        )

    if not ANALYSIS_FILE.exists():

        analysis_df = pd.DataFrame(
            columns=[
                "post_id",
                "user_id",
                "text",
                "timestamp",
                "spam_score",
                "duplicate_score",
                "risk_score",
                "risk_level",
                "suspicious"
            ]
        )

        analysis_df.to_csv(
            ANALYSIS_FILE,
            index=False
        )


initialize_files()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def normalize_text(text):

    text = str(text).lower()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def calculate_spam_score(text):

    text_lower = normalize_text(text)

    spam_keywords = [
        "buy now",
        "click here",
        "limited offer",
        "free money",
        "earn money",
        "visit now",
        "subscribe now",
        "winner",
        "congratulations",
        "free",
        "discount",
        "cash prize",
        "make money",
        "urgent",
        "offer"
    ]

    spam_hits = sum(
        keyword in text_lower
        for keyword in spam_keywords
    )

    score = min(
        spam_hits * 20,
        100
    )

    return score


def calculate_duplicate_score(
    text,
    previous_posts
):

    normalized = normalize_text(text)

    if previous_posts.empty:
        return 0

    previous_texts = (
        previous_posts["text"]
        .astype(str)
        .apply(normalize_text)
    )

    if normalized in previous_texts.values:
        return 100

    return 0


def calculate_risk(
    spam_score,
    duplicate_score
):

    risk_score = (
        spam_score * 0.5 +
        duplicate_score * 0.5
    )

    if risk_score >= 70:
        risk_level = "HIGH"

    elif risk_score >= 40:
        risk_level = "MEDIUM"

    else:
        risk_level = "LOW"

    return round(risk_score, 2), risk_level


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/")
def root():

    return {
        "status": "online",
        "service": "TrustLens Live Detection API",
        "version": "1.1"
    }


@app.get("/health")
def health():

    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


# ============================================================
# REGISTER USER
# ============================================================

@app.post("/users")
def register_user(user: User):

    initialize_files()

    username = str(
        user.username
    ).strip()

    if username == "":

        return {
            "success": False,
            "message": "Username cannot be empty"
        }

    users_df = pd.read_csv(
        USERS_FILE
    )

    existing_users = (
        users_df["user_id"]
        .astype(str)
        .tolist()
    )

    if username not in existing_users:

        new_user = pd.DataFrame([
            {
                "user_id": username,
                "timestamp": datetime.now().isoformat(),
                "source": "social-demo"
            }
        ])

        users_df = pd.concat(
            [
                users_df,
                new_user
            ],
            ignore_index=True
        )

        users_df.to_csv(
            USERS_FILE,
            index=False
        )

    return {
        "success": True,
        "user_id": username
    }


# ============================================================
# RECEIVE + ANALYZE POST
# ============================================================

@app.post("/posts")
def receive_post(post: Post):

    initialize_files()

    username = str(
        post.user
    ).strip()

    text = str(
        post.text
    ).strip()

    if username == "":

        return {
            "success": False,
            "message": "User is required"
        }

    if text == "":

        return {
            "success": False,
            "message": "Post cannot be empty"
        }


    # --------------------------------------------------------
    # CREATE POST ID
    # --------------------------------------------------------

    post_id = (
        "POST_" +
        uuid.uuid4().hex[:10].upper()
    )

    timestamp = datetime.now().isoformat()


    # --------------------------------------------------------
    # LOAD EXISTING POSTS
    # --------------------------------------------------------

    posts_df = pd.read_csv(
        POSTS_FILE
    )


    # --------------------------------------------------------
    # DETECT DUPLICATES
    # --------------------------------------------------------

    duplicate_score = calculate_duplicate_score(
        text,
        posts_df
    )


    # --------------------------------------------------------
    # DETECT SPAM
    # --------------------------------------------------------

    spam_score = calculate_spam_score(
        text
    )


    # --------------------------------------------------------
    # CALCULATE RISK
    # --------------------------------------------------------

    risk_score, risk_level = calculate_risk(
        spam_score,
        duplicate_score
    )

    suspicious = risk_score >= 40


    # --------------------------------------------------------
    # SAVE POST
    # --------------------------------------------------------

    new_post = pd.DataFrame([
        {
            "post_id": post_id,
            "user_id": username,
            "text": text,
            "timestamp": timestamp,
            "likes": 0,
            "comments": 0,
            "source": "social-demo"
        }
    ])

    posts_df = pd.concat(
        [
            posts_df,
            new_post
        ],
        ignore_index=True
    )

    posts_df.to_csv(
        POSTS_FILE,
        index=False
    )


    # --------------------------------------------------------
    # SAVE TRUSTLENS ANALYSIS
    # --------------------------------------------------------

    analysis_df = pd.read_csv(
        ANALYSIS_FILE
    )

    new_analysis = pd.DataFrame([
        {
            "post_id": post_id,
            "user_id": username,
            "text": text,
            "timestamp": timestamp,
            "spam_score": spam_score,
            "duplicate_score": duplicate_score,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "suspicious": suspicious
        }
    ])

    analysis_df = pd.concat(
        [
            analysis_df,
            new_analysis
        ],
        ignore_index=True
    )

    analysis_df.to_csv(
        ANALYSIS_FILE,
        index=False
    )


    # --------------------------------------------------------
    # RESPONSE TO REACT
    # --------------------------------------------------------

    return {

        "success": True,

        "post": {
            "post_id": post_id,
            "user_id": username,
            "text": text,
            "timestamp": timestamp
        },

        "analysis": {

            "spam_score": spam_score,

            "duplicate_score": duplicate_score,

            "risk_score": risk_score,

            "risk_level": risk_level,

            "suspicious": suspicious
        }
    }


# ============================================================
# GET ALL POSTS
# ============================================================

@app.get("/posts")
def get_posts():

    initialize_files()

    posts_df = pd.read_csv(
        POSTS_FILE
    )

    return posts_df.to_dict(
        orient="records"
    )


# ============================================================
# GET LIVE TRUSTLENS ANALYSIS
# ============================================================

@app.get("/analysis")
def get_analysis():

    initialize_files()

    analysis_df = pd.read_csv(
        ANALYSIS_FILE
    )

    return analysis_df.to_dict(
        orient="records"
    )


# ============================================================
# GET ANALYSIS FOR ONE POST
# ============================================================

@app.get("/analysis/{post_id}")
def get_post_analysis(post_id: str):

    initialize_files()

    analysis_df = pd.read_csv(
        ANALYSIS_FILE
    )

    result = analysis_df[
        analysis_df["post_id"].astype(str) == str(post_id)
    ]

    if result.empty:

        return {
            "success": False,
            "message": "Post analysis not found"
        }

    return {
        "success": True,
        "analysis": result.iloc[0].to_dict()
    }


# ============================================================
# LIVE STATISTICS
# ============================================================

@app.get("/stats")
def get_stats():

    initialize_files()

    posts_df = pd.read_csv(
        POSTS_FILE
    )

    users_df = pd.read_csv(
        USERS_FILE
    )

    analysis_df = pd.read_csv(
        ANALYSIS_FILE
    )


    high_risk = 0
    medium_risk = 0
    low_risk = 0
    suspicious = 0

    if not analysis_df.empty:

        high_risk = (
            analysis_df["risk_level"]
            .astype(str)
            .str.upper()
            .eq("HIGH")
            .sum()
        )

        medium_risk = (
            analysis_df["risk_level"]
            .astype(str)
            .str.upper()
            .eq("MEDIUM")
            .sum()
        )

        low_risk = (
            analysis_df["risk_level"]
            .astype(str)
            .str.upper()
            .eq("LOW")
            .sum()
        )

        suspicious = (
            analysis_df["suspicious"]
            .astype(str)
            .str.lower()
            .eq("true")
            .sum()
        )


    return {

        "users": len(users_df),

        "posts": len(posts_df),

        "analyzed_posts": len(analysis_df),

        "suspicious_posts": int(suspicious),

        "high_risk": int(high_risk),

        "medium_risk": int(medium_risk),

        "low_risk": int(low_risk),

        "timestamp": datetime.now().isoformat()
    }