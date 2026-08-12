import pandas as pd
from pathlib import Path

# ============================================================
# TRUSTLENS - ATTACK ANALYSIS
# ============================================================

print("=" * 65)
print("              TRUSTLENS ATTACK ANALYSIS")
print("=" * 65)


# ------------------------------------------------------------
# 1. PROJECT PATHS
# ------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

ATTACK_DIR = BASE_DIR / "data" / "simulated_attacks"

RESULT_DIR = BASE_DIR / "data" / "attack_results"

RESULT_DIR.mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------------
# 2. FILES
# ------------------------------------------------------------

users_file = ATTACK_DIR / "users_attacked.csv"
comments_file = ATTACK_DIR / "comments_attacked.csv"
ratings_file = ATTACK_DIR / "ratings_attacked.csv"

bots_file = ATTACK_DIR / "injected_bots.csv"
fake_comments_file = ATTACK_DIR / "injected_comments.csv"
fake_ratings_file = ATTACK_DIR / "injected_ratings.csv"


# ------------------------------------------------------------
# 3. CHECK FILES
# ------------------------------------------------------------

files = [
    users_file,
    comments_file,
    ratings_file,
    bots_file,
    fake_comments_file,
    fake_ratings_file
]


for file in files:

    if not file.exists():

        print("\nERROR: File not found:")
        print(file)

        exit()


print("\nAttack dataset found successfully.")


# ------------------------------------------------------------
# 4. LOAD DATA
# ------------------------------------------------------------

users = pd.read_csv(users_file)

comments = pd.read_csv(comments_file)

ratings = pd.read_csv(ratings_file)

injected_bots = pd.read_csv(bots_file)

injected_comments = pd.read_csv(fake_comments_file)

injected_ratings = pd.read_csv(fake_ratings_file)


print("\nDataset sizes:")

print("Users:", len(users))
print("Comments:", len(comments))
print("Ratings:", len(ratings))

print("\nKnown attacks:")

print("Bots:", len(injected_bots))

print("Fake comments:", len(injected_comments))

print("Fake ratings:", len(injected_ratings))


# ------------------------------------------------------------
# 5. FIND USER ID COLUMN
# ------------------------------------------------------------

def find_user_column(df):

    possible = [
        "user_id",
        "userid",
        "id"
    ]

    for column in possible:

        if column in df.columns:
            return column

    return None


user_column = find_user_column(users)

injected_user_column = find_user_column(injected_bots)


if user_column is None:

    print("\nERROR: Could not find user ID column.")

    print("Available columns:")
    print(list(users.columns))

    exit()


print("\nUser ID column:", user_column)


# ------------------------------------------------------------
# 6. EXTRACT INJECTED BOT IDS
# ------------------------------------------------------------

known_bot_ids = set(
    injected_bots[injected_user_column]
    .astype(str)
)


print("\nKnown injected bot IDs:")

for bot in sorted(known_bot_ids):

    print(bot)


# ------------------------------------------------------------
# 7. BASIC BOT SIGNAL ANALYSIS
# ------------------------------------------------------------

print("\n")
print("=" * 65)
print("              BOT SIGNAL ANALYSIS")
print("=" * 65)


# Create analysis dataframe
analysis = users.copy()


# ------------------------------------------------------------
# FOLLOWER / FOLLOWING SIGNALS
# ------------------------------------------------------------

def find_column(df, keywords):

    for column in df.columns:

        name = column.lower()

        for keyword in keywords:

            if keyword in name:

                return column

    return None


followers_col = find_column(
    users,
    ["followers", "follower_count"]
)

following_col = find_column(
    users,
    ["following", "following_count"]
)


# ------------------------------------------------------------
# CREATE BOT SCORE
# ------------------------------------------------------------

analysis["attack_bot_score"] = 0.0


# Suspicious following/follower ratio
if followers_col and following_col:

    followers = pd.to_numeric(
        analysis[followers_col],
        errors="coerce"
    ).fillna(0)

    following = pd.to_numeric(
        analysis[following_col],
        errors="coerce"
    ).fillna(0)


    ratio = following / (followers + 1)


    # Normalize ratio
    ratio_score = (
        ratio.clip(0, 20) / 20
    ) * 100


    analysis["attack_bot_score"] += (
        ratio_score * 0.45
    )


# ------------------------------------------------------------
# VERY LOW FOLLOWERS
# ------------------------------------------------------------

if followers_col:

    followers = pd.to_numeric(
        analysis[followers_col],
        errors="coerce"
    ).fillna(0)


    low_follower_score = (
        followers <= 5
    ).astype(float) * 100


    analysis["attack_bot_score"] += (
        low_follower_score * 0.30
    )


# ------------------------------------------------------------
# VERY HIGH FOLLOWING
# ------------------------------------------------------------

if following_col:

    following = pd.to_numeric(
        analysis[following_col],
        errors="coerce"
    ).fillna(0)


    high_following_score = (
        following >= 500
    ).astype(float) * 100


    analysis["attack_bot_score"] += (
        high_following_score * 0.25
    )


# Keep score between 0 and 100

analysis["attack_bot_score"] = (
    analysis["attack_bot_score"]
    .clip(0, 100)
)


# ------------------------------------------------------------
# 8. DETECTION THRESHOLD
# ------------------------------------------------------------

DETECTION_THRESHOLD = 60


analysis["detected_bot"] = (
    analysis["attack_bot_score"]
    >= DETECTION_THRESHOLD
)


# ------------------------------------------------------------
# 9. COMPARE AGAINST GROUND TRUTH
# ------------------------------------------------------------

analysis["is_real_attack"] = (
    analysis[user_column]
    .astype(str)
    .isin(known_bot_ids)
)


# ------------------------------------------------------------
# 10. CONFUSION MATRIX
# ------------------------------------------------------------

true_positive = (
    analysis["detected_bot"]
    & analysis["is_real_attack"]
).sum()


false_positive = (
    analysis["detected_bot"]
    & ~analysis["is_real_attack"]
).sum()


false_negative = (
    ~analysis["detected_bot"]
    & analysis["is_real_attack"]
).sum()


true_negative = (
    ~analysis["detected_bot"]
    & ~analysis["is_real_attack"]
).sum()


print("\nConfusion Matrix:")

print("--------------------------------")

print("True Positives :", true_positive)

print("False Positives:", false_positive)

print("False Negatives:", false_negative)

print("True Negatives :", true_negative)


# ------------------------------------------------------------
# 11. METRICS
# ------------------------------------------------------------

precision = (
    true_positive /
    (true_positive + false_positive)
    if (true_positive + false_positive) > 0
    else 0
)


recall = (
    true_positive /
    (true_positive + false_negative)
    if (true_positive + false_negative) > 0
    else 0
)


f1 = (
    2 * precision * recall /
    (precision + recall)
    if (precision + recall) > 0
    else 0
)


accuracy = (
    (true_positive + true_negative)
    /
    len(analysis)
)


false_positive_rate = (
    false_positive /
    (false_positive + true_negative)
    if (false_positive + true_negative) > 0
    else 0
)


# ------------------------------------------------------------
# 12. DISPLAY RESULTS
# ------------------------------------------------------------

print("\n")
print("=" * 65)
print("              DETECTION PERFORMANCE")
print("=" * 65)


print(
    f"\nPrecision          : {precision * 100:.2f}%"
)

print(
    f"Recall             : {recall * 100:.2f}%"
)

print(
    f"F1 Score           : {f1 * 100:.2f}%"
)

print(
    f"Accuracy           : {accuracy * 100:.2f}%"
)

print(
    f"False Positive Rate : {false_positive_rate * 100:.2f}%"
)


# ------------------------------------------------------------
# 13. SHOW DETECTED BOTS
# ------------------------------------------------------------

detected_attacks = analysis[
    analysis["detected_bot"]
].copy()


print("\n")
print("=" * 65)
print("              DETECTED SUSPICIOUS USERS")
print("=" * 65)


display_columns = [
    user_column,
    "attack_bot_score",
    "is_real_attack",
    "detected_bot"
]


print(
    detected_attacks[
        display_columns
    ]
    .sort_values(
        "attack_bot_score",
        ascending=False
    )
    .head(30)
    .to_string(index=False)
)


# ------------------------------------------------------------
# 14. SAVE RESULTS
# ------------------------------------------------------------

output_file = RESULT_DIR / "bot_attack_analysis.csv"


analysis.to_csv(
    output_file,
    index=False
)


# Save only detected users

detected_file = RESULT_DIR / "detected_bots.csv"


detected_attacks.to_csv(
    detected_file,
    index=False
)


# Save metrics

metrics = pd.DataFrame({

    "metric": [
        "true_positive",
        "false_positive",
        "false_negative",
        "true_negative",
        "precision",
        "recall",
        "f1_score",
        "accuracy",
        "false_positive_rate"
    ],

    "value": [
        true_positive,
        false_positive,
        false_negative,
        true_negative,
        precision,
        recall,
        f1,
        accuracy,
        false_positive_rate
    ]

})


metrics_file = RESULT_DIR / "bot_detection_metrics.csv"


metrics.to_csv(
    metrics_file,
    index=False
)


# ------------------------------------------------------------
# 15. FINAL
# ------------------------------------------------------------

print("\n")
print("=" * 65)

print("ATTACK ANALYSIS COMPLETE")

print("=" * 65)

print("\nResults saved to:")

print(output_file)

print(detected_file)

print(metrics_file)

print("\n")