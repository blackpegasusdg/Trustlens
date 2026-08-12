import pandas as pd
import os
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# TRUSTLENS - FAKE COMMENT ATTACK DETECTOR
# ============================================================

print("=" * 65)
print("          TRUSTLENS FAKE COMMENT ATTACK DETECTOR")
print("=" * 65)


# ============================================================
# 1. PROJECT PATHS
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
    "comment_attack"
)

os.makedirs(
    RESULT_DIR,
    exist_ok=True
)


comments_file = os.path.join(
    ATTACK_DIR,
    "comments_attacked.csv"
)

injected_file = os.path.join(
    ATTACK_DIR,
    "injected_comments.csv"
)


# ============================================================
# 2. CHECK FILES
# ============================================================

print("\nChecking attack dataset...")

if not os.path.exists(comments_file):

    print("\nERROR: comments_attacked.csv not found.")
    print(comments_file)
    raise SystemExit


if not os.path.exists(injected_file):

    print("\nERROR: injected_comments.csv not found.")
    print(injected_file)
    raise SystemExit


print("Attack dataset found successfully.")


# ============================================================
# 3. LOAD DATA
# ============================================================

print("\nLoading datasets...")

comments = pd.read_csv(
    comments_file
)

injected = pd.read_csv(
    injected_file
)

print("Data loaded successfully.")

print("\nDataset sizes:")

print(
    "Comments:",
    len(comments)
)

print(
    "Known fake comments:",
    len(injected)
)


# ============================================================
# 4. FIND COLUMNS
# ============================================================

def find_column(df, names):

    for name in names:

        if name in df.columns:
            return name

    return None


user_col = find_column(
    comments,
    [
        "user_id",
        "userid",
        "user"
    ]
)


item_col = find_column(
    comments,
    [
        "item_id",
        "item",
        "product_id"
    ]
)


text_col = find_column(
    comments,
    [
        "text",
        "comment",
        "comment_text",
        "content"
    ]
)


comment_id_col = find_column(
    comments,
    [
        "comment_id",
        "id",
        "commentid"
    ]
)


print("\nDetected columns:")

print(
    "User column    :",
    user_col
)

print(
    "Item column    :",
    item_col
)

print(
    "Text column    :",
    text_col
)

print(
    "Comment ID     :",
    comment_id_col
)


if text_col is None:

    raise ValueError(
        "Could not find comment text column."
    )


# ============================================================
# 5. CLEAN COMMENT TEXT
# ============================================================

comments[text_col] = (

    comments[text_col]
    .fillna("")
    .astype(str)
    .str.lower()
    .str.strip()

)


# ============================================================
# 6. EXACT DUPLICATE DETECTION
# ============================================================

print("\n[1/5] Detecting exact duplicates...")


duplicate_counts = (

    comments[text_col]
    .value_counts()

)


comments["duplicate_count"] = (

    comments[text_col]
    .map(duplicate_counts)

)


def duplicate_score(count):

    if count <= 1:
        return 0

    if count == 2:
        return 50

    if count == 3:
        return 75

    return 100


comments["duplicate_score"] = (

    comments["duplicate_count"]
    .apply(duplicate_score)

)


# ============================================================
# 7. SPAM DETECTION
# ============================================================

print("[2/5] Detecting spam...")


spam_words = [

    "buy now",
    "click here",
    "free",
    "discount",
    "offer",
    "win",
    "winner",
    "subscribe",
    "follow me",
    "visit",
    "http://",
    "https://",
    "limited time",
    "promo",
    "promotion",
    "deal",
    "sale"

]


def calculate_spam_score(text):

    score = 0

    # Spam keywords

    for word in spam_words:

        if word in text:

            score += 15


    # Excessive punctuation

    exclamation_count = text.count("!")

    if exclamation_count >= 3:

        score += 20


    # Very short comment

    if len(text) < 8:

        score += 10


    # Excessive word repetition

    words = text.split()

    if len(words) >= 4:

        unique_words = len(
            set(words)
        )

        repetition_ratio = (

            1 -
            unique_words / len(words)

        )

        if repetition_ratio > 0.4:

            score += 20


    return min(
        score,
        100
    )


comments["spam_score"] = (

    comments[text_col]
    .apply(
        calculate_spam_score
    )

)


# ============================================================
# 8. TF-IDF NEAR-DUPLICATE DETECTION
# ============================================================

print("[3/5] Detecting near duplicates with TF-IDF...")


# ------------------------------------------------------------
# IMPORTANT PERFORMANCE OPTIMIZATION
# ------------------------------------------------------------
#
# We don't need a huge similarity matrix.
#
# We create TF-IDF vectors for all comments,
# but compare only against a limited reference set.
#
# ------------------------------------------------------------

vectorizer = TfidfVectorizer(

    lowercase=True,

    stop_words="english",

    ngram_range=(1, 2),

    max_features=3000

)


tfidf_matrix = vectorizer.fit_transform(

    comments[text_col]

)


# ------------------------------------------------------------
# Find suspicious duplicate groups efficiently
# ------------------------------------------------------------

# Exact duplicate comments have already been handled.
#
# For near duplicates we process the comments in batches.

near_duplicate_scores = np.zeros(
    len(comments)
)


BATCH_SIZE = 500

for start in range(
    0,
    len(comments),
    BATCH_SIZE
):

    end = min(
        start + BATCH_SIZE,
        len(comments)
    )

    batch = tfidf_matrix[start:end]

    similarities = cosine_similarity(
        batch,
        tfidf_matrix
    )

    # Ignore comparison with itself

    for i in range(
        end - start
    ):

        similarities[i, start + i] = 0


    best_similarity = (
        similarities.max(axis=1)
    )


    near_duplicate_scores[
        start:end
    ] = best_similarity


    print(
        f"  Processed {end}/{len(comments)} comments"
    )


# ------------------------------------------------------------
# Convert similarity to 0-100 score
# ------------------------------------------------------------

comments["near_duplicate_similarity"] = (
    near_duplicate_scores
)


comments["near_duplicate_score"] = np.where(

    near_duplicate_scores >= 0.90,

    100,

    np.where(

        near_duplicate_scores >= 0.80,

        75,

        np.where(

            near_duplicate_scores >= 0.70,

            50,

            np.where(

                near_duplicate_scores >= 0.60,

                25,

                0

            )

        )

    )

)


# ============================================================
# 9. USER BEHAVIOR
# ============================================================

print("[4/5] Analyzing user behaviour...")


if user_col is not None:

    user_counts = (

        comments[user_col]
        .value_counts()

    )


    comments["user_comment_count"] = (

        comments[user_col]
        .map(user_counts)
        .fillna(0)

    )


    def activity_score(count):

        if count >= 20:
            return 100

        if count >= 15:
            return 80

        if count >= 10:
            return 60

        if count >= 5:
            return 30

        return 0


    comments["user_activity_score"] = (

        comments["user_comment_count"]
        .apply(activity_score)

    )

else:

    comments["user_comment_count"] = 0

    comments["user_activity_score"] = 0


# ============================================================
# 10. ITEM TARGETING
# ============================================================

print("[5/5] Analyzing item targeting...")


if item_col is not None:

    item_counts = (

        comments[item_col]
        .value_counts()

    )


    comments["item_comment_count"] = (

        comments[item_col]
        .map(item_counts)
        .fillna(0)

    )


    def item_score(count):

        if count >= 50:
            return 100

        if count >= 30:
            return 70

        if count >= 20:
            return 50

        return 0


    comments["item_targeting_score"] = (

        comments["item_comment_count"]
        .apply(item_score)

    )

else:

    comments["item_comment_count"] = 0

    comments["item_targeting_score"] = 0


# ============================================================
# 11. COMBINED COMMENT ATTACK SCORE
# ============================================================

print("\nCalculating final comment risk score...")


comments["attack_score"] = (

    comments["duplicate_score"] * 0.35

    +

    comments["near_duplicate_score"] * 0.30

    +

    comments["spam_score"] * 0.20

    +

    comments["user_activity_score"] * 0.10

    +

    comments["item_targeting_score"] * 0.05

)


comments["attack_score"] = (

    comments["attack_score"]
    .clip(0, 100)

)


# ============================================================
# 12. CLASSIFICATION
# ============================================================

# ------------------------------------------------------------
# Initial threshold
# ------------------------------------------------------------

THRESHOLD = 60


comments["detected_fake"] = (

    comments["attack_score"]
    >= THRESHOLD

)


# ============================================================
# 13. GROUND TRUTH
# ============================================================

print("Building attack ground truth...")


# The simulator explicitly added is_fake_attack.
#
# This is the safest way to know which comments
# are actually fake.

if "is_fake_attack" in comments.columns:

    comments["is_real_attack"] = (

        comments["is_fake_attack"]
        .fillna(False)
        .astype(bool)

    )

else:

    # Backup method

    if "attack_type" in comments.columns:

        comments["is_real_attack"] = (

            comments["attack_type"]
            .fillna("GENUINE")
            .astype(str)
            .str.upper()
            != "GENUINE"

        )

    else:

        comments["is_real_attack"] = False


# ============================================================
# 14. CONFUSION MATRIX
# ============================================================

TP = (

    (
        comments["is_real_attack"]
        == True
    )

    &

    (
        comments["detected_fake"]
        == True
    )

).sum()


FP = (

    (
        comments["is_real_attack"]
        == False
    )

    &

    (
        comments["detected_fake"]
        == True
    )

).sum()


FN = (

    (
        comments["is_real_attack"]
        == True
    )

    &

    (
        comments["detected_fake"]
        == False
    )

).sum()


TN = (

    (
        comments["is_real_attack"]
        == False
    )

    &

    (
        comments["detected_fake"]
        == False
    )

).sum()


# ============================================================
# 15. METRICS
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

)


false_positive_rate = (

    FP / (FP + TN)

    if FP + TN > 0

    else 0

)


# ============================================================
# 16. DISPLAY RESULTS
# ============================================================

print("\n")
print("=" * 65)
print("             COMMENT ATTACK RESULTS")
print("=" * 65)


print(
    "\nKnown fake comments :",
    int(
        comments["is_real_attack"].sum()
    )
)


print(
    "Detected suspicious :",
    int(
        comments["detected_fake"].sum()
    )
)


print("\nConfusion Matrix:")
print("-" * 45)

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


print("\nPerformance:")
print("-" * 45)


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
# 17. ATTACK TYPE PERFORMANCE
# ============================================================

if "attack_type" in comments.columns:

    print("\n")
    print("=" * 65)
    print("             ATTACK TYPE ANALYSIS")
    print("=" * 65)


    attack_comments = comments[
        comments["is_real_attack"] == True
    ]


    for attack_type in sorted(
        attack_comments[
            "attack_type"
        ]
        .unique()
    ):

        subset = attack_comments[
            attack_comments[
                "attack_type"
            ]
            == attack_type
        ]


        detected = subset[
            "detected_fake"
        ].sum()


        total = len(subset)


        rate = (

            detected / total * 100

            if total > 0

            else 0

        )


        print(
            f"{attack_type:<20}"
            f"{detected}/{total}"
            f" detected "
            f"({rate:.2f}%)"
        )


# ============================================================
# 18. TOP SUSPICIOUS COMMENTS
# ============================================================

print("\n")
print("=" * 65)
print("             TOP SUSPICIOUS COMMENTS")
print("=" * 65)


display_columns = []


if comment_id_col:

    display_columns.append(
        comment_id_col
    )


if user_col:

    display_columns.append(
        user_col
    )


display_columns += [

    text_col,

    "attack_score",

    "duplicate_score",

    "near_duplicate_score",

    "spam_score",

    "user_activity_score",

    "item_targeting_score",

    "detected_fake",

    "is_real_attack"

]


top_comments = (

    comments

    .sort_values(
        "attack_score",
        ascending=False
    )

    [
        display_columns
    ]

    .head(30)

)


print(
    top_comments
    .to_string(
        index=False
    )
)


# ============================================================
# 19. SAVE RESULTS
# ============================================================

result_file = os.path.join(

    RESULT_DIR,

    "comment_attack_analysis.csv"

)


metrics_file = os.path.join(

    RESULT_DIR,

    "comment_detection_metrics.csv"

)


comments.to_csv(

    result_file,

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

        false_positive_rate

    ]

})


metrics.to_csv(

    metrics_file,

    index=False

)


# ============================================================
# 20. FINAL
# ============================================================

print("\n")
print("=" * 65)
print("          COMMENT ATTACK DETECTION COMPLETE")
print("=" * 65)


print("\nResults saved to:")

print(
    result_file
)

print(
    metrics_file
)

print("\nDone.")