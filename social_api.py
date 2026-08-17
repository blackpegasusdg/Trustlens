from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import random

app = FastAPI(
    title="TrustLens Social Demo API",
    version="1.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# DATA MODELS
# ============================================================

class PostRequest(BaseModel):
    text: str


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "status": "online",
        "service": "TrustLens Social Demo API",
        "version": "1.0"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# ============================================================
# POST ANALYSIS
# ============================================================

@app.post("/posts")
def analyze_post(post: PostRequest):

    text = post.text.strip()

    if not text:

        return {
            "success": False,
            "message": "Post cannot be empty"
        }


    # --------------------------------------------------------
    # Basic demonstration analysis
    # --------------------------------------------------------

    lower_text = text.lower()


    # Spam indicators
    spam_words = [
        "buy now",
        "click here",
        "free money",
        "limited offer",
        "winner",
        "congratulations",
        "earn money",
        "visit link",
        "subscribe",
        "100% free"
    ]


    spam_matches = [
        word
        for word in spam_words
        if word in lower_text
    ]


    # Excessive repetition
    words = lower_text.split()

    repetition_score = 0

    if len(words) >= 5:

        unique_words = len(set(words))

        repetition_ratio = (
            unique_words / len(words)
        )

        if repetition_ratio < 0.5:
            repetition_score = 30


    # Excessive punctuation
    punctuation_count = sum(
        1
        for char in text
        if char in "!?"
    )


    punctuation_score = min(
        punctuation_count * 5,
        20
    )


    # Spam score
    spam_score = min(
        len(spam_matches) * 20
        + repetition_score
        + punctuation_score,
        100
    )


    # --------------------------------------------------------
    # Manipulation indicators
    # --------------------------------------------------------

    manipulation_words = [
        "everyone",
        "nobody",
        "always",
        "never",
        "guaranteed",
        "shocking",
        "must share",
        "urgent"
    ]


    manipulation_matches = [
        word
        for word in manipulation_words
        if word in lower_text
    ]


    manipulation_score = min(
        len(manipulation_matches) * 15,
        100
    )


    # --------------------------------------------------------
    # Risk calculation
    # --------------------------------------------------------

    risk_score = (
        spam_score * 0.6
        + manipulation_score * 0.4
    )


    if risk_score >= 70:

        risk_level = "HIGH"

    elif risk_score >= 40:

        risk_level = "MEDIUM"

    else:

        risk_level = "LOW"


    # Authenticity
    authenticity_score = round(
        100 - risk_score,
        2
    )


    # --------------------------------------------------------
    # Detection decision
    # --------------------------------------------------------

    suspicious = risk_score >= 50


    return {

        "success": True,

        "post": {
            "text": text,
            "timestamp": datetime.now().isoformat()
        },

        "risk_level": risk_level,

        "risk_score": round(
            risk_score,
            2
        ),

        "authenticity_score": authenticity_score,

        "spam_score": round(
            spam_score,
            2
        ),

        "manipulation_score": round(
            manipulation_score,
            2
        ),

        "coordination_score": 0,

        "user_behavior_score": 0,

        "detected_suspicious": suspicious,

        "evidence": {

            "spam_matches": spam_matches,

            "manipulation_matches":
                manipulation_matches,

            "repetition_score":
                repetition_score,

            "punctuation_score":
                punctuation_score
        }

    }


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000
    )