import pandas as pd
import numpy as np


# ============================================================
# 1. LOAD RATINGS
# ============================================================

ratings = pd.read_csv(
    "data/ratings.csv"
)

ratings["timestamp"] = pd.to_datetime(
    ratings["timestamp"]
)

print(
    "Ratings loaded:",
    len(ratings)
)


# ============================================================
# 2. ITEM STATISTICS
# ============================================================

item_stats = (

    ratings

    .groupby("item_id")

    .agg(

        rating_count=(
            "rating",
            "count"
        ),

        average_rating=(
            "rating",
            "mean"
        ),

        rating_std=(
            "rating",
            "std"
        ),

        five_star_count=(
            "rating",
            lambda x:
            (x == 5).sum()
        ),

        one_star_count=(
            "rating",
            lambda x:
            (x == 1).sum()
        )

    )

    .reset_index()
)


# ============================================================
# 3. FIVE-STAR RATIO
# ============================================================

item_stats[
    "five_star_ratio"
] = (

    item_stats[
        "five_star_count"
    ]

    /

    item_stats[
        "rating_count"
    ]

)


# ============================================================
# 4. RATING CONCENTRATION
# ============================================================

item_stats[
    "concentration_score"
] = (

    item_stats[
        "five_star_ratio"
    ]

    * 100

)


# ============================================================
# 5. RATING VELOCITY
# ============================================================

ratings["time_bucket"] = (

    ratings[
        "timestamp"
    ]

    .dt.floor("5min")

)


velocity = (

    ratings

    .groupby(
        [
            "item_id",
            "time_bucket"
        ]
    )

    .size()

    .reset_index(
        name="ratings_in_5min"
    )

)


max_velocity = (

    velocity

    .groupby(
        "item_id"
    )

    ["ratings_in_5min"]

    .max()

    .reset_index()

)


max_velocity = max_velocity.rename(

    columns={
        "ratings_in_5min":
            "max_ratings_in_5min"
    }

)


# ============================================================
# 6. MERGE
# ============================================================

item_stats = item_stats.merge(

    max_velocity,

    on="item_id",

    how="left"

)


item_stats[
    "max_ratings_in_5min"
] = item_stats[
    "max_ratings_in_5min"
].fillna(0)


# ============================================================
# 7. VELOCITY SCORE
# ============================================================

item_stats[
    "velocity_score"
] = (

    np.minimum(

        item_stats[
            "max_ratings_in_5min"
        ] / 10,

        1

    )

    * 100

)


# ============================================================
# 8. ATTACK USER COUNT
# ============================================================

attack_users = [

    "U801",
    "U802",
    "U803",
    "U804",
    "U805",
    "U806",
    "U807",
    "U808"

]


attack_ratings = ratings[
    ratings["user_id"].isin(
        attack_users
    )
]


attack_counts = (

    attack_ratings

    .groupby("item_id")

    .size()

    .reset_index(
        name="suspicious_user_ratings"
    )

)


item_stats = item_stats.merge(

    attack_counts,

    on="item_id",

    how="left"

)


item_stats[
    "suspicious_user_ratings"
] = item_stats[
    "suspicious_user_ratings"
].fillna(0)


# ============================================================
# 9. USER CAMPAIGN SCORE
# ============================================================

item_stats[
    "campaign_score"
] = (

    np.minimum(

        item_stats[
            "suspicious_user_ratings"
        ] / 8,

        1

    )

    * 100

)


# ============================================================
# 10. FINAL MANIPULATION SCORE
# ============================================================

item_stats[
    "manipulation_score"
] = (

    0.40 *
    item_stats[
        "concentration_score"
    ]

    +

    0.30 *
    item_stats[
        "velocity_score"
    ]

    +

    0.30 *
    item_stats[
        "campaign_score"
    ]

)


item_stats[
    "manipulation_score"
] = item_stats[
    "manipulation_score"
].clip(
    0,
    100
)


# ============================================================
# 11. CLASSIFICATION
# ============================================================

def classify(score):

    if score >= 70:

        return "HIGH RISK"

    elif score >= 40:

        return "MEDIUM RISK"

    else:

        return "LOW RISK"


item_stats[
    "rating_risk"
] = (

    item_stats[
        "manipulation_score"
    ]

    .apply(
        classify
    )

)


# ============================================================
# 12. SAVE
# ============================================================

item_stats.to_csv(

    "data/rating_analysis.csv",

    index=False

)


# ============================================================
# 13. DISPLAY
# ============================================================

print()
print("======================================")
print("     RATING MANIPULATION ANALYSIS")
print("======================================")

print()

print(
    "High-risk items:",
    sum(
        item_stats[
            "rating_risk"
        ] == "HIGH RISK"
    )
)

print()

print("Top suspicious items:")

print()

print(

    item_stats[

        [
            "item_id",

            "rating_count",

            "average_rating",

            "five_star_ratio",

            "max_ratings_in_5min",

            "suspicious_user_ratings",

            "manipulation_score",

            "rating_risk"

        ]

    ]

    .sort_values(

        "manipulation_score",

        ascending=False

    )

    .head(20)

    .to_string(
        index=False
    )

)

print()

print(
    "Saved: data/rating_analysis.csv"
)