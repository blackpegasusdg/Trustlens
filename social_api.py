import os
import re
import uuid
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from sqlalchemy import (
    create_engine,
    Column,
    String,
    Text,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
)
from sqlalchemy.orm import (
    declarative_base,
    sessionmaker,
    relationship,
)


# ============================================================
# CONFIGURATION
# ============================================================

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Local development fallback.
    # Render should use PostgreSQL through DATABASE_URL.
    DATABASE_URL = "sqlite:///./trustlens.db"


# Render/Postgres sometimes provides postgres://
# while SQLAlchemy expects postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgres://",
        "postgresql://",
        1
    )


# ============================================================
# DATABASE
# ============================================================

connect_args = {}

if DATABASE_URL.startswith("sqlite"):
    connect_args = {
        "check_same_thread": False
    }


engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


Base = declarative_base()


# ============================================================
# DATABASE MODELS
# ============================================================

class Post(Base):

    __tablename__ = "posts"

    id = Column(
        String,
        primary_key=True,
        index=True
    )

    text = Column(
        Text,
        nullable=False
    )

    user_id = Column(
        String,
        nullable=True,
        index=True
    )

    timestamp = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    comments = relationship(
        "Comment",
        back_populates="post",
        cascade="all, delete-orphan"
    )

    analysis = relationship(
        "PostAnalysis",
        back_populates="post",
        uselist=False,
        cascade="all, delete-orphan"
    )


class Comment(Base):

    __tablename__ = "comments"

    id = Column(
        String,
        primary_key=True,
        index=True
    )

    post_id = Column(
        String,
        ForeignKey("posts.id"),
        nullable=False,
        index=True
    )

    user_id = Column(
        String,
        nullable=True,
        index=True
    )

    text = Column(
        Text,
        nullable=False
    )

    timestamp = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    post = relationship(
        "Post",
        back_populates="comments"
    )

    analysis = relationship(
        "CommentAnalysis",
        back_populates="comment",
        uselist=False,
        cascade="all, delete-orphan"
    )


class PostAnalysis(Base):

    __tablename__ = "post_analysis"

    id = Column(
        String,
        primary_key=True,
        index=True
    )

    post_id = Column(
        String,
        ForeignKey("posts.id"),
        nullable=False,
        unique=True,
        index=True
    )

    risk_level = Column(
        String,
        nullable=False
    )

    risk_score = Column(
        Float,
        nullable=False
    )

    authenticity_score = Column(
        Float,
        nullable=False
    )

    spam_score = Column(
        Float,
        nullable=False
    )

    manipulation_score = Column(
        Float,
        nullable=False
    )

    coordination_score = Column(
        Float,
        default=0
    )

    user_behavior_score = Column(
        Float,
        default=0
    )

    detected_suspicious = Column(
        Boolean,
        default=False
    )

    evidence = Column(
        JSON,
        nullable=True
    )

    analyzed_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    post = relationship(
        "Post",
        back_populates="analysis"
    )


class CommentAnalysis(Base):

    __tablename__ = "comment_analysis"

    id = Column(
        String,
        primary_key=True,
        index=True
    )

    comment_id = Column(
        String,
        ForeignKey("comments.id"),
        nullable=False,
        unique=True,
        index=True
    )

    risk_level = Column(
        String,
        nullable=False
    )

    risk_score = Column(
        Float,
        nullable=False
    )

    authenticity_score = Column(
        Float,
        nullable=False
    )

    spam_score = Column(
        Float,
        nullable=False
    )

    manipulation_score = Column(
        Float,
        nullable=False
    )

    duplicate_score = Column(
        Float,
        default=0
    )

    detected_suspicious = Column(
        Boolean,
        default=False
    )

    evidence = Column(
        JSON,
        nullable=True
    )

    analyzed_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    comment = relationship(
        "Comment",
        back_populates="analysis"
    )


# ============================================================
# CREATE TABLES
# ============================================================

Base.metadata.create_all(
    bind=engine
)


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(
    title="TrustLens Social Platform API",
    version="2.0"
)


# ============================================================
# CORS
# ============================================================

frontend_url = os.getenv(
    "FRONTEND_URL"
)

allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

if frontend_url:
    allowed_origins.append(
        frontend_url
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST MODELS
# ============================================================

class PostRequest(BaseModel):

    text: str

    user_id: str | None = None


class CommentRequest(BaseModel):

    post_id: str

    text: str

    user_id: str | None = None


# ============================================================
# TRUSTLENS ANALYSIS ENGINE
# ============================================================

def analyze_text(text: str):

    text = text.strip()

    if not text:
        raise ValueError(
            "Text cannot be empty"
        )

    lower_text = text.lower()


    # --------------------------------------------------------
    # SPAM
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # REPETITION
    # --------------------------------------------------------

    words = lower_text.split()

    repetition_score = 0

    if len(words) >= 5:

        unique_words = len(
            set(words)
        )

        repetition_ratio = (
            unique_words /
            len(words)
        )

        if repetition_ratio < 0.5:
            repetition_score = 30


    # --------------------------------------------------------
    # PUNCTUATION
    # --------------------------------------------------------

    punctuation_count = sum(
        1
        for char in text
        if char in "!?"
    )

    punctuation_score = min(
        punctuation_count * 5,
        20
    )


    # --------------------------------------------------------
    # SPAM SCORE
    # --------------------------------------------------------

    spam_score = min(
        len(spam_matches) * 20
        + repetition_score
        + punctuation_score,
        100
    )


    # --------------------------------------------------------
    # MANIPULATION
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
    # RISK
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


    authenticity_score = round(
        100 - risk_score,
        2
    )

    suspicious = (
        risk_score >= 50
    )


    return {

        "risk_level":
            risk_level,

        "risk_score":
            round(
                risk_score,
                2
            ),

        "authenticity_score":
            authenticity_score,

        "spam_score":
            round(
                spam_score,
                2
            ),

        "manipulation_score":
            round(
                manipulation_score,
                2
            ),

        "coordination_score":
            0,

        "user_behavior_score":
            0,

        "detected_suspicious":
            suspicious,

        "evidence": {

            "spam_matches":
                spam_matches,

            "manipulation_matches":
                manipulation_matches,

            "repetition_score":
                repetition_score,

            "punctuation_score":
                punctuation_score
        }
    }


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "status": "online",
        "service": "TrustLens Social Platform API",
        "version": "2.0",
        "database": (
            "postgresql"
            if DATABASE_URL.startswith("postgresql")
            else "sqlite"
        )
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():

    db = SessionLocal()

    try:

        db.execute(
            __import__(
                "sqlalchemy"
            ).text(
                "SELECT 1"
            )
        )

        database_status = "connected"

    except Exception as exc:

        database_status = str(exc)

    finally:

        db.close()


    return {
        "status": "healthy",
        "database": database_status
    }


# ============================================================
# CREATE POST
# ============================================================

@app.post("/posts")
def create_post(post: PostRequest):

    text = post.text.strip()

    if not text:

        return {
            "success": False,
            "message": "Post cannot be empty"
        }


    analysis = analyze_text(
        text
    )


    post_id = str(
        uuid.uuid4()
    )

    timestamp = datetime.now(
        timezone.utc
    )


    db = SessionLocal()

    try:

        new_post = Post(

            id=post_id,

            text=text,

            user_id=post.user_id,

            timestamp=timestamp
        )

        db.add(
            new_post
        )


        post_analysis = PostAnalysis(

            id=str(
                uuid.uuid4()
            ),

            post_id=post_id,

            risk_level=
                analysis["risk_level"],

            risk_score=
                analysis["risk_score"],

            authenticity_score=
                analysis["authenticity_score"],

            spam_score=
                analysis["spam_score"],

            manipulation_score=
                analysis["manipulation_score"],

            coordination_score=
                analysis["coordination_score"],

            user_behavior_score=
                analysis["user_behavior_score"],

            detected_suspicious=
                analysis["detected_suspicious"],

            evidence=
                analysis["evidence"],

            analyzed_at=timestamp
        )

        db.add(
            post_analysis
        )

        db.commit()


        return {

            "success": True,

            "post": {

                "id":
                    post_id,

                "text":
                    text,

                "user_id":
                    post.user_id,

                "timestamp":
                    timestamp.isoformat()
            },

            **analysis
        }


    except Exception:

        db.rollback()

        raise


    finally:

        db.close()


# ============================================================
# GET ALL POSTS
# ============================================================

@app.get("/posts")
def get_posts():

    db = SessionLocal()

    try:

        posts = (
            db.query(Post)
            .order_by(
                Post.timestamp.desc()
            )
            .all()
        )

        result = []

        for post in posts:

            analysis = post.analysis

            result.append({

                "id":
                    post.id,

                "text":
                    post.text,

                "user_id":
                    post.user_id,

                "timestamp":
                    post.timestamp.isoformat(),

                "risk_level":
                    analysis.risk_level
                    if analysis
                    else "UNKNOWN",

                "risk_score":
                    analysis.risk_score
                    if analysis
                    else 0,

                "authenticity_score":
                    analysis.authenticity_score
                    if analysis
                    else 0,

                "spam_score":
                    analysis.spam_score
                    if analysis
                    else 0,

                "manipulation_score":
                    analysis.manipulation_score
                    if analysis
                    else 0,

                "detected_suspicious":
                    analysis.detected_suspicious
                    if analysis
                    else False,

                "comment_count":
                    len(post.comments)
            })

        return result

    finally:

        db.close()


# ============================================================
# GET SINGLE POST
# ============================================================

@app.get("/posts/{post_id}")
def get_post(post_id: str):

    db = SessionLocal()

    try:

        post = (
            db.query(Post)
            .filter(
                Post.id == post_id
            )
            .first()
        )

        if not post:

            raise HTTPException(
                status_code=404,
                detail="Post not found"
            )


        analysis = post.analysis


        return {

            "id":
                post.id,

            "text":
                post.text,

            "user_id":
                post.user_id,

            "timestamp":
                post.timestamp.isoformat(),

            "risk_level":
                analysis.risk_level
                if analysis
                else "UNKNOWN",

            "risk_score":
                analysis.risk_score
                if analysis
                else 0,

            "authenticity_score":
                analysis.authenticity_score
                if analysis
                else 0,

            "spam_score":
                analysis.spam_score
                if analysis
                else 0,

            "manipulation_score":
                analysis.manipulation_score
                if analysis
                else 0,

            "detected_suspicious":
                analysis.detected_suspicious
                if analysis
                else False
        }

    finally:

        db.close()


# ============================================================
# CREATE COMMENT
# ============================================================

@app.post("/comments")
def create_comment(
    comment: CommentRequest
):

    text = comment.text.strip()

    if not text:

        return {
            "success": False,
            "message": "Comment cannot be empty"
        }


    db = SessionLocal()

    try:

        post = (
            db.query(Post)
            .filter(
                Post.id ==
                comment.post_id
            )
            .first()
        )

        if not post:

            raise HTTPException(
                status_code=404,
                detail="Post not found"
            )


        # ----------------------------------------------------
        # Analyze comment
        # ----------------------------------------------------

        analysis = analyze_text(
            text
        )


        # ----------------------------------------------------
        # Basic duplicate detection
        # ----------------------------------------------------

        existing_comments = (
            db.query(Comment)
            .filter(
                Comment.post_id ==
                comment.post_id
            )
            .all()
        )


        normalized_new = re.sub(
            r"\s+",
            " ",
            text.lower()
        ).strip()


        duplicate_score = 0


        for existing in existing_comments:

            normalized_existing = re.sub(
                r"\s+",
                " ",
                existing.text.lower()
            ).strip()


            if (
                normalized_existing ==
                normalized_new
            ):

                duplicate_score = 100

                break


        # ----------------------------------------------------
        # Combine duplicate with risk
        # ----------------------------------------------------

        final_risk = max(
            analysis["risk_score"],
            duplicate_score
        )


        if final_risk >= 70:

            risk_level = "HIGH"

        elif final_risk >= 40:

            risk_level = "MEDIUM"

        else:

            risk_level = "LOW"


        suspicious = (
            final_risk >= 50
        )


        comment_id = str(
            uuid.uuid4()
        )

        timestamp = datetime.now(
            timezone.utc
        )


        # ----------------------------------------------------
        # Save comment
        # ----------------------------------------------------

        new_comment = Comment(

            id=comment_id,

            post_id=
                comment.post_id,

            user_id=
                comment.user_id,

            text=text,

            timestamp=timestamp
        )

        db.add(
            new_comment
        )


        # ----------------------------------------------------
        # Save analysis
        # ----------------------------------------------------

        comment_analysis = CommentAnalysis(

            id=str(
                uuid.uuid4()
            ),

            comment_id=
                comment_id,

            risk_level=
                risk_level,

            risk_score=
                round(
                    final_risk,
                    2
                ),

            authenticity_score=
                round(
                    100 - final_risk,
                    2
                ),

            spam_score=
                analysis["spam_score"],

            manipulation_score=
                analysis[
                    "manipulation_score"
                ],

            duplicate_score=
                duplicate_score,

            detected_suspicious=
                suspicious,

            evidence={
                **analysis["evidence"],
                "duplicate":
                    duplicate_score > 0
            },

            analyzed_at=
                timestamp
        )

        db.add(
            comment_analysis
        )

        db.commit()


        return {

            "success": True,

            "comment": {

                "id":
                    comment_id,

                "post_id":
                    comment.post_id,

                "user_id":
                    comment.user_id,

                "text":
                    text,

                "timestamp":
                    timestamp.isoformat()
            },

            "risk_level":
                risk_level,

            "risk_score":
                round(
                    final_risk,
                    2
                ),

            "authenticity_score":
                round(
                    100 - final_risk,
                    2
                ),

            "spam_score":
                analysis["spam_score"],

            "manipulation_score":
                analysis[
                    "manipulation_score"
                ],

            "duplicate_score":
                duplicate_score,

            "detected_suspicious":
                suspicious,

            "evidence":
                {
                    **analysis["evidence"],
                    "duplicate":
                        duplicate_score > 0
                }
        }


    except HTTPException:

        db.rollback()

        raise


    except Exception:

        db.rollback()

        raise


    finally:

        db.close()


# ============================================================
# GET COMMENTS FOR A POST
# ============================================================

@app.get("/posts/{post_id}/comments")
def get_post_comments(
    post_id: str
):

    db = SessionLocal()

    try:

        post = (
            db.query(Post)
            .filter(
                Post.id == post_id
            )
            .first()
        )

        if not post:

            raise HTTPException(
                status_code=404,
                detail="Post not found"
            )


        comments = (
            db.query(Comment)
            .filter(
                Comment.post_id ==
                post_id
            )
            .order_by(
                Comment.timestamp.asc()
            )
            .all()
        )


        result = []


        for comment in comments:

            analysis = (
                comment.analysis
            )


            result.append({

                "id":
                    comment.id,

                "post_id":
                    comment.post_id,

                "user_id":
                    comment.user_id,

                "text":
                    comment.text,

                "timestamp":
                    comment.timestamp.isoformat(),

                "risk_level":
                    analysis.risk_level
                    if analysis
                    else "UNKNOWN",

                "risk_score":
                    analysis.risk_score
                    if analysis
                    else 0,

                "authenticity_score":
                    analysis.authenticity_score
                    if analysis
                    else 0,

                "spam_score":
                    analysis.spam_score
                    if analysis
                    else 0,

                "duplicate_score":
                    analysis.duplicate_score
                    if analysis
                    else 0,

                "detected_suspicious":
                    analysis.detected_suspicious
                    if analysis
                    else False
            })


        return result


    finally:

        db.close()


# ============================================================
# GLOBAL TRUSTLENS ANALYSIS
# ============================================================

@app.get("/analysis")
def get_analysis():

    db = SessionLocal()

    try:

        records = (
            db.query(
                PostAnalysis,
                Post
            )
            .join(
                Post,
                Post.id ==
                PostAnalysis.post_id
            )
            .order_by(
                PostAnalysis.analyzed_at.desc()
            )
            .all()
        )


        result = []


        for analysis, post in records:

            result.append({

                "post_id":
                    post.id,

                "user_id":
                    post.user_id,

                "text":
                    post.text,

                "timestamp":
                    post.timestamp.isoformat(),

                "risk_level":
                    analysis.risk_level,

                "risk_score":
                    analysis.risk_score,

                "authenticity_score":
                    analysis.authenticity_score,

                "spam_score":
                    analysis.spam_score,

                "manipulation_score":
                    analysis.manipulation_score,

                "coordination_score":
                    analysis.coordination_score,

                "user_behavior_score":
                    analysis.user_behavior_score,

                "suspicious":
                    analysis.detected_suspicious,

                "is_suspicious":
                    analysis.detected_suspicious,

                "flagged":
                    analysis.detected_suspicious,

                "analysis_timestamp":
                    analysis.analyzed_at.isoformat(),

                "evidence":
                    analysis.evidence
            })


        return result


    finally:

        db.close()


# ============================================================
# COMMENT ANALYSIS
# ============================================================

@app.get("/comment-analysis")
def get_comment_analysis():

    db = SessionLocal()

    try:

        records = (
            db.query(
                CommentAnalysis,
                Comment
            )
            .join(
                Comment,
                Comment.id ==
                CommentAnalysis.comment_id
            )
            .order_by(
                CommentAnalysis.analyzed_at.desc()
            )
            .all()
        )


        result = []


        for analysis, comment in records:

            result.append({

                "comment_id":
                    comment.id,

                "post_id":
                    comment.post_id,

                "user_id":
                    comment.user_id,

                "text":
                    comment.text,

                "timestamp":
                    comment.timestamp.isoformat(),

                "risk_level":
                    analysis.risk_level,

                "risk_score":
                    analysis.risk_score,

                "authenticity_score":
                    analysis.authenticity_score,

                "spam_score":
                    analysis.spam_score,

                "duplicate_score":
                    analysis.duplicate_score,

                "manipulation_score":
                    analysis.manipulation_score,

                "suspicious":
                    analysis.detected_suspicious,

                "is_suspicious":
                    analysis.detected_suspicious,

                "flagged":
                    analysis.detected_suspicious,

                "analysis_timestamp":
                    analysis.analyzed_at.isoformat(),

                "evidence":
                    analysis.evidence
            })


        return result


    finally:

        db.close()


# ============================================================
# DATABASE STATISTICS
# ============================================================

@app.get("/stats")
def get_stats():

    db = SessionLocal()

    try:

        posts_count = (
            db.query(Post)
            .count()
        )

        comments_count = (
            db.query(Comment)
            .count()
        )

        suspicious_posts = (
            db.query(PostAnalysis)
            .filter(
                PostAnalysis.detected_suspicious
                == True
            )
            .count()
        )

        suspicious_comments = (
            db.query(CommentAnalysis)
            .filter(
                CommentAnalysis.detected_suspicious
                == True
            )
            .count()
        )


        return {

            "posts":
                posts_count,

            "comments":
                comments_count,

            "analyzed_posts":
                db.query(
                    PostAnalysis
                ).count(),

            "analyzed_comments":
                db.query(
                    CommentAnalysis
                ).count(),

            "suspicious_posts":
                suspicious_posts,

            "suspicious_comments":
                suspicious_comments
        }


    finally:

        db.close()


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(
            os.getenv(
                "PORT",
                "8000"
            )
        )
    )