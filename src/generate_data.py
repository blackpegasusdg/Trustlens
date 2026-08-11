import pandas as pd
import numpy as np
import random
import os

# ============================================================
# SETTINGS
# ============================================================

random.seed(42)
np.random.seed(42)

NUM_USERS = 1000
NUM_ITEMS = 500
NUM_COMMENTS = 5000
NUM_RATINGS = 5000
NUM_INTERACTIONS = 10000

os.makedirs("data", exist_ok=True)


# ============================================================
# 1. USERS
# ============================================================

users = []

for i in range(NUM_USERS):

    users.append({
        "user_id": f"U{i}",
        "account_age_days": np.random.randint(30, 2000),
        "followers": np.random.randint(10, 5000),
        "following": np.random.randint(10, 3000),
        "posts": np.random.randint(1, 1000)
    })


# ============================================================
# 2. BOT-LIKE USERS
# ============================================================

bot_users = [
    f"U{i}" for i in random.sample(
        range(NUM_USERS),
        80
    )
]

for user_id in bot_users:

    index = int(user_id[1:])

    users[index]["account_age_days"] = np.random.randint(1, 30)

    users[index]["followers"] = np.random.randint(1, 50)

    users[index]["following"] = np.random.randint(1000, 5000)

    users[index]["posts"] = np.random.randint(500, 2000)


users_df = pd.DataFrame(users)


# ============================================================
# 3. ITEMS
# ============================================================

categories = [
    "Technology",
    "Gaming",
    "Fashion",
    "Sports",
    "Music",
    "Movies",
    "Food",
    "Education"
]

items = []

for i in range(NUM_ITEMS):

    items.append({
        "item_id": f"I{i}",
        "category": random.choice(categories)
    })

items_df = pd.DataFrame(items)


# ============================================================
# 4. NORMAL COMMENTS
# ============================================================

comment_templates = [

    "I really enjoyed this post about {topic}.",

    "This is an interesting perspective on {topic}.",

    "I learned something useful about {topic} here.",

    "The explanation of {topic} was very clear.",

    "I have a different opinion about {topic}.",

    "This is worth discussing further.",

    "The information presented here is useful.",

    "I think this could be improved.",

    "This was a surprisingly interesting post.",

    "Thanks for sharing this information."

]

topics = [
    "technology",
    "gaming",
    "education",
    "sports",
    "movies",
    "music",
    "fashion",
    "food"
]


# ============================================================
# 5. SPAM COMMENTS
# ============================================================

spam_comments = [

    "Amazing product buy now",

    "Best product ever buy now",

    "Click here for amazing deals",

    "You must buy this product",

    "Best deal available now"

]


comments = []


# ============================================================
# 6. NORMAL COMMENTS
# ============================================================

for i in range(NUM_COMMENTS):

    user_id = f"U{random.randint(0, NUM_USERS - 1)}"

    item_id = f"I{random.randint(0, NUM_ITEMS - 1)}"

    template = random.choice(comment_templates)

    topic = random.choice(topics)

    text = template.format(
        topic=topic
    )

    # Add a unique identifier so normal
    # comments aren't all exact duplicates

    text += f" Reference {i}"

    timestamp = (
        pd.Timestamp.now()
        -
        pd.Timedelta(
            minutes=random.randint(
                0,
                100000
            )
        )
    )

    comments.append({

        "comment_id": f"C{i}",

        "user_id": user_id,

        "item_id": item_id,

        "text": text,

        "timestamp": timestamp

    })


# ============================================================
# 7. INSERT SPAM
# ============================================================

for i in range(300):

    index = random.randint(
        0,
        len(comments) - 1
    )

    comments[index]["text"] = random.choice(
        spam_comments
    )


# ============================================================
# 8. COORDINATED COMMENT ATTACK
# ============================================================

print(
    "Injecting coordinated comment attack..."
)

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

attack_item = "I42"

attack_text = "Amazing product buy now"

attack_time = pd.Timestamp.now()


for i, user_id in enumerate(attack_users):

    comments.append({

        "comment_id": f"ATTACK_C{i}",

        "user_id": user_id,

        "item_id": attack_item,

        "text": attack_text,

        "timestamp":
            attack_time
            +
            pd.Timedelta(
                seconds=i * 20
            )

    })


comments_df = pd.DataFrame(
    comments
)


# ============================================================
# 9. RATINGS
# ============================================================

ratings = []

for i in range(NUM_RATINGS):

    ratings.append({

        "rating_id": f"R{i}",

        "user_id":
            f"U{random.randint(0, NUM_USERS - 1)}",

        "item_id":
            f"I{random.randint(0, NUM_ITEMS - 1)}",

        "rating":
            random.randint(1, 5),

        "timestamp":
            pd.Timestamp.now()
            -
            pd.Timedelta(
                minutes=random.randint(
                    0,
                    100000
                )
            )

    })


# ============================================================
# 10. RATING MANIPULATION ATTACK
# ============================================================

print(
    "Injecting rating manipulation attack..."
)

rating_attack_item = "I100"

rating_attack_time = pd.Timestamp.now()


for i, user_id in enumerate(
    attack_users
):

    ratings.append({

        "rating_id":
            f"ATTACK_R{i}",

        "user_id":
            user_id,

        "item_id":
            rating_attack_item,

        "rating":
            5,

        "timestamp":
            rating_attack_time
            +
            pd.Timedelta(
                seconds=i * 30
            )

    })


ratings_df = pd.DataFrame(
    ratings
)


# ============================================================
# 11. INTERACTIONS
# ============================================================

interactions = []

for i in range(NUM_INTERACTIONS):

    interactions.append({

        "user_id":
            f"U{random.randint(0, NUM_USERS - 1)}",

        "item_id":
            f"I{random.randint(0, NUM_ITEMS - 1)}",

        "type":
            random.choice([
                "like",
                "comment",
                "view"
            ]),

        "timestamp":
            pd.Timestamp.now()
            -
            pd.Timedelta(
                minutes=random.randint(
                    0,
                    100000
                )
            )

    })


interactions_df = pd.DataFrame(
    interactions
)


# ============================================================
# 12. SAVE
# ============================================================

users_df.to_csv(
    "data/users.csv",
    index=False
)

items_df.to_csv(
    "data/items.csv",
    index=False
)

comments_df.to_csv(
    "data/comments.csv",
    index=False
)

ratings_df.to_csv(
    "data/ratings.csv",
    index=False
)

interactions_df.to_csv(
    "data/interactions.csv",
    index=False
)


# ============================================================
# 13. SUMMARY
# ============================================================

print()
print("======================================")
print("       DATASET GENERATED")
print("======================================")

print()

print("Users:", len(users_df))
print("Items:", len(items_df))
print("Comments:", len(comments_df))
print("Ratings:", len(ratings_df))
print("Interactions:", len(interactions_df))

print()

print("Bot-like users:", len(bot_users))
print("Coordinated attackers:", len(attack_users))
print("Comment attack target:", attack_item)
print("Rating attack target:", rating_attack_item)

print()

print("Data saved successfully.")
