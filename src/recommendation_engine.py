import pandas as pd
import numpy as np


# ============================================================
# TRUSTLENS RECOMMENDATION ENGINE
# ============================================================


# ============================================================
# 1. LOAD DATA
# ============================================================

ratings = pd.read_csv(
    "data/ratings.csv"
)

items = pd.read_csv(
    "data/items.csv"
)

print("Ratings loaded:", len(ratings))


# ============================================================
# 2. GLOBAL AVERAGE
# ============================================================

global_average = ratings["rating"].mean()

print(
    "Global average rating:",
    round(global_average, 3)
)


# ============================================================
# 3. CALCULATE ITEM STATISTICS
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
        )

    )

    .reset_index()

)


# ============================================================
# 4. WEIGHTED RECOMMENDATION SCORE
# ============================================================

k = 20

item_stats["recommendation_score"] = (

    (
        item_stats["rating_count"]
        /
        (
            item_stats["rating_count"]
            + k
        )
    )

    *

    item_stats["average_rating"]

    +

    (
        k
        /
        (
            item_stats["rating_count"]
            + k
        )
    )

    *

    global_average

)


# ============================================================
# 5. CREATE RANKING
# ============================================================

item_stats = (

    item_stats

    .sort_values(
        "recommendation_score",
        ascending=False
    )

    .reset_index(
        drop=True
    )

)


item_stats["rank"] = (

    item_stats.index + 1

)


# ============================================================
# 6. DISPLAY TOP ITEMS
# ============================================================

print()
print("==========================================")
print("       TRUSTLENS RECOMMENDATIONS")
print("==========================================")

print()

print(
    item_stats[
        [
            "rank",
            "item_id",
            "rating_count",
            "average_rating",
            "recommendation_score"
        ]
    ]

    .head(20)

    .to_string(
        index=False
    )
)


# ============================================================
# 7. SAVE
# ============================================================

item_stats.to_csv(

    "data/recommendation_ranking.csv",

    index=False

)


print()

print(
    "Saved: data/recommendation_ranking.csv"
)