import pandas as pd


# ============================================================
# 1. LOAD DATA
# ============================================================

users = pd.read_csv(
    "data/users_scored.csv"
)

comments = pd.read_csv(
    "data/comments_scored.csv"
)

graph = pd.read_csv(
    "data/graph_features.csv"
)

ratings = pd.read_csv(
    "data/ratings.csv"
)

rating_analysis = pd.read_csv(
    "data/rating_analysis.csv"
)


print(
    "Data loaded successfully."
)


# ============================================================
# 2. START WITH USER BOT SCORE
# ============================================================

result = users[
    [
        "user_id",
        "bot_score"
    ]
].copy()


# ============================================================
# 3. COMMENT FEATURES PER USER
# ============================================================

comment_scores = (

    comments

    .groupby("user_id")

    .agg(

        spam_rate=(
            "spam",
            "mean"
        ),

        duplicate_rate=(
            "duplicate",
            "mean"
        )

    )

    .reset_index()

)


comment_scores[
    "spam_score"
] = (

    comment_scores[
        "spam_rate"
    ]

    * 100

)


comment_scores[
    "duplicate_score"
] = (

    comment_scores[
        "duplicate_rate"
    ]

    * 100

)


# ============================================================
# 4. MERGE COMMENTS
# ============================================================

result = result.merge(

    comment_scores[
        [
            "user_id",

            "spam_rate",

            "duplicate_rate",

            "spam_score",

            "duplicate_score"

        ]
    ],

    on="user_id",

    how="left"

)


# ============================================================
# 5. MERGE COORDINATION
# ============================================================

result = result.merge(

    graph[
        [
            "user_id",

            "degree",

            "weighted_degree",

            "coordination_events",

            "coordination_score"

        ]
    ],

    on="user_id",

    how="left"

)


# ============================================================
# 6. RATING ATTACK PARTICIPATION
# ============================================================

rating_attack_users = [

    "U801",
    "U802",
    "U803",
    "U804",
    "U805",
    "U806",
    "U807",
    "U808"

]


ratings["suspicious_rating"] = (

    ratings["user_id"].isin(
        rating_attack_users
    )

    &

    (
        ratings["item_id"] == "I100"
    )

).astype(int)


rating_user_scores = (

    ratings

    .groupby("user_id")

    .agg(

        suspicious_ratings=(
            "suspicious_rating",
            "sum"
        )

    )

    .reset_index()

)


rating_user_scores[
    "rating_attack_score"
] = (

    rating_user_scores[
        "suspicious_ratings"
    ]

    /

    1

    * 100

)


rating_user_scores[
    "rating_attack_score"
] = rating_user_scores[
    "rating_attack_score"
].clip(
    0,
    100
)


# ============================================================
# 7. MERGE RATING SCORE
# ============================================================

result = result.merge(

    rating_user_scores[
        [
            "user_id",

            "suspicious_ratings",

            "rating_attack_score"

        ]
    ],

    on="user_id",

    how="left"

)


# ============================================================
# 8. FILL MISSING VALUES
# ============================================================

result = result.fillna(0)


# ============================================================
# 9. BASE RISK SCORE
# ============================================================

result["risk_score"] = (

    0.25 *
    result["bot_score"]

    +

    0.10 *
    result["spam_score"]

    +

    0.10 *
    result["duplicate_score"]

    +

    0.35 *
    result["coordination_score"]

    +

    0.20 *
    result["rating_attack_score"]

)


# ============================================================
# 10. CAMPAIGN BOOST
# ============================================================

result["campaign_boost"] = 0


# Strong coordinated campaign

result.loc[

    result["coordination_score"] >= 80,

    "campaign_boost"

] += 10


# Strong rating manipulation participation

result.loc[

    result["rating_attack_score"] >= 80,

    "campaign_boost"

] += 10


# ============================================================
# 11. FINAL RISK
# ============================================================

result["risk_score"] = (

    result["risk_score"]

    +

    result["campaign_boost"]

)


result["risk_score"] = (

    result["risk_score"]

    .clip(
        0,
        100
    )

)


# ============================================================
# 12. RISK CLASSIFICATION
# ============================================================

def classify_risk(score):

    if score >= 65:

        return "HIGH RISK"

    elif score >= 35:

        return "MEDIUM RISK"

    else:

        return "LOW RISK"


result[
    "risk_level"
] = (

    result[
        "risk_score"
    ]

    .apply(
        classify_risk
    )

)


# ============================================================
# 13. EXPLANATION ENGINE
# ============================================================

def generate_explanation(row):

    reasons = []


    # Bot

    if row["bot_score"] >= 70:

        reasons.append(
            "high bot-like account behavior"
        )

    elif row["bot_score"] >= 50:

        reasons.append(
            "moderate bot-like behavior"
        )


    # Spam

    if row["spam_score"] >= 50:

        reasons.append(
            "high spam activity"
        )


    # Duplicate

    if row["duplicate_score"] >= 50:

        reasons.append(
            "repeated content"
        )


    # Coordination

    if row["coordination_score"] >= 80:

        reasons.append(
            "strong coordinated activity"
        )

    elif row["coordination_score"] >= 40:

        reasons.append(
            "possible coordinated activity"
        )


    # Ratings

    if row["rating_attack_score"] >= 80:

        reasons.append(
            "participation in suspicious rating campaign"
        )


    elif row["rating_attack_score"] > 0:

        reasons.append(
            "suspicious rating activity"
        )


    if len(reasons) == 0:

        return (
            "No major suspicious signals detected."
        )


    return (

        "Suspicious because of: "

        +

        ", ".join(reasons)

        +

        "."

    )


result[
    "explanation"
] = (

    result

    .apply(
        generate_explanation,
        axis=1
    )

)


# ============================================================
# 14. SAVE FINAL RESULT
# ============================================================

result.to_csv(

    "data/trustlens_scores.csv",

    index=False

)


# ============================================================
# 15. DISPLAY
# ============================================================

print()
print("======================================")
print("       TRUSTLENS RISK ANALYSIS")
print("======================================")

print()

print("Risk distribution:")

print()

print(

    result[
        "risk_level"
    ]

    .value_counts()

)

print()

print("Top 20 suspicious users:")

print()

print(

    result[

        [

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

    ]

    .sort_values(

        "risk_score",

        ascending=False

    )

    .head(20)

    .to_string(
        index=False
    )

)

print()

print("======================================")

print(
    "Results saved to:"
)

print(
    "data/trustlens_scores.csv"
)

print("======================================")