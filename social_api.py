from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import os
import uuid
import re
import psycopg2
from psycopg2.extras import RealDictCursor


# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="TrustLens Live Detection API",
    description="TrustLens social demo with persistent PostgreSQL storage",
    version="2.0"
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

        "https://trustlens-tau.vercel.app"
    ],

    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# DATABASE
# ============================================================

DATABASE_URL = os.environ.get("DATABASE_URL")


def get_connection():

    if not DATABASE_URL:

        raise RuntimeError(
            "DATABASE_URL environment variable is not configured"
        )

    return psycopg2.connect(
        DATABASE_URL,
        sslmode="require"
    )


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def initialize_database():

    connection = get_connection()

    try:

        cursor = connection.cursor()


        # ====================================================
        # USERS
        # ====================================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (

                user_id TEXT PRIMARY KEY,

                timestamp TIMESTAMP NOT NULL,

                source TEXT

            )
            """
        )


        # ====================================================
        # POSTS
        # ====================================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS posts (

                post_id TEXT PRIMARY KEY,

                user_id TEXT NOT NULL,

                text TEXT NOT NULL,

                timestamp TIMESTAMP NOT NULL,

                likes INTEGER DEFAULT 0,

                comments INTEGER DEFAULT 0,

                source TEXT

            )
            """
        )


        # ====================================================
        # ANALYSIS
        # ====================================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS analysis (

                post_id TEXT PRIMARY KEY,

                user_id TEXT NOT NULL,

                text TEXT NOT NULL,

                timestamp TIMESTAMP NOT NULL,

                spam_score REAL DEFAULT 0,

                duplicate_score REAL DEFAULT 0,

                risk_score REAL DEFAULT 0,

                risk_level TEXT,

                suspicious BOOLEAN DEFAULT FALSE

            )
            """
        )


        connection.commit()

        cursor.close()

    finally:

        connection.close()


# ============================================================
# STARTUP
# ============================================================

@app.on_event("startup")
def startup():

    initialize_database()


# ============================================================
# DATA MODELS
# ============================================================

class Post(BaseModel):

    user: str
    text: str


class User(BaseModel):

    username: str


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


# ============================================================
# SPAM DETECTION
# ============================================================

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


# ============================================================
# DUPLICATE DETECTION
# ============================================================

def calculate_duplicate_score(
    text,
    previous_posts
):

    normalized = normalize_text(text)


    for post in previous_posts:

        previous_text = normalize_text(
            post["text"]
        )


        if normalized == previous_text:

            return 100


    return 0


# ============================================================
# RISK CALCULATION
# ============================================================

def calculate_risk(
    spam_score,
    duplicate_score
):

    risk_score = (

        spam_score * 0.5

        +

        duplicate_score * 0.5

    )


    if risk_score >= 70:

        risk_level = "HIGH"

    elif risk_score >= 40:

        risk_level = "MEDIUM"

    else:

        risk_level = "LOW"


    return round(
        risk_score,
        2
    ), risk_level


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {

        "status": "online",

        "service":
            "TrustLens Live Detection API",

        "version":
            "2.0",

        "database":
            "PostgreSQL"

    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            "SELECT 1"
        )

        cursor.fetchone()

        cursor.close()

        return {

            "status": "healthy",

            "database":
                "connected",

            "timestamp":
                datetime.now().isoformat()

        }

    finally:

        connection.close()


# ============================================================
# REGISTER USER
# ============================================================

@app.post("/users")
def register_user(user: User):

    username = str(
        user.username
    ).strip()


    if username == "":

        return {

            "success": False,

            "message":
                "Username cannot be empty"

        }


    connection = get_connection()

    try:

        cursor = connection.cursor()


        cursor.execute(
            """
            INSERT INTO users
            (
                user_id,
                timestamp,
                source
            )

            VALUES
            (
                %s,
                %s,
                %s
            )

            ON CONFLICT (user_id)
            DO NOTHING
            """,

            (
                username,
                datetime.now(),
                "social-demo"
            )

        )


        connection.commit()

        cursor.close()


        return {

            "success": True,

            "user_id":
                username

        }

    finally:

        connection.close()


# ============================================================
# RECEIVE + ANALYZE POST
# ============================================================

@app.post("/posts")
def receive_post(post: Post):

    username = str(
        post.user
    ).strip()


    text = str(
        post.text
    ).strip()


    if username == "":

        return {

            "success": False,

            "message":
                "User is required"

        }


    if text == "":

        return {

            "success": False,

            "message":
                "Post cannot be empty"

        }


    # ========================================================
    # CREATE POST ID
    # ========================================================

    post_id = (

        "POST_"

        +

        uuid.uuid4()
        .hex[:10]
        .upper()

    )


    timestamp = datetime.now()


    # ========================================================
    # DATABASE CONNECTION
    # ========================================================

    connection = get_connection()

    try:

        cursor = connection.cursor(
            cursor_factory=RealDictCursor
        )


        # ====================================================
        # GET PREVIOUS POSTS
        # ====================================================

        cursor.execute(
            """
            SELECT
                post_id,
                user_id,
                text,
                timestamp,
                likes,
                comments

            FROM posts

            ORDER BY timestamp ASC
            """
        )


        previous_posts = cursor.fetchall()


        # ====================================================
        # DUPLICATE DETECTION
        # ====================================================

        duplicate_score = (

            calculate_duplicate_score(
                text,
                previous_posts
            )

        )


        # ====================================================
        # SPAM DETECTION
        # ====================================================

        spam_score = (

            calculate_spam_score(
                text
            )

        )


        # ====================================================
        # RISK
        # ====================================================

        risk_score, risk_level = (

            calculate_risk(
                spam_score,
                duplicate_score
            )

        )


        suspicious = (
            risk_score >= 40
        )


        # ====================================================
        # MAKE SURE USER EXISTS
        # ====================================================

        cursor.execute(
            """
            INSERT INTO users
            (
                user_id,
                timestamp,
                source
            )

            VALUES
            (
                %s,
                %s,
                %s
            )

            ON CONFLICT (user_id)
            DO NOTHING
            """,

            (
                username,
                timestamp,
                "social-demo"
            )

        )


        # ====================================================
        # SAVE POST
        # ====================================================

        cursor.execute(
            """
            INSERT INTO posts
            (
                post_id,
                user_id,
                text,
                timestamp,
                likes,
                comments,
                source
            )

            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,

            (
                post_id,
                username,
                text,
                timestamp,
                0,
                0,
                "social-demo"
            )

        )


        # ====================================================
        # SAVE ANALYSIS
        # ====================================================

        cursor.execute(
            """
            INSERT INTO analysis
            (
                post_id,
                user_id,
                text,
                timestamp,
                spam_score,
                duplicate_score,
                risk_score,
                risk_level,
                suspicious
            )

            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,

            (
                post_id,
                username,
                text,
                timestamp,
                spam_score,
                duplicate_score,
                risk_score,
                risk_level,
                suspicious
            )

        )


        connection.commit()

        cursor.close()


        # ====================================================
        # RESPONSE
        # ====================================================

        return {

            "success": True,

            "post": {

                "post_id":
                    post_id,

                "user_id":
                    username,

                "text":
                    text,

                "timestamp":
                    timestamp.isoformat(),

                "likes":
                    0,

                "comments":
                    0

            },

            "analysis": {

                "spam_score":
                    spam_score,

                "duplicate_score":
                    duplicate_score,

                "risk_score":
                    risk_score,

                "risk_level":
                    risk_level,

                "suspicious":
                    suspicious

            }

        }


    except Exception:

        connection.rollback()

        raise


    finally:

        connection.close()


# ============================================================
# GET ALL POSTS
# ============================================================

@app.get("/posts")
def get_posts():

    connection = get_connection()

    try:

        cursor = connection.cursor(
            cursor_factory=RealDictCursor
        )


        cursor.execute(
            """
            SELECT

                post_id,

                user_id,

                text,

                timestamp,

                likes,

                comments,

                source

            FROM posts

            ORDER BY timestamp DESC
            """
        )


        posts = cursor.fetchall()


        cursor.close()


        # Convert timestamps to strings
        for post in posts:

            if post["timestamp"]:

                post["timestamp"] = (
                    post["timestamp"]
                    .isoformat()
                )


        return posts


    finally:

        connection.close()


# ============================================================
# GET LIVE TRUSTLENS ANALYSIS
# ============================================================

@app.get("/analysis")
def get_analysis():

    connection = get_connection()

    try:

        cursor = connection.cursor(
            cursor_factory=RealDictCursor
        )


        cursor.execute(
            """
            SELECT

                post_id,

                user_id,

                text,

                timestamp,

                spam_score,

                duplicate_score,

                risk_score,

                risk_level,

                suspicious

            FROM analysis

            ORDER BY timestamp DESC
            """
        )


        results = cursor.fetchall()


        cursor.close()


        for result in results:

            if result["timestamp"]:

                result["timestamp"] = (
                    result["timestamp"]
                    .isoformat()
                )


        return results


    finally:

        connection.close()


# ============================================================
# GET ANALYSIS FOR ONE POST
# ============================================================

@app.get("/analysis/{post_id}")
def get_post_analysis(post_id: str):

    connection = get_connection()

    try:

        cursor = connection.cursor(
            cursor_factory=RealDictCursor
        )


        cursor.execute(
            """
            SELECT

                post_id,

                user_id,

                text,

                timestamp,

                spam_score,

                duplicate_score,

                risk_score,

                risk_level,

                suspicious

            FROM analysis

            WHERE post_id = %s
            """,

            (
                post_id,
            )

        )


        result = cursor.fetchone()


        cursor.close()


        if result is None:

            return {

                "success": False,

                "message":
                    "Post analysis not found"

            }


        if result["timestamp"]:

            result["timestamp"] = (
                result["timestamp"]
                .isoformat()
            )


        return {

            "success": True,

            "analysis":
                result

        }


    finally:

        connection.close()


# ============================================================
# LIVE STATISTICS
# ============================================================

@app.get("/stats")
def get_stats():

    connection = get_connection()

    try:

        cursor = connection.cursor(
            cursor_factory=RealDictCursor
        )


        # ====================================================
        # USERS
        # ====================================================

        cursor.execute(
            """
            SELECT COUNT(*) AS count
            FROM users
            """
        )

        users = cursor.fetchone()["count"]


        # ====================================================
        # POSTS
        # ====================================================

        cursor.execute(
            """
            SELECT COUNT(*) AS count
            FROM posts
            """
        )

        posts = cursor.fetchone()["count"]


        # ====================================================
        # ANALYZED POSTS
        # ====================================================

        cursor.execute(
            """
            SELECT COUNT(*) AS count
            FROM analysis
            """
        )

        analyzed_posts = (
            cursor.fetchone()["count"]
        )


        # ====================================================
        # HIGH RISK
        # ====================================================

        cursor.execute(
            """
            SELECT COUNT(*) AS count
            FROM analysis
            WHERE UPPER(risk_level) = 'HIGH'
            """
        )

        high_risk = (
            cursor.fetchone()["count"]
        )


        # ====================================================
        # MEDIUM RISK
        # ====================================================

        cursor.execute(
            """
            SELECT COUNT(*) AS count
            FROM analysis
            WHERE UPPER(risk_level) = 'MEDIUM'
            """
        )

        medium_risk = (
            cursor.fetchone()["count"]
        )


        # ====================================================
        # LOW RISK
        # ====================================================

        cursor.execute(
            """
            SELECT COUNT(*) AS count
            FROM analysis
            WHERE UPPER(risk_level) = 'LOW'
            """
        )

        low_risk = (
            cursor.fetchone()["count"]
        )


        # ====================================================
        # SUSPICIOUS
        # ====================================================

        cursor.execute(
            """
            SELECT COUNT(*) AS count
            FROM analysis
            WHERE suspicious = TRUE
            """
        )

        suspicious = (
            cursor.fetchone()["count"]
        )


        cursor.close()


        return {

            "users":
                int(users),

            "posts":
                int(posts),

            "analyzed_posts":
                int(analyzed_posts),

            "suspicious_posts":
                int(suspicious),

            "high_risk":
                int(high_risk),

            "medium_risk":
                int(medium_risk),

            "low_risk":
                int(low_risk),

            "timestamp":
                datetime.now().isoformat()

        }


    finally:

        connection.close()