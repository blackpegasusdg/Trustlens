# ============================================================
# TRUSTLENS - RATING ATTACK DETECTOR
# ============================================================
#
# Detects:
#   1. Extreme ratings
#   2. Suspicious user behaviour
#   3. Item targeting
#   4. Duplicate rating patterns
#   5. Coordinated behaviour
#   6. Suspicious account behaviour
#   7. Attack clusters
#   8. Evidence combination
#   9. Final attack risk score
#
# IMPORTANT:
#
# Ground truth from injected_ratings.csv is used ONLY
# for evaluation.
#
# Ground truth is NEVER used to calculate attack_score.
#
# ============================================================

import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parent

DATA_DIR = PROJECT_DIR / "data"

ATTACK_DIR = DATA_DIR / "simulated_attacks"

ATTACK_FILE = ATTACK_DIR / "ratings_attacked.csv"

INJECTED_FILE = ATTACK_DIR / "injected_ratings.csv"

USERS_ATTACKED_FILE = ATTACK_DIR / "users_attacked.csv"

RESULT_DIR = (
    DATA_DIR
    / "attack_results"
    / "rating_attack"
)

ANALYSIS_FILE = (
    RESULT_DIR
    / "rating_attack_analysis.csv"
)

METRICS_FILE = (
    RESULT_DIR
    / "rating_attack_metrics.csv"
)


# ============================================================
# DETECTION CONFIGURATION
# ============================================================

# Main suspicious threshold.
#
# The score is deliberately designed so that:
#
# normal extreme rating alone       -> LOW
# extreme + targeting               -> usually LOW/MEDIUM
# coordinated attack               -> MEDIUM/HIGH
# strong multi-signal attack        -> HIGH/CRITICAL
#
DETECTION_THRESHOLD = 30.0


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def print_line():
    print("=" * 60)


def clean_column_names(df):
    """
    Clean dataframe column names.
    """

    df = df.copy()

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.replace("\ufeff", "", regex=False)
    )

    return df


def find_column(
    df,
    candidates,
    required=True
):
    """
    Find a column using case-insensitive matching.
    """

    normalized = {
        str(col).strip().lower(): col
        for col in df.columns
    }

    for candidate in candidates:

        key = (
            str(candidate)
            .strip()
            .lower()
        )

        if key in normalized:
            return normalized[key]

    if required:

        raise ValueError(
            "\nCould not find required column.\n"
            f"Expected one of: {candidates}\n"
            f"Available columns: {list(df.columns)}"
        )

    return None


def safe_numeric(
    series,
    default=0.0
):
    """
    Safely convert values to numeric.
    """

    return (
        pd.to_numeric(
            series,
            errors="coerce"
        )
        .fillna(default)
    )


def normalize_id(value):
    """
    Normalize IDs such as:

        BOT_001
        bot_001
        I15
        i15

    into a consistent representation.
    """

    if pd.isna(value):
        return ""

    text = str(value).strip()

    if text.lower() in [
        "",
        "nan",
        "none",
        "null"
    ]:
        return ""

    return text.upper()


def normalize_rating(value):
    """
    Normalize rating values.

    5
    5.0
    '5'
    '5.0'

    all become 5.0.
    """

    try:

        value = float(value)

        return round(
            value,
            6
        )

    except Exception:

        return None


def ensure_bool(series):
    """
    Convert arbitrary values to boolean.
    """

    if series.dtype == bool:
        return series

    return (
        series
        .astype(str)
        .str.strip()
        .str.lower()
        .isin(
            [
                "true",
                "1",
                "yes",
                "y"
            ]
        )
    )


# ============================================================
# DATASET CHECK
# ============================================================

print_line()

print(
    "TRUSTLENS RATING ATTACK DETECTOR"
)

print_line()

print()
print(
    "Project directory detected:"
)

print(PROJECT_DIR)

print()
print(
    "Checking attack dataset..."
)

print()
print(
    "Expected:"
)

print(ATTACK_FILE)


if not ATTACK_FILE.exists():

    print()
    print(
        "ERROR: Attack dataset not found."
    )

    print()
    print(
        "The detector searched:"
    )

    print(ATTACK_FILE)

    print()
    print(
        "Let's check the data folder..."
    )

    if DATA_DIR.exists():

        print()
        print(
            "Data folder found:"
        )

        print(DATA_DIR)

        print()
        print(
            "Contents:"
        )

        try:

            for item in DATA_DIR.iterdir():

                print(
                    "  ",
                    item.name
                )

        except Exception:
            pass

    else:

        print()
        print(
            "Data folder does not exist:"
        )

        print(DATA_DIR)

    print()
    print(
        "Expected folder structure:"
    )

    print()

    print("TrustLens/")
    print("│")
    print("├── data/")
    print("│   ├── simulated_attacks/")
    print("│   │   ├── ratings_attacked.csv")
    print("│   │   ├── injected_ratings.csv")
    print("│   │   ├── users_attacked.csv")
    print("│   │   └── comments_attacked.csv")
    print("│   │")
    print("│   └── attack_results/")
    print("│")
    print("├── detect_rating_attack.py")
    print("└── app.py")

    print()
    print(
        "If ratings_attacked.csv is missing,"
    )

    print(
        "run the CONTROLLED RATING ATTACK SIMULATOR first."
    )

    sys.exit(1)


print()
print(
    "Attack dataset found successfully."
)


# ============================================================
# LOAD DATASET
# ============================================================

print()
print(
    "Loading attack dataset..."
)

try:

    df = pd.read_csv(
        ATTACK_FILE
    )

except Exception as e:

    print()
    print(
        "ERROR while loading dataset:"
    )

    print(e)

    sys.exit(1)


df = clean_column_names(df)

print(
    "Dataset loaded successfully."
)

print()
print(
    "Dataset size:"
)

print(
    "Ratings:",
    len(df)
)


# ============================================================
# DETECT DATASET COLUMNS
# ============================================================

try:

    USER_COL = find_column(
        df,
        [
            "user_id",
            "user",
            "userid",
            "user id"
        ]
    )

    ITEM_COL = find_column(
        df,
        [
            "item_id",
            "item",
            "itemid",
            "item id"
        ]
    )

    RATING_COL = find_column(
        df,
        [
            "rating",
            "score",
            "stars"
        ]
    )

    RATING_ID_COL = find_column(
        df,
        [
            "rating_id",
            "ratingid",
            "review_id",
            "reviewid",
            "id"
        ],
        required=False
    )

except Exception as e:

    print()
    print(
        "ERROR detecting dataset columns:"
    )

    print(e)

    sys.exit(1)


print()
print(
    "Detected columns:"
)

print(
    "User    :",
    USER_COL
)

print(
    "Item    :",
    ITEM_COL
)

print(
    "Rating  :",
    RATING_COL
)

print(
    "Rating ID:",
    RATING_ID_COL
)


# ============================================================
# STANDARD INTERNAL COLUMNS
# ============================================================

df["_user"] = (
    df[USER_COL]
    .apply(normalize_id)
)

df["_item"] = (
    df[ITEM_COL]
    .apply(normalize_id)
)

df["_rating"] = safe_numeric(
    df[RATING_COL]
)


if RATING_ID_COL is not None:

    df["_rating_id"] = (
        df[RATING_ID_COL]
        .apply(normalize_id)
    )

    df["_rating_id"] = (
        df["_rating_id"]
        .replace(
            "",
            np.nan
        )
    )

else:

    df["_rating_id"] = np.nan


# ============================================================
# LOAD INJECTED RATINGS
# ============================================================

injected_df = None

inj_user_col = None
inj_item_col = None
inj_rating_col = None
inj_rating_id_col = None

if INJECTED_FILE.exists():

    print()
    print(
        "Injected ratings file found."
    )

    try:

        injected_df = pd.read_csv(
            INJECTED_FILE
        )

        injected_df = clean_column_names(
            injected_df
        )

        print(
            "Known injected ratings:",
            len(injected_df)
        )

    except Exception as e:

        print()
        print(
            "WARNING: Could not load injected ratings:"
        )

        print(e)

        injected_df = None

else:

    print()
    print(
        "WARNING: injected_ratings.csv not found."
    )

    print(
        "Ground truth evaluation will be unavailable."
    )


# ============================================================
# DETECT INJECTED FILE COLUMNS
# ============================================================

if (
    injected_df is not None
    and len(injected_df) > 0
):

    inj_user_col = find_column(
        injected_df,
        [
            "user_id",
            "user",
            "userid",
            "user id"
        ],
        required=False
    )

    inj_item_col = find_column(
        injected_df,
        [
            "item_id",
            "item",
            "itemid",
            "item id"
        ],
        required=False
    )

    inj_rating_col = find_column(
        injected_df,
        [
            "rating",
            "score",
            "stars"
        ],
        required=False
    )

    inj_rating_id_col = find_column(
        injected_df,
        [
            "rating_id",
            "ratingid",
            "review_id",
            "reviewid",
            "id"
        ],
        required=False
    )


# ============================================================
# BUILD GROUND TRUTH
# ============================================================

print()
print(
    "Preparing ground truth..."
)


# ------------------------------------------------------------
# IMPORTANT:
#
# We create TWO types of keys:
#
# 1. Rating ID
#
# 2. User + Item + Rating
#
# The second method is essential because controlled injected
# ratings frequently do not have rating IDs.
# ------------------------------------------------------------

known_fake_id_keys = set()

known_fake_triplets = set()

known_fake_users = set()


if injected_df is not None:

    # --------------------------------------------------------
    # USER INFORMATION
    # --------------------------------------------------------

    if inj_user_col is not None:

        for value in (
            injected_df[
                inj_user_col
            ]
            .dropna()
        ):

            user = normalize_id(
                value
            )

            if user:

                known_fake_users.add(
                    user
                )


    # --------------------------------------------------------
    # RATING ID KEYS
    # --------------------------------------------------------

    if inj_rating_id_col is not None:

        for value in (
            injected_df[
                inj_rating_id_col
            ]
            .dropna()
        ):

            rating_id = normalize_id(
                value
            )

            if rating_id:

                known_fake_id_keys.add(
                    rating_id
                )


    # --------------------------------------------------------
    # USER + ITEM + RATING KEYS
    # --------------------------------------------------------

    if (
        inj_user_col is not None
        and inj_item_col is not None
        and inj_rating_col is not None
    ):

        for _, row in injected_df.iterrows():

            user = normalize_id(
                row[inj_user_col]
            )

            item = normalize_id(
                row[inj_item_col]
            )

            rating = normalize_rating(
                row[inj_rating_col]
            )

            if (
                user
                and item
                and rating is not None
            ):

                known_fake_triplets.add(
                    (
                        user,
                        item,
                        rating
                    )
                )


# ============================================================
# BOT USER INFORMATION
# ============================================================

bot_users = set()


if USERS_ATTACKED_FILE.exists():

    try:

        users_df = pd.read_csv(
            USERS_ATTACKED_FILE
        )

        users_df = clean_column_names(
            users_df
        )

        attacked_user_col = find_column(
            users_df,
            [
                "user_id",
                "user",
                "userid"
            ],
            required=False
        )

        bot_flag_col = find_column(
            users_df,
            [
                "is_bot",
                "bot",
                "bot_user",
                "is_attacker"
            ],
            required=False
        )

        if (
            attacked_user_col is not None
            and bot_flag_col is not None
        ):

            flags = ensure_bool(
                users_df[
                    bot_flag_col
                ]
            )

            bot_users = set(
                users_df.loc[
                    flags,
                    attacked_user_col
                ]
                .apply(normalize_id)
            )

    except Exception:

        bot_users = set()


# ------------------------------------------------------------
# Fallback only for reporting.
#
# BOT_ naming is NOT used as a detection signal.
# ------------------------------------------------------------

if not bot_users:

    bot_users = {
        user
        for user in df["_user"].unique()
        if user.startswith("BOT_")
    }


if bot_users:

    print()
    print(
        "Known bot users:",
        len(bot_users)
    )

    print(
        "Bot IDs:"
    )

    for bot in sorted(
        bot_users
    ):

        print(bot)


# ============================================================
# INITIALIZE FEATURES
# ============================================================

df["extreme_rating_score"] = 0.0

df["user_behavior_score"] = 0.0

df["item_targeting_score"] = 0.0

df["duplicate_rating_score"] = 0.0

df["coordination_score"] = 0.0

df["coordinated_users"] = 0

df["cluster_score"] = 0.0

df["combination_bonus"] = 0.0

df["bot_user_flag"] = False

df["evidence_count"] = 0


# ============================================================
# [1/9] EXTREME RATING ANALYSIS
# ============================================================

print()
print(
    "[1/9] Analyzing extreme ratings..."
)


# ------------------------------------------------------------
# Extreme ratings are a weak signal.
#
# 1-star and 5-star ratings are common in legitimate systems.
# ------------------------------------------------------------

df["extreme_rating_score"] = np.where(
    df["_rating"].isin(
        [
            1,
            5
        ]
    ),
    20.0,
    0.0
)


# ============================================================
# [2/9] USER BEHAVIOUR
# ============================================================

print(
    "[2/9] Analyzing user behavior..."
)


user_counts = (
    df.groupby(
        "_user"
    )
    .size()
    .rename(
        "_user_count"
    )
)

df = df.join(
    user_counts,
    on="_user"
)


user_unique_items = (
    df.groupby(
        "_user"
    )["_item"]
    .nunique()
    .rename(
        "_unique_items"
    )
)

df = df.join(
    user_unique_items,
    on="_user"
)


df["_extreme"] = (
    df["_rating"]
    .isin(
        [
            1,
            5
        ]
    )
)


user_extreme_ratio = (
    df.groupby(
        "_user"
    )["_extreme"]
    .mean()
    .rename(
        "_extreme_ratio"
    )
)

df = df.join(
    user_extreme_ratio,
    on="_user"
)


# ------------------------------------------------------------
# Activity percentile
# ------------------------------------------------------------

activity_percentile = (
    df["_user_count"]
    .rank(
        pct=True
    )
)


behavior_score = np.zeros(
    len(df),
    dtype=float
)


# High activity
behavior_score += np.where(
    activity_percentile >= 0.95,
    15.0,
    0.0
)


# Highly extreme behaviour
behavior_score += np.where(
    df["_extreme_ratio"] >= 0.80,
    15.0,
    0.0
)


# Very low item diversity
behavior_score += np.where(
    df["_unique_items"] <= 3,
    10.0,
    0.0
)


df["user_behavior_score"] = np.clip(
    behavior_score,
    0,
    40
)


# ============================================================
# [3/9] ITEM TARGETING
# ============================================================

print(
    "[3/9] Analyzing item targeting..."
)


item_counts = (
    df.groupby(
        "_item"
    )
    .size()
    .rename(
        "_item_count"
    )
)

df = df.join(
    item_counts,
    on="_item"
)


item_users = (
    df.groupby(
        "_item"
    )["_user"]
    .nunique()
    .rename(
        "_item_unique_users"
    )
)

df = df.join(
    item_users,
    on="_item"
)


item_extreme_ratio = (
    df.groupby(
        "_item"
    )["_extreme"]
    .mean()
    .rename(
        "_item_extreme_ratio"
    )
)

df = df.join(
    item_extreme_ratio,
    on="_item"
)


targeting_score = np.zeros(
    len(df),
    dtype=float
)


# Many ratings directed at an item
targeting_score += np.where(
    df["_item_count"] >= 8,
    15.0,
    0.0
)


# Strong targeting
targeting_score += np.where(
    df["_item_count"] >= 12,
    10.0,
    0.0
)


# Many extreme ratings
targeting_score += np.where(
    df["_item_extreme_ratio"] >= 0.80,
    15.0,
    0.0
)


df["item_targeting_score"] = np.clip(
    targeting_score,
    0,
    40
)


# ============================================================
# [4/9] DUPLICATE RATING PATTERNS
# ============================================================

print(
    "[4/9] Detecting duplicate rating patterns..."
)


# ------------------------------------------------------------
# Same user + same item + same rating repeated.
# ------------------------------------------------------------

duplicate_mask = (
    df.duplicated(
        subset=[
            "_user",
            "_item",
            "_rating"
        ],
        keep=False
    )
)


df["duplicate_rating_score"] = np.where(
    duplicate_mask,
    40.0,
    0.0
)


# ------------------------------------------------------------
# Multiple users giving identical ratings to same item.
# ------------------------------------------------------------

group_user_count = (
    df.groupby(
        [
            "_item",
            "_rating"
        ]
    )["_user"]
    .transform(
        "nunique"
    )
)


df["duplicate_rating_score"] += np.where(
    group_user_count >= 5,
    20.0,
    0.0
)


df["duplicate_rating_score"] = np.clip(
    df["duplicate_rating_score"],
    0,
    60
)


# ============================================================
# [5/9] COORDINATED BEHAVIOUR
# ============================================================

print(
    "[5/9] Detecting coordinated behavior..."
)


# ------------------------------------------------------------
# For every item + rating pair:
#
# How many different users participated?
#
# Example:
#
# I15 + 5 stars
# -> BOT_001
# -> BOT_002
# -> BOT_003
# -> U100
# -> U200
#
# = 5 coordinated users
# ------------------------------------------------------------

coordination_group_users = (
    df.groupby(
        [
            "_item",
            "_rating"
        ]
    )["_user"]
    .transform(
        "nunique"
    )
)


df["coordinated_users"] = (
    coordination_group_users
    .astype(int)
)


df["coordination_score"] = np.select(

    [
        df["coordinated_users"] >= 15,

        df["coordinated_users"] >= 10,

        df["coordinated_users"] >= 7,

        df["coordinated_users"] >= 5
    ],

    [
        80.0,
        60.0,
        45.0,
        30.0
    ],

    default=0.0
)


# ============================================================
# [6/9] SUSPICIOUS ACCOUNT BEHAVIOUR
# ============================================================

print(
    "[6/9] Analyzing suspicious account behavior..."
)


# ------------------------------------------------------------
# Informational only.
#
# IMPORTANT:
# bot_user_flag is NOT directly added to attack_score.
# ------------------------------------------------------------

df["bot_user_flag"] = (
    df["_user"]
    .isin(
        bot_users
    )
)


df["_small_account"] = (
    df["_user_count"] <= 3
)


# ------------------------------------------------------------
# Suspicious account pattern:
#
# Small account
# +
# extreme behaviour
# +
# coordinated activity
#
# This is still based entirely on behavioural evidence.
# ------------------------------------------------------------

account_pattern_bonus = np.where(

    (
        df["_small_account"]
        &
        (
            df["_extreme_ratio"] >= 0.80
        )
        &
        (
            df["coordinated_users"] >= 5
        )
    ),

    15.0,

    0.0
)


# Add this later as part of combination bonus.
df["_account_pattern_bonus"] = (
    account_pattern_bonus
)


# ============================================================
# [7/9] ATTACK CLUSTERS
# ============================================================

print(
    "[7/9] Detecting attack clusters..."
)


cluster_score = np.zeros(
    len(df),
    dtype=float
)


# Coordination
cluster_score += np.where(
    df["coordinated_users"] >= 7,
    25.0,
    0.0
)


cluster_score += np.where(
    df["coordinated_users"] >= 10,
    20.0,
    0.0
)


# Duplicate pattern
cluster_score += np.where(
    df["duplicate_rating_score"] >= 40,
    20.0,
    0.0
)


# Targeting
cluster_score += np.where(
    df["item_targeting_score"] >= 20,
    15.0,
    0.0
)


# Behaviour
cluster_score += np.where(
    df["user_behavior_score"] >= 20,
    10.0,
    0.0
)


df["cluster_score"] = np.clip(
    cluster_score,
    0,
    70
)


# ============================================================
# [8/9] COMBINING ATTACK EVIDENCE
# ============================================================

print(
    "[8/9] Combining attack evidence..."
)


# ------------------------------------------------------------
# Independent evidence count.
# ------------------------------------------------------------

evidence = (

    (
        df["extreme_rating_score"]
        >= 20
    )
    .astype(int)

    +

    (
        df["user_behavior_score"]
        >= 20
    )
    .astype(int)

    +

    (
        df["item_targeting_score"]
        >= 20
    )
    .astype(int)

    +

    (
        df["duplicate_rating_score"]
        >= 40
    )
    .astype(int)

    +

    (
        df["coordination_score"]
        >= 45
    )
    .astype(int)

    +

    (
        df["cluster_score"]
        >= 40
    )
    .astype(int)

    +

    (
        df["_account_pattern_bonus"]
        > 0
    )
    .astype(int)
)


df["evidence_count"] = evidence


# ------------------------------------------------------------
# Combination bonus.
# ------------------------------------------------------------

df["combination_bonus"] = np.select(

    [

        df["evidence_count"] >= 6,

        df["evidence_count"] >= 5,

        df["evidence_count"] >= 4,

        df["evidence_count"] >= 3,

        df["evidence_count"] >= 2
    ],

    [
        35.0,
        30.0,
        25.0,
        15.0,
        5.0
    ],

    default=0.0
)


# Add account behaviour pattern.
df["combination_bonus"] += (
    df["_account_pattern_bonus"]
)


df["combination_bonus"] = np.clip(
    df["combination_bonus"],
    0,
    70
)


# ============================================================
# [9/9] FINAL ATTACK SCORE
# ============================================================

print(
    "[9/9] Calculating final attack score..."
)


# ------------------------------------------------------------
# Weighted evidence model.
#
# Coordination       25%
# Item targeting     15%
# User behaviour     15%
# Cluster evidence   15%
# Duplicate pattern  10%
# Extreme rating      5%
# Combination bonus  15%
# ------------------------------------------------------------

score = (

    df["coordination_score"]
    * 0.25

    +

    df["item_targeting_score"]
    * 0.15

    +

    df["user_behavior_score"]
    * 0.15

    +

    df["cluster_score"]
    * 0.15

    +

    df["duplicate_rating_score"]
    * 0.10

    +

    df["extreme_rating_score"]
    * 0.05

    +

    df["combination_bonus"]
    * 0.15
)


# ------------------------------------------------------------
# Strong coordination rule.
#
# Does NOT depend on bot_user_flag.
# ------------------------------------------------------------

strong_coordination = (

    (
        df["coordinated_users"]
        >= 10
    )

    &

    (
        df["evidence_count"]
        >= 3
    )
)


score += np.where(
    strong_coordination,
    10.0,
    0.0
)


# ------------------------------------------------------------
# Coordinated extreme attack.
#
# Many users
# +
# extreme rating
# +
# targeting
# ------------------------------------------------------------

coordinated_extreme_attack = (

    (
        df["coordinated_users"]
        >= 7
    )

    &

    (
        df["_rating"]
        .isin(
            [
                1,
                5
            ]
        )
    )

    &

    (
        df["item_targeting_score"]
        >= 20
    )
)


score += np.where(
    coordinated_extreme_attack,
    8.0,
    0.0
)


# ------------------------------------------------------------
# Small-account coordinated attack.
#
# This is useful for controlled bot attacks where each attacker
# has only a few ratings.
# ------------------------------------------------------------

small_coordinated_attack = (

    df["_small_account"]

    &

    (
        df["coordinated_users"]
        >= 7
    )

    &

    (
        df["_extreme_ratio"]
        >= 0.80
    )
)


score += np.where(
    small_coordinated_attack,
    8.0,
    0.0
)


# ------------------------------------------------------------
# Duplicate + coordination.
# ------------------------------------------------------------

strong_duplicate_coordination = (

    (
        df["duplicate_rating_score"]
        >= 40
    )

    &

    (
        df["coordination_score"]
        >= 45
    )
)


score += np.where(
    strong_duplicate_coordination,
    7.0,
    0.0
)


df["attack_score"] = np.clip(
    score,
    0,
    100
)


# ============================================================
# RISK LEVEL
# ============================================================

df["risk_level"] = np.select(

    [

        df["attack_score"] >= 70,

        df["attack_score"] >= 50,

        df["attack_score"] >= 30
    ],

    [

        "CRITICAL",

        "HIGH",

        "MEDIUM"
    ],

    default="LOW"
)


# ============================================================
# FINAL DETECTION
# ============================================================

df["detected_fake"] = (
    df["attack_score"]
    >= DETECTION_THRESHOLD
)


# ============================================================
# BUILD GROUND TRUTH - ROBUST VERSION
# ============================================================

print()
print(
    "Building ground truth..."
)


# ------------------------------------------------------------
# We match injected ratings in this order:
#
# 1. Rating ID
#
# 2. User + Item + Rating
#
# Importantly, the second method handles duplicate rows using
# occurrence counts.
# ------------------------------------------------------------

df["is_real_attack"] = False


# ------------------------------------------------------------
# METHOD 1:
# Rating ID matching
# ------------------------------------------------------------

if (
    known_fake_id_keys
    and RATING_ID_COL is not None
):

    valid_id_mask = (
        df["_rating_id"]
        .notna()
    )

    df.loc[
        valid_id_mask,
        "is_real_attack"
    ] = (
        df.loc[
            valid_id_mask,
            "_rating_id"
        ]
        .isin(
            known_fake_id_keys
        )
    )


# ------------------------------------------------------------
# METHOD 2:
# User + Item + Rating
#
# Only apply this to rows that haven't already matched.
# ------------------------------------------------------------

if known_fake_triplets:

    candidate_mask = (
        ~df["is_real_attack"]
    )

    candidate_df = df.loc[
        candidate_mask,
        [
            "_user",
            "_item",
            "_rating"
        ]
    ].copy()


    candidate_df["_triplet"] = list(
        zip(
            candidate_df["_user"],
            candidate_df["_item"],
            candidate_df["_rating"].apply(
                normalize_rating
            )
        )
    )


    # --------------------------------------------------------
    # Count how many times each injected triplet occurs.
    # --------------------------------------------------------

    injected_triplet_counts = {}

    if injected_df is not None:

        for _, row in injected_df.iterrows():

            if (
                inj_user_col is None
                or inj_item_col is None
                or inj_rating_col is None
            ):
                continue

            user = normalize_id(
                row[inj_user_col]
            )

            item = normalize_id(
                row[inj_item_col]
            )

            rating = normalize_rating(
                row[inj_rating_col]
            )

            if (
                user
                and item
                and rating is not None
            ):

                key = (
                    user,
                    item,
                    rating
                )

                injected_triplet_counts[
                    key
                ] = (
                    injected_triplet_counts.get(
                        key,
                        0
                    )
                    + 1
                )


    # --------------------------------------------------------
    # Match occurrences without marking every duplicate.
    # --------------------------------------------------------

    used_counts = {}

    matched_indices = []

    for idx, row in candidate_df.iterrows():

        key = row["_triplet"]

        if key not in known_fake_triplets:
            continue

        allowed = injected_triplet_counts.get(
            key,
            0
        )

        used = used_counts.get(
            key,
            0
        )

        if used < allowed:

            matched_indices.append(
                idx
            )

            used_counts[key] = (
                used + 1
            )


    if matched_indices:

        df.loc[
            matched_indices,
            "is_real_attack"
        ] = True


# ============================================================
# GROUND TRUTH SANITY CHECK
# ============================================================

known_attack_count = int(
    df["is_real_attack"]
    .sum()
)


# ------------------------------------------------------------
# If we have an injected file but zero rows matched, print
# diagnostic information.
# ------------------------------------------------------------

if (
    injected_df is not None
    and len(injected_df) > 0
    and known_attack_count == 0
):

    print()
    print(
        "WARNING: injected_ratings.csv was found,"
    )

    print(
        "but no injected rows matched ratings_attacked.csv."
    )

    print()
    print(
        "Injected columns:"
    )

    print(
        list(
            injected_df.columns
        )
    )

    print()
    print(
        "Detector columns:"
    )

    print(
        list(
            df.columns
        )
    )

    print()
    print(
        "Ground truth cannot be evaluated until"
    )

    print(
        "the injected and attacked datasets share"
    )

    print(
        "matching user/item/rating values."
    )


# ============================================================
# CONFUSION MATRIX
# ============================================================

tp = int(
    (
        df["detected_fake"]
        &
        df["is_real_attack"]
    )
    .sum()
)


fp = int(
    (
        df["detected_fake"]
        &
        ~df["is_real_attack"]
    )
    .sum()
)


fn = int(
    (
        ~df["detected_fake"]
        &
        df["is_real_attack"]
    )
    .sum()
)


tn = int(
    (
        ~df["detected_fake"]
        &
        ~df["is_real_attack"]
    )
    .sum()
)


# ============================================================
# METRICS
# ============================================================

precision = (

    tp
    /
    (
        tp + fp
    )

    if (
        tp + fp
    ) > 0

    else 0.0
)


recall = (

    tp
    /
    (
        tp + fn
    )

    if (
        tp + fn
    ) > 0

    else 0.0
)


f1 = (

    2
    * precision
    * recall
    /
    (
        precision + recall
    )

    if (
        precision + recall
    ) > 0

    else 0.0
)


accuracy = (

    (
        tp + tn
    )
    /
    len(df)

    if len(df) > 0

    else 0.0
)


false_positive_rate = (

    fp
    /
    (
        fp + tn
    )

    if (
        fp + tn
    ) > 0

    else 0.0
)


# ============================================================
# OUTPUT SUMMARY
# ============================================================

print()

print(
    "Known fake ratings :",
    known_attack_count
)

print(
    "Detected suspicious:",
    int(
        df["detected_fake"]
        .sum()
    )
)


print()
print(
    "## Confusion Matrix:"
)

print()

print(
    "True Positives :",
    tp
)

print(
    "False Positives:",
    fp
)

print(
    "False Negatives:",
    fn
)

print(
    "True Negatives :",
    tn
)


print()
print(
    "## Performance:"
)

print()

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
    f"{false_positive_rate * 100:.2f}%"
)


# ============================================================
# DETECTION SUMMARY
# ============================================================

detected_attack_count = int(
    (
        df["is_real_attack"]
        &
        df["detected_fake"]
    )
    .sum()
)


if known_attack_count > 0:

    attack_detection_rate = (
        detected_attack_count
        /
        known_attack_count
    )

else:

    attack_detection_rate = 0.0


print()
print(
    "Detection summary:"
)

print()

print(
    f"Injected ratings detected: "
    f"{detected_attack_count} / "
    f"{known_attack_count}"
)

print(
    f"Overall attack detection rate: "
    f"{attack_detection_rate * 100:.2f}%"
)


# ============================================================
# RISK DISTRIBUTION
# ============================================================

print()
print(
    "Risk distribution:"
)


for level in [
    "CRITICAL",
    "HIGH",
    "MEDIUM",
    "LOW"
]:

    count = int(
        (
            df["risk_level"]
            == level
        )
        .sum()
    )

    print(
        f"{level:<10}: {count}"
    )


# ============================================================
# TOP SUSPICIOUS RATINGS
# ============================================================

print()
print(
    "Top suspicious ratings:"
)

print()


output_columns = [

    "_rating_id",

    "_user",

    "_item",

    "_rating",

    "attack_score",

    "risk_level",

    "extreme_rating_score",

    "user_behavior_score",

    "item_targeting_score",

    "duplicate_rating_score",

    "coordination_score",

    "coordinated_users",

    "cluster_score",

    "combination_bonus",

    "bot_user_flag",

    "evidence_count",

    "detected_fake",

    "is_real_attack"
]


top_suspicious = (

    df[
        df["detected_fake"]
    ]

    .sort_values(
        "attack_score",
        ascending=False
    )

    .head(30)
)


if len(
    top_suspicious
) > 0:

    print(
        top_suspicious[
            output_columns
        ]
        .to_string(
            index=False
        )
    )

else:

    print(
        "No suspicious ratings detected."
    )


# ============================================================
# ATTACK DETECTION BY INJECTED USER
# ============================================================

print()
print(
    "Attack detection by injected user:"
)


if (
    injected_df is not None
    and inj_user_col is not None
):

    user_statistics = []


    injected_users = (
        injected_df[
            inj_user_col
        ]
        .dropna()
        .apply(normalize_id)
        .replace(
            "",
            np.nan
        )
        .dropna()
        .unique()
    )


    for user in injected_users:

        # ----------------------------------------------
        # Ground-truth rows belonging to this injected
        # user.
        # ----------------------------------------------

        user_attack_rows = df[
            (
                df["_user"]
                == user
            )
            &
            (
                df["is_real_attack"]
            )
        ]


        injected_count = len(
            user_attack_rows
        )


        detected_count = int(
            user_attack_rows[
                "detected_fake"
            ]
            .sum()
        )


        # ----------------------------------------------
        # Average score of the actual injected ratings.
        # ----------------------------------------------

        if len(
            user_attack_rows
        ) > 0:

            average_score = float(
                user_attack_rows[
                    "attack_score"
                ]
                .mean()
            )

        else:

            # Fallback if ground truth matching failed.
            #
            # This is useful for debugging only.
            user_rows = df[
                df["_user"]
                == user
            ]

            average_score = (

                float(
                    user_rows[
                        "attack_score"
                    ]
                    .mean()
                )

                if len(
                    user_rows
                ) > 0

                else 0.0
            )


        detection_rate = (

            detected_count
            /
            injected_count

            if injected_count > 0

            else 0.0
        )


        user_statistics.append(

            {
                "user_id":
                    user,

                "injected_ratings":
                    injected_count,

                "detected_ratings":
                    detected_count,

                "average_score":
                    round(
                        average_score,
                        2
                    ),

                "detection_rate":
                    round(
                        detection_rate
                        * 100,
                        2
                    )
            }
        )


    if user_statistics:

        user_detection_df = (

            pd.DataFrame(
                user_statistics
            )

            .sort_values(
                [
                    "detected_ratings",
                    "average_score"
                ],
                ascending=False
            )
        )


        print(
            user_detection_df
            .to_string(
                index=False
            )
        )


    else:

        user_detection_df = (
            pd.DataFrame()
        )

        print(
            "No injected-user information available."
        )


else:

    user_detection_df = (
        pd.DataFrame()
    )

    print(
        "Injected-user statistics unavailable."
    )


# ============================================================
# SAVE RESULTS
# ============================================================

RESULT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# CLEAN ANALYSIS DATAFRAME
# ============================================================

analysis_df = df.copy()


analysis_df = analysis_df.rename(
    columns={
        "_rating_id":
            "rating_id",

        "_user":
            "user_id",

        "_item":
            "item_id",

        "_rating":
            "rating"
    }
)


# ============================================================
# PUBLIC OUTPUT COLUMNS
# ============================================================

preferred_columns = [

    "rating_id",

    "user_id",

    "item_id",

    "rating",

    "attack_score",

    "risk_level",

    "extreme_rating_score",

    "user_behavior_score",

    "item_targeting_score",

    "duplicate_rating_score",

    "coordination_score",

    "coordinated_users",

    "cluster_score",

    "combination_bonus",

    "bot_user_flag",

    "evidence_count",

    "detected_fake",

    "is_real_attack"
]


existing_columns = [

    col

    for col in preferred_columns

    if col in analysis_df.columns
]


analysis_df = analysis_df[
    existing_columns
]


# ============================================================
# SAVE ANALYSIS
# ============================================================

analysis_df.to_csv(
    ANALYSIS_FILE,
    index=False
)


# ============================================================
# SAVE USER DETECTION FILE
# ============================================================

if (
    user_detection_df is not None
    and not user_detection_df.empty
):

    USER_ANALYSIS_FILE = (
        RESULT_DIR
        / "rating_attack_by_user.csv"
    )

    user_detection_df.to_csv(
        USER_ANALYSIS_FILE,
        index=False
    )

else:

    USER_ANALYSIS_FILE = None


# ============================================================
# METRICS DATAFRAME
# ============================================================

metrics = pd.DataFrame(

    {
        "metric": [

            "total_ratings",

            "known_fake_ratings",

            "detected_suspicious",

            "true_positives",

            "false_positives",

            "false_negatives",

            "true_negatives",

            "precision",

            "recall",

            "f1_score",

            "accuracy",

            "false_positive_rate",

            "attack_detection_rate",

            "detection_threshold"
        ],

        "value": [

            len(df),

            known_attack_count,

            int(
                df[
                    "detected_fake"
                ]
                .sum()
            ),

            tp,

            fp,

            fn,

            tn,

            round(
                precision,
                6
            ),

            round(
                recall,
                6
            ),

            round(
                f1,
                6
            ),

            round(
                accuracy,
                6
            ),

            round(
                false_positive_rate,
                6
            ),

            round(
                attack_detection_rate,
                6
            ),

            DETECTION_THRESHOLD
        ]
    }
)


# ============================================================
# SAVE METRICS
# ============================================================

metrics.to_csv(
    METRICS_FILE,
    index=False
)


# ============================================================
# FINAL FILE INFORMATION
# ============================================================

print()
print(
    "Files saved:"
)

print(
    ANALYSIS_FILE
)

print(
    METRICS_FILE
)


if USER_ANALYSIS_FILE is not None:

    print(
        USER_ANALYSIS_FILE
    )


print()
print_line()

print(
    "RATING ATTACK DETECTION COMPLETE"
)

print_line()