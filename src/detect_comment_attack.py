import pandas as pd
import numpy as np
import os
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# TRUSTLENS
# ADVANCED FAKE COMMENT DETECTOR
# ============================================================

print("=" * 70)
print("          TRUSTLENS ADVANCED COMMENT DETECTOR")
print("=" * 70)


# ============================================================
# 1. PATHS
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
    "comment_attack",
    "advanced"
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

    print("ERROR: comments_attacked.csv not found.")

    print(comments_file)

    raise SystemExit


if not os.path.exists(injected_file):

    print("ERROR: injected_comments.csv not found.")

    print(injected_file)

    raise SystemExit


print("Attack dataset found successfully.")


# ============================================================
# 3. LOAD DATA
# ============================================================

print("\nLoading attack dataset...")


comments = pd.read_csv(
    comments_file
)

injected = pd.read_csv(
    injected_file
)


print("Dataset loaded successfully.")

print(
    "\nComments:",
    len(comments)
)

print(
    "Known attacks:",
    len(injected)
)


# ============================================================
# 4. FIND COLUMNS
# ============================================================

def find_column(df, possible):

    for col in possible:

        if col in df.columns:

            return col

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
    "User   :",
    user_col
)

print(
    "Item   :",
    item_col
)

print(
    "Text   :",
    text_col
)

print(
    "Comment:",
    comment_id_col
)


if text_col is None:

    raise ValueError(
        "Comment text column not found."
    )


# ============================================================
# 5. TEXT NORMALIZATION
# ============================================================

print(
    "\n[1/10] Normalizing comment text..."
)


def normalize_text(text):

    text = str(text).lower()

    # Remove URLs

    text = re.sub(
        r"https?://\S+|www\.\S+",
        " ",
        text
    )

    # Replace punctuation with spaces

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    # Remove repeated spaces

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


comments["normalized_text"] = (

    comments[text_col]
    .fillna("")
    .apply(normalize_text)

)


# ============================================================
# 6. WORD SETS
# ============================================================

comments["word_set"] = (

    comments["normalized_text"]
    .apply(
        lambda x: set(x.split())
    )

)


# ============================================================
# 7. EXACT DUPLICATE DETECTION
# ============================================================

print(
    "[2/10] Exact duplicate analysis..."
)


text_counts = (

    comments[
        "normalized_text"
    ]
    .value_counts()

)


comments[
    "duplicate_count"
] = (

    comments[
        "normalized_text"
    ]
    .map(text_counts)
    .fillna(1)

)


def duplicate_score(count):

    if count <= 1:

        return 0

    if count == 2:

        return 20

    if count == 3:

        return 30

    if count <= 5:

        return 40

    return 50


comments[
    "duplicate_score"
] = (

    comments[
        "duplicate_count"
    ]
    .apply(
        duplicate_score
    )

)


# ============================================================
# 8. TF-IDF WORD SIMILARITY
# ============================================================

print(
    "[3/10] TF-IDF word similarity..."
)


word_vectorizer = TfidfVectorizer(

    lowercase=True,

    ngram_range=(1, 2),

    max_features=5000

)


word_matrix = word_vectorizer.fit_transform(

    comments[
        "normalized_text"
    ]

)


best_word_similarity = np.zeros(
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


    batch = word_matrix[start:end]


    similarity = cosine_similarity(
        batch,
        word_matrix
    )


    for i in range(
        end - start
    ):

        similarity[
            i,
            start + i
        ] = 0


    best_word_similarity[
        start:end
    ] = similarity.max(
        axis=1
    )


    print(
        f"  {end}/{len(comments)} processed"
    )


comments[
    "tfidf_similarity"
] = best_word_similarity


# ============================================================
# 9. CHARACTER N-GRAM SIMILARITY
# ============================================================

print(
    "[4/10] Character n-gram similarity..."
)


char_vectorizer = TfidfVectorizer(

    analyzer="char_wb",

    ngram_range=(3, 5),

    min_df=1,

    max_features=8000

)


char_matrix = char_vectorizer.fit_transform(

    comments[
        "normalized_text"
    ]

)


best_char_similarity = np.zeros(
    len(comments)
)


for start in range(
    0,
    len(comments),
    BATCH_SIZE
):

    end = min(
        start + BATCH_SIZE,
        len(comments)
    )


    batch = char_matrix[start:end]


    similarity = cosine_similarity(
        batch,
        char_matrix
    )


    for i in range(
        end - start
    ):

        similarity[
            i,
            start + i
        ] = 0


    best_char_similarity[
        start:end
    ] = similarity.max(
        axis=1
    )


comments[
    "char_similarity"
] = best_char_similarity


# ============================================================
# 10. JACCARD SIMILARITY
# ============================================================

print(
    "[5/10] Jaccard similarity..."
)


# Instead of comparing every pair,
# use candidate groups based on the
# first few normalized words.


comments[
    "jaccard_similarity"
] = 0.0


prefix_groups = {}


for idx, words in enumerate(
    comments["word_set"]
):

    sorted_words = sorted(words)


    if len(sorted_words) == 0:

        continue


    prefix = tuple(
        sorted_words[:3]
    )


    if prefix not in prefix_groups:

        prefix_groups[prefix] = []


    prefix_groups[prefix].append(
        idx
    )


for indices in prefix_groups.values():

    if len(indices) < 2:

        continue


    sets = [

        comments.loc[
            i,
            "word_set"
        ]

        for i in indices

    ]


    for pos, i in enumerate(indices):

        best = 0


        current = sets[pos]


        for other_pos, other in enumerate(sets):

            if pos == other_pos:

                continue


            union = current | other


            if len(union) == 0:

                continue


            intersection = current & other


            score = (

                len(intersection)
                /
                len(union)

            )


            if score > best:

                best = score


        comments.loc[
            i,
            "jaccard_similarity"
        ] = best


# ============================================================
# 11. COMBINED SIMILARITY SCORE
# ============================================================

print(
    "[6/10] Combining similarity models..."
)


comments[
    "combined_similarity"
] = (

    comments[
        "tfidf_similarity"
    ] * 0.35

    +

    comments[
        "char_similarity"
    ] * 0.40

    +

    comments[
        "jaccard_similarity"
    ] * 0.25

)


def similarity_score(value):

    if value >= 0.90:

        return 50

    if value >= 0.80:

        return 40

    if value >= 0.70:

        return 30

    if value >= 0.60:

        return 20

    if value >= 0.50:

        return 10

    return 0


comments[
    "near_duplicate_score"
] = (

    comments[
        "combined_similarity"
    ]
    .apply(
        similarity_score
    )

)


# ============================================================
# 12. SPAM ANALYSIS
# ============================================================

print(
    "[7/10] Spam analysis..."
)


spam_patterns = [

    "buy now",
    "click here",
    "amazing deal",
    "best deal",
    "limited time",
    "free",
    "discount",
    "offer",
    "winner",
    "win now",
    "subscribe",
    "follow me",
    "visit",
    "promo",
    "promotion",
    "sale",
    "deal",
    "recommended",
    "highly recommended"

]


def spam_score(text):

    score = 0


    for pattern in spam_patterns:

        if pattern in text:

            score += 12


    # URLs

    if re.search(
        r"https?://|www\.",
        text
    ):

        score += 25


    # Excessive punctuation

    if text.count("!") >= 2:

        score += 10


    # Very short promotional message

    words = text.split()


    if len(words) <= 6:

        if any(
            x in text
            for x in [
                "buy",
                "deal",
                "offer",
                "sale",
                "amazing",
                "recommended"
            ]
        ):

            score += 15


    return min(
        score,
        100
    )


comments[
    "spam_score"
] = (

    comments[
        "normalized_text"
    ]
    .apply(
        spam_score
    )

)


# ============================================================
# 13. USER BEHAVIOR
# ============================================================

print(
    "[8/10] User behavior analysis..."
)


if user_col is not None:

    user_counts = (

        comments[
            user_col
        ]
        .value_counts()

    )


    comments[
        "user_comment_count"
    ] = (

        comments[
            user_col
        ]
        .map(user_counts)
        .fillna(0)

    )


    def activity_score(count):

        if count >= 30:

            return 100

        if count >= 20:

            return 70

        if count >= 10:

            return 40

        if count >= 5:

            return 20

        return 0


    comments[
        "user_activity_score"
    ] = (

        comments[
            "user_comment_count"
        ]
        .apply(
            activity_score
        )

    )

else:

    comments[
        "user_activity_score"
    ] = 0


# ============================================================
# 14. COORDINATION ANALYSIS
# ============================================================

print(
    "[9/10] Coordination analysis..."
)


comments[
    "unique_users_for_text"
] = 1


if user_col is not None:

    text_user_counts = (

        comments
        .groupby(
            "normalized_text"
        )[user_col]
        .nunique()

    )


    comments[
        "unique_users_for_text"
    ] = (

        comments[
            "normalized_text"
        ]
        .map(
            text_user_counts
        )
        .fillna(1)

    )


comments[
    "text_item_group_size"
] = 1


if item_col is not None:

    group_sizes = (

        comments
        .groupby(
            [
                "normalized_text",
                item_col
            ]
        )
        .size()

    )


    group_index = pd.MultiIndex.from_frame(

        comments[
            [
                "normalized_text",
                item_col
            ]
        ]

    )


    comments[
        "text_item_group_size"
    ] = (

        group_sizes
        .reindex(
            group_index
        )
        .fillna(1)
        .values

    )


def coordination_score(row):

    score = 0


    users = row[
        "unique_users_for_text"
    ]


    same_item = row[
        "text_item_group_size"
    ]


    similarity = row[
        "combined_similarity"
    ]


    if users >= 8:

        score += 45

    elif users >= 5:

        score += 35

    elif users >= 3:

        score += 25

    elif users == 2:

        score += 10


    if same_item >= 10:

        score += 40

    elif same_item >= 5:

        score += 30

    elif same_item >= 3:

        score += 20

    elif same_item == 2:

        score += 10


    # Similar comments across users

    if similarity >= 0.80 and users >= 3:

        score += 20

    elif similarity >= 0.70 and users >= 3:

        score += 10


    return min(
        score,
        100
    )


comments[
    "coordination_score"
] = comments.apply(

    coordination_score,

    axis=1

)


# ============================================================
# 15. ATTACK PATTERN SCORE
# ============================================================

print(
    "[10/10] Final risk calculation..."
)


comments[
    "attack_pattern_score"
] = 0


# Strong exact duplication

comments.loc[

    comments[
        "duplicate_score"
    ] >= 40,

    "attack_pattern_score"

] += 20


# Strong near duplication

comments.loc[

    comments[
        "near_duplicate_score"
    ] >= 30,

    "attack_pattern_score"

] += 20


# Spam

comments.loc[

    comments[
        "spam_score"
    ] >= 30,

    "attack_pattern_score"

] += 15


comments[
    "attack_pattern_score"
] = comments[
    "attack_pattern_score"
].clip(
    0,
    100
)


# ============================================================
# 16. BASE RISK SCORE
# ============================================================

comments[
    "base_attack_score"
] = (

    comments[
        "duplicate_score"
    ] * 0.15

    +

    comments[
        "near_duplicate_score"
    ] * 0.20

    +

    comments[
        "spam_score"
    ] * 0.15

    +

    comments[
        "user_activity_score"
    ] * 0.10

    +

    comments[
        "coordination_score"
    ] * 0.30

    +

    comments[
        "attack_pattern_score"
    ] * 0.10

)


comments[
    "base_attack_score"
] = comments[
    "base_attack_score"
].clip(
    0,
    100
)


# ============================================================
# 17. COORDINATION BOOST
# ============================================================

comments[
    "coordination_boost"
] = 0


comments.loc[

    comments[
        "coordination_score"
    ] >= 85,

    "coordination_boost"

] = 20


comments.loc[

    (
        comments[
            "coordination_score"
        ] >= 70
    )

    &

    (
        comments[
            "coordination_score"
        ] < 85
    ),

    "coordination_boost"

] = 12


# ============================================================
# 18. FINAL ATTACK SCORE
# ============================================================

comments[
    "attack_score"
] = (

    comments[
        "base_attack_score"
    ]

    +

    comments[
        "coordination_boost"
    ]

)


comments[
    "attack_score"
] = comments[
    "attack_score"
].clip(
    0,
    100
)


# ============================================================
# 19. DETECTION
# ============================================================

THRESHOLD = 60


comments[
    "detected_fake"
] = (

    comments[
        "attack_score"
    ] >= THRESHOLD

)


# ------------------------------------------------------------
# HIGH-CONFIDENCE RULES
# ------------------------------------------------------------

rule_exact = (

    (
        comments[
            "duplicate_score"
        ] >= 40
    )

    &

    (
        comments[
            "coordination_score"
        ] >= 70
    )

)


rule_near = (

    (
        comments[
            "near_duplicate_score"
        ] >= 30
    )

    &

    (
        comments[
            "coordination_score"
        ] >= 70
    )

)


rule_spam = (

    (
        comments[
            "spam_score"
        ] >= 40
    )

    &

    (
        comments[
            "coordination_score"
        ] >= 60
    )

)


comments.loc[

    rule_exact
    |
    rule_near
    |
    rule_spam,

    "detected_fake"

] = True


# ============================================================
# 20. GROUND TRUTH
# ============================================================

print(
    "\nBuilding ground truth..."
)


if "is_fake_attack" in comments.columns:

    comments[
        "is_real_attack"
    ] = (

        comments[
            "is_fake_attack"
        ]
        .fillna(False)
        .astype(bool)

    )


elif "attack_type" in comments.columns:

    comments[
        "is_real_attack"
    ] = (

        comments[
            "attack_type"
        ]
        .fillna("GENUINE")
        .astype(str)
        .str.upper()

        !=

        "GENUINE"

    )


else:

    comments[
        "is_real_attack"
    ] = False


# ============================================================
# 21. CONFUSION MATRIX
# ============================================================

TP = (

    (
        comments[
            "is_real_attack"
        ]
        == True
    )

    &

    (
        comments[
            "detected_fake"
        ]
        == True
    )

).sum()


FP = (

    (
        comments[
            "is_real_attack"
        ]
        == False
    )

    &

    (
        comments[
            "detected_fake"
        ]
        == True
    )

).sum()


FN = (

    (
        comments[
            "is_real_attack"
        ]
        == True
    )

    &

    (
        comments[
            "detected_fake"
        ]
        == False
    )

).sum()


TN = (

    (
        comments[
            "is_real_attack"
        ]
        == False
    )

    &

    (
        comments[
            "detected_fake"
        ]
        == False
    )

).sum()


# ============================================================
# 22. METRICS
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


fpr = (

    FP / (FP + TN)

    if FP + TN > 0

    else 0

)


# ============================================================
# 23. PRINT RESULTS
# ============================================================

print("\n")
print("=" * 70)
print("                 FINAL RESULTS")
print("=" * 70)


print(
    "\nKnown fake comments :",
    int(
        comments[
            "is_real_attack"
        ].sum()
    )
)


print(
    "Detected suspicious :",
    int(
        comments[
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
# 24. ATTACK TYPE PERFORMANCE
# ============================================================

if "attack_type" in comments.columns:

    print("\n")


    attack_comments = comments[
        comments[
            "is_real_attack"
        ]
        == True
    ]


    for attack_type in sorted(

        attack_comments[
            "attack_type"
        ]
        .astype(str)
        .unique()

    ):

        subset = attack_comments[

            attack_comments[
                "attack_type"
            ]
            .astype(str)
            == attack_type

        ]


        detected = subset[
            "detected_fake"
        ].sum()


        total = len(
            subset
        )


        percentage = (

            detected / total * 100

            if total > 0

            else 0

        )


        print(

            f"{attack_type:<20}"
            f"{detected}/{total} "
            f"({percentage:.2f}%)"

        )


# ============================================================
# 25. TOP SUSPICIOUS COMMENTS
# ============================================================

print("\n")
print("=" * 70)
print("              TOP SUSPICIOUS COMMENTS")
print("=" * 70)


columns = []


if comment_id_col:

    columns.append(
        comment_id_col
    )


if user_col:

    columns.append(
        user_col
    )


columns += [

    text_col,

    "attack_score",

    "duplicate_score",

    "near_duplicate_score",

    "spam_score",

    "user_activity_score",

    "coordination_score",

    "coordination_boost",

    "detected_fake",

    "is_real_attack"

]


top = (

    comments
    .sort_values(
        "attack_score",
        ascending=False
    )
    [columns]
    .head(30)

)


print(
    top.to_string(
        index=False
    )
)


# ============================================================
# 26. SAVE RESULTS
# ============================================================

analysis_file = os.path.join(

    RESULT_DIR,

    "advanced_comment_analysis.csv"

)


metrics_file = os.path.join(

    RESULT_DIR,

    "advanced_comment_metrics.csv"

)


comments.to_csv(

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


# ============================================================
# 27. COMPLETE
# ============================================================

print("\n")
print("=" * 70)
print("          ADVANCED COMMENT DETECTION COMPLETE")
print("=" * 70)


print("\nFiles saved:")

print(
    analysis_file
)

print(
    metrics_file
)

print("\nDone.")