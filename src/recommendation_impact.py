import pandas as pd


# ============================================================
# TRUSTLENS RECOMMENDATION IMPACT ANALYZER
# ============================================================


# ============================================================
# 1. LOAD DATA
# ============================================================

ratings = pd.read_csv(
    "data/ratings.csv"
)

trustlens = pd.read_csv(
    "data/trustlens_scores.csv"
)


print("Ratings loaded:", len(ratings))


# ============================================================
# 2. FIND HIGH-RISK USERS USING FINAL TRUSTLENS SCORE
# ============================================================

suspicious_users = trustlens.loc[

    trustlens["risk_level"] == "HIGH RISK",

    "user_id"

].tolist()


print()
print(
    "TrustLens HIGH RISK users:",
    len(suspicious_users)
)

print()

print(
    "Users:",
    suspicious_users
)


# ============================================================
# 3. RECOMMENDATION FUNCTION
# ============================================================

def calculate_ranking(ratings_data):

    if len(ratings_data) == 0:

        return pd.DataFrame(
            columns=[
                "item_id",
                "rating_count",
                "average_rating",
                "recommendation_score",
                "rank"
            ]
        )


    # --------------------------------------------------------
    # Overall average
    # --------------------------------------------------------

    global_average = (

        ratings_data["rating"].mean()

    )


    # --------------------------------------------------------
    # Item statistics
    # --------------------------------------------------------

    item_stats = (

        ratings_data

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


    # --------------------------------------------------------
    # Bayesian / weighted rating
    # --------------------------------------------------------

    k = 20


    item_stats[
        "recommendation_score"
    ] = (

        (

            item_stats[
                "rating_count"
            ]

            /

            (

                item_stats[
                    "rating_count"
                ]

                +

                k

            )

        )

        *

        item_stats[
            "average_rating"
        ]

        +

        (

            k

            /

            (

                item_stats[
                    "rating_count"
                ]

                +

                k

            )

        )

        *

        global_average

    )


    # --------------------------------------------------------
    # Ranking
    # --------------------------------------------------------

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


    return item_stats


# ============================================================
# 4. ORIGINAL RECOMMENDATIONS
# ============================================================

print()
print(
    "Calculating ORIGINAL recommendations..."
)


original = calculate_ranking(
    ratings
)


# ============================================================
# 5. REMOVE TRUSTLENS HIGH-RISK USERS
# ============================================================

print()
print(
    "Removing HIGH RISK users..."
)


clean_ratings = ratings[

    ~

    ratings[
        "user_id"
    ].isin(
        suspicious_users
    )

].copy()


print(
    "Original ratings:",
    len(ratings)
)

print(
    "Clean ratings:",
    len(clean_ratings)
)

print(
    "Suspicious ratings removed:",
    len(ratings) - len(clean_ratings)
)


# ============================================================
# 6. CLEAN RECOMMENDATIONS
# ============================================================

print()
print(
    "Calculating CLEAN recommendations..."
)


clean = calculate_ranking(
    clean_ratings
)


# ============================================================
# 7. MERGE RANKINGS
# ============================================================

comparison = original[

    [
        "item_id",
        "rank",
        "recommendation_score"
    ]

].rename(

    columns={

        "rank":
            "original_rank",

        "recommendation_score":
            "original_score"

    }

)


comparison = comparison.merge(

    clean[

        [
            "item_id",
            "rank",
            "recommendation_score"
        ]

    ].rename(

        columns={

            "rank":
                "clean_rank",

            "recommendation_score":
                "clean_score"

        }

    ),

    on="item_id",

    how="left"

)


# ============================================================
# 8. RANK CHANGE
# ============================================================

comparison[
    "rank_change"
] = (

    comparison[
        "clean_rank"
    ]

    -

    comparison[
        "original_rank"
    ]

)


comparison[
    "absolute_rank_change"
] = (

    comparison[
        "rank_change"
    ]

    .abs()

)


# ============================================================
# 9. SCORE CHANGE
# ============================================================

comparison[
    "score_change"
] = (

    comparison[
        "clean_score"
    ]

    -

    comparison[
        "original_score"
    ]

)


# ============================================================
# 10. BIGGEST IMPACT
# ============================================================

comparison = (

    comparison

    .sort_values(

        "absolute_rank_change",

        ascending=False

    )

)


# ============================================================
# 11. DISPLAY
# ============================================================

print()
print(
    "=========================================="
)

print(
    "     TRUSTLENS RECOMMENDATION IMPACT"
)

print(
    "=========================================="
)

print()

print(
    "HIGH RISK users removed:",
    len(suspicious_users)
)

print(
    "Ratings removed:",
    len(ratings)
    -
    len(clean_ratings)
)

print()

print(
    "Largest recommendation changes:"
)

print()

print(

    comparison[

        [

            "item_id",

            "original_rank",

            "clean_rank",

            "rank_change",

            "original_score",

            "clean_score",

            "score_change"

        ]

    ]

    .head(20)

    .to_string(
        index=False
    )

)


# ============================================================
# 12. ATTACK ITEM I100
# ============================================================

print()
print(
    "=========================================="
)

print(
    "       RATING ATTACK IMPACT"
)

print(
    "=========================================="
)

print()


attack_item = "I100"


attack_result = comparison[

    comparison[
        "item_id"
    ]

    ==

    attack_item

]


if len(attack_result) > 0:

    print(
        attack_result[
            [
                "item_id",
                "original_rank",
                "clean_rank",
                "rank_change",
                "original_score",
                "clean_score",
                "score_change"
            ]
        ].to_string(
            index=False
        )
    )

else:

    print(
        "I100 was not present in ranking."
    )


# ============================================================
# 13. SAVE
# ============================================================

comparison.to_csv(

    "data/recommendation_impact.csv",

    index=False

)


print()

print(
    "Saved:"
)

print(
    "data/recommendation_impact.csv"
)