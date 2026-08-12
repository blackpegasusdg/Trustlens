import pandas as pd
import numpy as np
import os


# ============================================================
# TRUSTLENS
# IMPROVED FAKE RATING ATTACK DETECTOR
# ============================================================

print("=" * 70)
print("          TRUSTLENS IMPROVED RATING DETECTOR")
print("=" * 70)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

ATTACK_DIR = os.path.join(
    BASE_DIR,
    "data",
    "simulated_attacks"
)

RESULT_DIR = os.path.join(
    BASE_DIR,
    "data",
    "attack_results",
    "rating_attack"
)

os.makedirs(
    RESULT_DIR,
    exist_ok=True
)


ratings_file = os.path.join(
    ATTACK_DIR,
    "ratings_attacked.csv"
)

injected_file = os.path.join(
    ATTACK_DIR,
    "injected_ratings.csv"
)


# ============================================================
# CHECK FILES
# ============================================================

print("\nChecking attack dataset...")


if not os.path.exists(ratings_file):

    print(
        "ERROR: ratings_attacked.csv not found."
    )

    print(ratings_file)

    raise SystemExit


if not os.path.exists(injected_file):

    print(
        "ERROR: injected_ratings.csv not found."
    )

    print(injected_file)

    raise SystemExit


print(
    "Attack dataset found successfully."
)


# ============================================================
# LOAD
# ============================================================

print(
    "\nLoading rating dataset..."
)


ratings = pd.read_csv(
    ratings_file
)

injected = pd.read_csv(
    injected_file
)


print(
    "Dataset loaded successfully."
)


print(
    "\nRatings:",
    len(ratings)
)

print(
    "Known fake ratings:",
    len(injected)
)


# ============================================================
# COLUMN DETECTION
# ============================================================

def find_column(df, names):

    for name in names:

        if name in df.columns:

            return name

    return None


user_col = find_column(
    ratings,
    [
        "user_id",
        "userid",
        "user"
    ]
)

item_col = find_column(
    ratings,
    [
        "item_id",
        "item",
        "product_id"
    ]
)

rating_col = find_column(
    ratings,
    [
        "rating",
        "score",
        "stars",
        "value"
    ]
)

rating_id_col = find_column(
    ratings,
    [
        "rating_id",
        "id"
    ]
)


print("\nDetected columns:")

print(
    "User   :",
    user_col
)

print(
    "Item   :",
    item_col
)

print(
    "Rating :",
    rating_col
)

print(
    "ID     :",
    rating_id_col
)


if user_col is None:
    raise ValueError(
        "User column not found."
    )

if item_col is None:
    raise ValueError(
        "Item column not found."
    )

if rating_col is None:
    raise ValueError(
        "Rating column not found."
    )


# ============================================================
# CLEAN
# ============================================================

ratings[rating_col] = pd.to_numeric(
    ratings[rating_col],
    errors="coerce"
)

ratings = ratings.dropna(
    subset=[
        user_col,
        item_col,
        rating_col
    ]
).copy()


# ============================================================
# BUILD GROUND TRUTH FIRST
# ============================================================

print(
    "\n[1/9] Building attack ground truth..."
)


ratings["is_real_attack"] = False


# ------------------------------------------------------------
# METHOD 1:
# Exact rating ID matching
# ------------------------------------------------------------

if (
    rating_id_col is not None
    and rating_id_col in injected.columns
):

    injected_ids = set(
        injected[
            rating_id_col
        ]
        .astype(str)
    )

    ratings["is_real_attack"] = (
        ratings[
            rating_id_col
        ]
        .astype(str)
        .isin(
            injected_ids
        )
    )


# ------------------------------------------------------------
# METHOD 2:
# Match user + item + rating
# ------------------------------------------------------------

if not ratings["is_real_attack"].any():

    injected_keys = set(

        zip(

            injected[user_col].astype(str),

            injected[item_col].astype(str),

            injected[rating_col].astype(float)

        )

    )


    ratings["is_real_attack"] = [

        (
            str(u),
            str(i),
            float(r)
        )

        in injected_keys

        for u, i, r in zip(

            ratings[user_col],

            ratings[item_col],

            ratings[rating_col]

        )

    ]


print(
    "Ground-truth attacks found:",
    int(
        ratings[
            "is_real_attack"
        ].sum()
    )
)


# ============================================================
# EXTREME RATINGS
# ============================================================

print(
    "[2/9] Detecting extreme ratings..."
)


ratings[
    "extreme_rating_score"
] = 0


ratings.loc[
    ratings[rating_col] >= 5,
    "extreme_rating_score"
] = 25


ratings.loc[
    ratings[rating_col] <= 1,
    "extreme_rating_score"
] = 25


# ============================================================
# USER BEHAVIOUR
# ============================================================

print(
    "[3/9] Analyzing user behaviour..."
)


user_stats = (

    ratings
    .groupby(user_col)[rating_col]
    .agg(
        [
            "count",
            "mean",
            "std"
        ]
    )

)


ratings[
    "user_rating_count"
] = (

    ratings[
        user_col
    ]
    .map(
        user_stats["count"]
    )
    .fillna(0)

)


ratings[
    "user_rating_std"
] = (

    ratings[
        user_col
    ]
    .map(
        user_stats["std"]
    )
    .fillna(0)

)


extreme_mask = (

    (ratings[rating_col] >= 5)

    |

    (ratings[rating_col] <= 1)

)


extreme_user_counts = (

    ratings[
        extreme_mask
    ]
    .groupby(user_col)
    .size()

)


ratings[
    "user_extreme_ratio"
] = (

    ratings[
        user_col
    ]
    .map(
        extreme_user_counts
    )
    .fillna(0)

    /

    ratings[
        "user_rating_count"
    ].replace(
        0,
        1
    )

)


ratings[
    "user_behavior_score"
] = 0


ratings.loc[
    ratings[
        "user_extreme_ratio"
    ] >= 0.90,
    "user_behavior_score"
] = 35


ratings.loc[
    (
        ratings[
            "user_extreme_ratio"
        ] >= 0.70
    )
    &
    (
        ratings[
            "user_extreme_ratio"
        ] < 0.90
    ),
    "user_behavior_score"
] = 25


ratings.loc[
    (
        ratings[
            "user_extreme_ratio"
        ] >= 0.50
    )
    &
    (
        ratings[
            "user_extreme_ratio"
        ] < 0.70
    ),
    "user_behavior_score"
] = 15


# ============================================================
# ITEM ANALYSIS
# ============================================================

print(
    "[4/9] Analyzing item targeting..."
)


item_stats = (

    ratings
    .groupby(item_col)[rating_col]
    .agg(
        [
            "count",
            "mean",
            "std"
        ]
    )

)


ratings[
    "item_rating_count"
] = (

    ratings[
        item_col
    ]
    .map(
        item_stats["count"]
    )
    .fillna(0)

)


ratings[
    "item_average_rating"
] = (

    ratings[
        item_col
    ]
    .map(
        item_stats["mean"]
    )
    .fillna(
        ratings[
            rating_col
        ].mean()
    )

)


item_extreme_counts = (

    ratings[
        extreme_mask
    ]
    .groupby(item_col)
    .size()

)


ratings[
    "item_extreme_count"
] = (

    ratings[
        item_col
    ]
    .map(
        item_extreme_counts
    )
    .fillna(0)

)


ratings[
    "item_extreme_ratio"
] = (

    ratings[
        "item_extreme_count"
    ]

    /

    ratings[
        "item_rating_count"
    ].replace(
        0,
        1
    )

)


ratings[
    "item_targeting_score"
] = 0


ratings.loc[
    ratings[
        "item_extreme_ratio"
    ] >= 0.80,
    "item_targeting_score"
] = 35


ratings.loc[
    (
        ratings[
            "item_extreme_ratio"
        ] >= 0.60
    )
    &
    (
        ratings[
            "item_extreme_ratio"
        ] < 0.80
    ),
    "item_targeting_score"
] = 25


ratings.loc[
    (
        ratings[
            "item_extreme_ratio"
        ] >= 0.40
    )
    &
    (
        ratings[
            "item_extreme_ratio"
        ] < 0.60
    ),
    "item_targeting_score"
] = 15


# ============================================================
# USER-ITEM DUPLICATES
# ============================================================

print(
    "[5/9] Detecting repeated user-item ratings..."
)


user_item_counts = (

    ratings
    .groupby(
        [
            user_col,
            item_col
        ]
    )
    .size()

)


index = pd.MultiIndex.from_frame(

    ratings[
        [
            user_col,
            item_col
        ]
    ]

)


ratings[
    "user_item_rating_count"
] = (

    user_item_counts
    .reindex(index)
    .fillna(1)
    .values

)


ratings[
    "duplicate_rating_score"
] = 0


ratings.loc[
    ratings[
        "user_item_rating_count"
    ] >= 2,
    "duplicate_rating_score"
] = 25


# ============================================================
# COORDINATION
# ============================================================

print(
    "[6/9] Detecting coordinated rating groups..."
)


coordination = (

    ratings
    .groupby(
        [
            item_col,
            rating_col
        ]
    )[user_col]
    .nunique()

)


coord_index = pd.MultiIndex.from_frame(

    ratings[
        [
            item_col,
            rating_col
        ]
    ]

)


ratings[
    "coordinated_users"
] = (

    coordination
    .reindex(
        coord_index
    )
    .fillna(1)
    .values

)


ratings[
    "coordination_score"
] = 0


ratings.loc[
    ratings[
        "coordinated_users"
    ] >= 15,
    "coordination_score"
] = 50


ratings.loc[
    (
        ratings[
            "coordinated_users"
        ] >= 10
    )
    &
    (
        ratings[
            "coordinated_users"
        ] < 15
    ),
    "coordination_score"
] = 40


ratings.loc[
    (
        ratings[
            "coordinated_users"
        ] >= 7
    )
    &
    (
        ratings[
            "coordinated_users"
        ] < 10
    ),
    "coordination_score"
] = 30


ratings.loc[
    (
        ratings[
            "coordinated_users"
        ] >= 5
    )
    &
    (
        ratings[
            "coordinated_users"
        ] < 7
    ),
    "coordination_score"
] = 20


ratings.loc[
    (
        ratings[
            "coordinated_users"
        ] >= 3
    )
    &
    (
        ratings[
            "coordinated_users"
        ] < 5
    ),
    "coordination_score"
] = 10


# ============================================================
# ATTACK-SPECIFIC EVIDENCE
# ============================================================

print(
    "[7/9] Applying attack-specific evidence..."
)


ratings[
    "attack_pattern_boost"
] = 0


# If an extreme rating is part of a coordinated
# group of >= 5 users, this is strong evidence.

ratings.loc[
    (
        ratings[
            "extreme_rating_score"
        ] >= 25
    )
    &
    (
        ratings[
            "coordinated_users"
        ] >= 5
    ),
    "attack_pattern_boost"
] += 20


# Very strong coordinated rating

ratings.loc[
    (
        ratings[
            "extreme_rating_score"
        ] >= 25
    )
    &
    (
        ratings[
            "coordinated_users"
        ] >= 10
    ),
    "attack_pattern_boost"
] += 15


# Multiple extreme ratings aimed at same item

ratings.loc[
    ratings[
        "item_extreme_count"
    ] >= 10,
    "attack_pattern_boost"
] += 10


ratings[
    "attack_pattern_boost"
] = ratings[
    "attack_pattern_boost"
].clip(
    0,
    40
)


# ============================================================
# FINAL SCORE
# ============================================================

print(
    "[8/9] Calculating final risk score..."
)


ratings[
    "attack_score"
] = (

    ratings[
        "extreme_rating_score"
    ] * 0.15

    +

    ratings[
        "user_behavior_score"
    ] * 0.15

    +

    ratings[
        "item_targeting_score"
    ] * 0.15

    +

    ratings[
        "duplicate_rating_score"
    ] * 0.05

    +

    ratings[
        "coordination_score"
    ] * 0.30

    +

    ratings[
        "attack_pattern_boost"
    ] * 0.20

)


ratings[
    "attack_score"
] = ratings[
    "attack_score"
].clip(
    0,
    100
)


# ============================================================
# DETECTION RULES
# ============================================================

print(
    "[9/9] Applying detection rules..."
)


THRESHOLD = 50


ratings[
    "detected_fake"
] = (

    ratings[
        "attack_score"
    ] >= THRESHOLD

)


# Strong coordinated extreme-rating rule

rule_1 = (

    (
        ratings[
            "extreme_rating_score"
        ] >= 25
    )

    &

    (
        ratings[
            "coordinated_users"
        ] >= 7
    )

)


# Very strong item attack

rule_2 = (

    (
        ratings[
            "item_extreme_count"
        ] >= 10
    )

    &

    (
        ratings[
            "coordinated_users"
        ] >= 5
    )

)


# Very strong user attack behaviour

rule_3 = (

    (
        ratings[
            "user_extreme_ratio"
        ] >= 0.90
    )

    &

    (
        ratings[
            "coordinated_users"
        ] >= 5
    )

)


ratings.loc[
    rule_1 | rule_2 | rule_3,
    "detected_fake"
] = True


# ============================================================
# CONFUSION MATRIX
# ============================================================

print(
    "\nBuilding confusion matrix..."
)


TP = (

    (
        ratings[
            "is_real_attack"
        ]
        == True
    )

    &

    (
        ratings[
            "detected_fake"
        ]
        == True
    )

).sum()


FP = (

    (
        ratings[
            "is_real_attack"
        ]
        == False
    )

    &

    (
        ratings[
            "detected_fake"
        ]
        == True
    )

).sum()


FN = (

    (
        ratings[
            "is_real_attack"
        ]
        == True
    )

    &

    (
        ratings[
            "detected_fake"
        ]
        == False
    )

).sum()


TN = (

    (
        ratings[
            "is_real_attack"
        ]
        == False
    )

    &

    (
        ratings[
            "detected_fake"
        ]
        == False
    )

).sum()


# ============================================================
# METRICS
# ============================================================

precision = (

    TP / (TP + FP)

    if TP + FP > 0

    else 0

)


recall = (

    TP / (TP + FN)

    if TP + FN > 0

    else 0

)


f1 = (

    2 * precision * recall
    /
    (precision + recall)

    if precision + recall > 0

    else 0

)


accuracy = (

    (TP + TN)
    /
    (TP + TN + FP + FN)

    if TP + TN + FP + FN > 0

    else 0

)


fpr = (

    FP / (FP + TN)

    if FP + TN > 0

    else 0

)


# ============================================================
# RESULTS
# ============================================================

print("\n")
print("=" * 70)
print("                 RATING ATTACK RESULTS")
print("=" * 70)


print(
    "\nKnown fake ratings :",
    int(
        ratings[
            "is_real_attack"
        ].sum()
    )
)


print(
    "Detected suspicious:",
    int(
        ratings[
            "detected_fake"
        ].sum()
    )
)


print("\n## Confusion Matrix:\n")


print(
    "True Positives :",
    TP
)

print(
    "False Positives:",
    FP
)

print(
    "False Negatives:",
    FN
)

print(
    "True Negatives :",
    TN
)


print("\n## Performance:\n")


print(
    f"Precision          : "
    f"{precision * 100:.2f}%"
)

print(
    f"Recall             : "
    f"{recall * 100:.2f}%"
)

print(
    f"F1 Score           : "
    f"{f1 * 100:.2f}%"
)

print(
    f"Accuracy           : "
    f"{accuracy * 100:.2f}%"
)

print(
    f"False Positive Rate: "
    f"{fpr * 100:.2f}%"
)


# ============================================================
# TOP RESULTS
# ============================================================

print("\n")
print("=" * 70)
print("              TOP SUSPICIOUS RATINGS")
print("=" * 70)


display_columns = [

    user_col,

    item_col,

    rating_col,

    "attack_score",

    "extreme_rating_score",

    "user_behavior_score",

    "item_targeting_score",

    "duplicate_rating_score",

    "coordination_score",

    "attack_pattern_boost",

    "coordinated_users",

    "detected_fake",

    "is_real_attack"

]


if rating_id_col:

    display_columns.insert(
        0,
        rating_id_col
    )


print(

    ratings
    .sort_values(
        "attack_score",
        ascending=False
    )
    [display_columns]
    .head(30)
    .to_string(
        index=False
    )

)


# ============================================================
# SAVE
# ============================================================

analysis_file = os.path.join(

    RESULT_DIR,

    "rating_attack_analysis.csv"

)


metrics_file = os.path.join(

    RESULT_DIR,

    "rating_attack_metrics.csv"

)


ratings.to_csv(
    analysis_file,
    index=False
)


metrics = pd.DataFrame({

    "metric": [

        "True Positives",

        "False Positives",

        "False Negatives",

        "True Negatives",

        "Precision",

        "Recall",

        "F1 Score",

        "Accuracy",

        "False Positive Rate"

    ],

    "value": [

        TP,

        FP,

        FN,

        TN,

        precision,

        recall,

        f1,

        accuracy,

        fpr

    ]

})


metrics.to_csv(
    metrics_file,
    index=False
)


print("\n")
print("=" * 70)
print("          RATING DETECTION COMPLETE")
print("=" * 70)


print("\nFiles saved:")

print(
    analysis_file
)

print(
    metrics_file
)

print("\nDone.")