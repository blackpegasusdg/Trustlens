import pandas as pd
import re


# ============================================================
# 1. LOAD COMMENTS
# ============================================================

comments = pd.read_csv(
    "data/comments.csv"
)

print(
    "Comments loaded:",
    len(comments)
)


# ============================================================
# 2. TEXT NORMALIZATION
# ============================================================

def normalize_text(text):

    text = str(text).lower()

    text = re.sub(
        r"http\S+|www\S+",
        "",
        text
    )

    text = re.sub(
        r"[^a-z0-9\s]",
        "",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


comments["normalized_text"] = (

    comments["text"]

    .apply(
        normalize_text
    )

)


# ============================================================
# 3. SPAM KEYWORDS
# ============================================================

spam_keywords = [

    "buy now",

    "click here",

    "best deal",

    "amazing product",

    "limited offer",

    "discount",

    "free",

    "sale"

]


def spam_score(text):

    text = str(text).lower()

    matches = 0

    for keyword in spam_keywords:

        if keyword in text:

            matches += 1


    if matches == 0:

        return 0

    elif matches == 1:

        return 0.5

    else:

        return 1.0


comments["spam_probability"] = (

    comments["text"]

    .apply(
        spam_score
    )

)


comments["spam"] = (

    comments["spam_probability"] >= 0.5

).astype(int)


# ============================================================
# 4. DUPLICATE DETECTION
# ============================================================

text_counts = (

    comments[
        "normalized_text"
    ]

    .value_counts()

)


comments["text_frequency"] = (

    comments[
        "normalized_text"
    ]

    .map(
        text_counts
    )

)


# Only consider text duplicate
# when it appears multiple times

comments["duplicate"] = (

    comments[
        "text_frequency"
    ] > 1

).astype(int)


# ============================================================
# 5. COMMENT SCORE
# ============================================================

comments["comment_risk_score"] = (

    0.55 *
    comments["spam_probability"]

    +

    0.45 *
    comments["duplicate"]

) * 100


# ============================================================
# 6. SAVE
# ============================================================

comments.to_csv(
    "data/comments_scored.csv",
    index=False
)


# ============================================================
# 7. DISPLAY
# ============================================================

print()
print("======================================")
print("       COMMENT ANALYSIS")
print("======================================")

print()

print(
    "Spam comments:",
    comments["spam"].sum()
)

print(
    "Duplicate comments:",
    comments["duplicate"].sum()
)

print()

print("Sample suspicious comments:")

print()

print(

    comments[
        [
            "comment_id",
            "user_id",
            "text",
            "spam",
            "duplicate",
            "comment_risk_score"
        ]
    ]

    .sort_values(
        "comment_risk_score",
        ascending=False
    )

    .head(20)

    .to_string(
        index=False
    )

)

print()
print("Saved: data/comments_scored.csv")