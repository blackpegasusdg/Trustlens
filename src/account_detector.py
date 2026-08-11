import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest


# ============================================================
# 1. LOAD USERS
# ============================================================

users = pd.read_csv(
    "data/users.csv"
)

print("Users loaded:", len(users))


# ============================================================
# 2. FEATURE ENGINEERING
# ============================================================

users["following_followers_ratio"] = (

    users["following"]

    /

    (users["followers"] + 1)

)


users["posts_per_day"] = (

    users["posts"]

    /

    (users["account_age_days"] + 1)

)


# ============================================================
# 3. ISOLATION FOREST
# ============================================================

features = [

    "account_age_days",

    "followers",

    "following",

    "posts",

    "following_followers_ratio",

    "posts_per_day"

]


X = users[features].copy()


model = IsolationForest(

    n_estimators=200,

    contamination=0.08,

    random_state=42

)


model.fit(X)


users["anomaly_score_raw"] = model.decision_function(X)


# Convert anomaly score so that
# larger = more suspicious

users["isolation_score"] = (

    -users["anomaly_score_raw"]

)


# ============================================================
# 4. NORMALIZE FUNCTION
# ============================================================

def normalize(series):

    minimum = series.min()

    maximum = series.max()

    if maximum == minimum:

        return pd.Series(
            0,
            index=series.index
        )

    return (

        (series - minimum)

        /

        (maximum - minimum)

    ) * 100


# ============================================================
# 5. BEHAVIORAL SCORES
# ============================================================

users["young_account_score"] = (

    1 -

    normalize(
        users["account_age_days"]
    ) / 100

) * 100


users["low_follower_score"] = (

    1 -

    normalize(
        users["followers"]
    ) / 100

) * 100


users["following_ratio_score"] = normalize(

    users["following_followers_ratio"]

)


users["activity_score"] = normalize(

    users["posts_per_day"]

)


users["isolation_score"] = normalize(

    users["isolation_score"]

)


# ============================================================
# 6. BOT SCORE
# ============================================================

users["bot_score"] = (

    0.25 *
    users["young_account_score"]

    +

    0.20 *
    users["low_follower_score"]

    +

    0.25 *
    users["following_ratio_score"]

    +

    0.15 *
    users["activity_score"]

    +

    0.15 *
    users["isolation_score"]

)


users["bot_score"] = users[
    "bot_score"
].clip(0, 100)


# ============================================================
# 7. CLASSIFICATION
# ============================================================

users["account_status"] = np.where(

    users["bot_score"] >= 70,

    "SUSPICIOUS",

    np.where(

        users["bot_score"] >= 50,

        "WATCH",

        "NORMAL"

    )

)


# ============================================================
# 8. SAVE
# ============================================================

users.to_csv(
    "data/users_scored.csv",
    index=False
)


# ============================================================
# 9. DISPLAY
# ============================================================

print()
print("======================================")
print("       ACCOUNT DETECTION")
print("======================================")

print()

print(
    users["account_status"]
    .value_counts()
)

print()

print("Top suspicious accounts:")

print()

print(

    users[
        [
            "user_id",
            "bot_score",
            "account_status"
        ]
    ]

    .sort_values(
        "bot_score",
        ascending=False
    )

    .head(20)

    .to_string(
        index=False
    )

)

print()
print("Saved: data/users_scored.csv")