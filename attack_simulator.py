import pandas as pd
import os
import random
from pathlib import Path


# ============================================================
# TRUSTLENS - CONTROLLED ATTACK SIMULATOR
# ============================================================

print("=" * 65)
print("              TRUSTLENS ATTACK SIMULATOR")
print("=" * 65)


# ------------------------------------------------------------
# 1. FIND PROJECT DIRECTORY
# ------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

# Your actual dataset location
DATA_DIR = BASE_DIR / "src" / "data"

# Output directory
OUTPUT_DIR = BASE_DIR / "data" / "simulated_attacks"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


print("\nData directory:")
print(DATA_DIR)

print("\nOutput directory:")
print(OUTPUT_DIR)


# ------------------------------------------------------------
# 2. LOAD ORIGINAL DATA
# ------------------------------------------------------------

users_path = DATA_DIR / "users.csv"
comments_path = DATA_DIR / "comments.csv"
ratings_path = DATA_DIR / "ratings.csv"


if not users_path.exists():
    print("\nERROR: users.csv not found.")
    print("Expected:")
    print(users_path)
    exit()

if not comments_path.exists():
    print("\nERROR: comments.csv not found.")
    print("Expected:")
    print(comments_path)
    exit()

if not ratings_path.exists():
    print("\nERROR: ratings.csv not found.")
    print("Expected:")
    print(ratings_path)
    exit()


users = pd.read_csv(users_path)
comments = pd.read_csv(comments_path)
ratings = pd.read_csv(ratings_path)


print("\nOriginal data loaded successfully.")

print("Users:", len(users))
print("Comments:", len(comments))
print("Ratings:", len(ratings))


# ------------------------------------------------------------
# 3. SHOW COLUMN NAMES
# ------------------------------------------------------------

print("\nUsers columns:")
print(list(users.columns))

print("\nComments columns:")
print(list(comments.columns))

print("\nRatings columns:")
print(list(ratings.columns))


# ------------------------------------------------------------
# 4. CONTROLLED ATTACK PARAMETERS
# ------------------------------------------------------------

NUMBER_OF_BOTS = 20

FAKE_COMMENTS_PER_BOT = 5

FAKE_RATINGS_PER_BOT = 3


# ------------------------------------------------------------
# 5. DETERMINE ID COLUMNS
# ------------------------------------------------------------

def find_column(df, possible_names):

    for name in possible_names:

        if name in df.columns:
            return name

    return None


user_id_col = find_column(
    users,
    ["user_id", "userid", "id"]
)

comment_user_col = find_column(
    comments,
    ["user_id", "userid", "author_id"]
)

comment_text_col = find_column(
    comments,
    ["comment_text", "comment", "text", "content"]
)

rating_user_col = find_column(
    ratings,
    ["user_id", "userid", "rater_id"]
)

rating_item_col = find_column(
    ratings,
    ["item_id", "itemid", "product_id"]
)

rating_value_col = find_column(
    ratings,
    ["rating", "score", "rating_value"]
)


print("\nDetected columns:")

print("User ID:", user_id_col)
print("Comment user:", comment_user_col)
print("Comment text:", comment_text_col)

print("Rating user:", rating_user_col)
print("Rating item:", rating_item_col)
print("Rating value:", rating_value_col)


# ------------------------------------------------------------
# 6. CREATE BOT ACCOUNTS
# ------------------------------------------------------------

print("\nCreating bot accounts...")


existing_user_ids = set(
    users[user_id_col].astype(str)
)


bot_users = []


for i in range(NUMBER_OF_BOTS):

    bot_id = f"BOT_{i + 1:03d}"

    # Make sure ID does not already exist
    while bot_id in existing_user_ids:

        bot_id = f"BOT_{random.randint(1000, 9999)}"


    existing_user_ids.add(bot_id)


    # Start with a copy of the first user's structure
    new_user = {}

    for column in users.columns:

        # Default value
        new_user[column] = None


    # Set ID
    new_user[user_id_col] = bot_id


    # Try to create suspicious account attributes
    for column in users.columns:

        column_lower = column.lower()


        if "follower" in column_lower:
            new_user[column] = random.randint(0, 3)


        elif "following" in column_lower:
            new_user[column] = random.randint(500, 1000)


        elif "friend" in column_lower:
            new_user[column] = random.randint(0, 5)


        elif "age" in column_lower:
            new_user[column] = random.randint(1, 30)


        elif "account" in column_lower and "age" in column_lower:
            new_user[column] = random.randint(1, 7)


    bot_users.append(new_user)


bot_users_df = pd.DataFrame(bot_users)


# Combine with original users
attacked_users = pd.concat(
    [users, bot_users_df],
    ignore_index=True
)


print("Bots injected:", len(bot_users_df))


# ------------------------------------------------------------
# 7. GENERATE FAKE COMMENTS
# ------------------------------------------------------------

print("\nInjecting fake comments...")


fake_comments = []


# Get existing item IDs if available
comment_item_col = find_column(
    comments,
    ["item_id", "itemid", "product_id"]
)


if comment_item_col is not None:

    available_items = (
        comments[comment_item_col]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

else:

    available_items = ["I001"]


fake_comment_texts = [

    "Amazing product! Highly recommended!",
    "Best product ever!",
    "Excellent quality, I love it!",
    "Five stars! Absolutely perfect!",
    "Highly recommend this to everyone!",
    "Great product and great experience!",
    "This is the best thing I have purchased!",
    "Perfect! Totally worth it!",
    "Excellent! Buy this now!",
    "Very good product, highly recommended!"

]


for bot in bot_users_df[user_id_col]:

    for j in range(FAKE_COMMENTS_PER_BOT):

        row = {}

        # Create empty structure
        for column in comments.columns:
            row[column] = None


        # User
        if comment_user_col:
            row[comment_user_col] = bot


        # Item
        if comment_item_col:
            row[comment_item_col] = random.choice(
                available_items
            )


        # Comment
        if comment_text_col:
            row[comment_text_col] = random.choice(
                fake_comment_texts
            )


        # Fill common columns
        for column in comments.columns:

            column_lower = column.lower()

            if "timestamp" in column_lower:
                row[column] = pd.Timestamp.now()

            elif "date" in column_lower:
                row[column] = pd.Timestamp.now()


        fake_comments.append(row)


fake_comments_df = pd.DataFrame(fake_comments)


attacked_comments = pd.concat(
    [comments, fake_comments_df],
    ignore_index=True
)


print(
    "Fake comments injected:",
    len(fake_comments_df)
)


# ------------------------------------------------------------
# 8. GENERATE FAKE RATINGS
# ------------------------------------------------------------

print("\nInjecting fake ratings...")


fake_ratings = []


if rating_item_col:

    rating_items = (
        ratings[rating_item_col]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

else:

    rating_items = ["I001"]


for bot in bot_users_df[user_id_col]:

    # Choose a small number of items
    selected_items = random.sample(
        rating_items,
        min(
            FAKE_RATINGS_PER_BOT,
            len(rating_items)
        )
    )


    for item in selected_items:

        row = {}

        for column in ratings.columns:
            row[column] = None


        # User
        if rating_user_col:
            row[rating_user_col] = bot


        # Item
        if rating_item_col:
            row[rating_item_col] = item


        # Fake rating
        if rating_value_col:

            # Strong positive manipulation
            row[rating_value_col] = 5


        # Timestamp
        for column in ratings.columns:

            column_lower = column.lower()

            if "timestamp" in column_lower:
                row[column] = pd.Timestamp.now()

            elif "date" in column_lower:
                row[column] = pd.Timestamp.now()


        fake_ratings.append(row)


fake_ratings_df = pd.DataFrame(fake_ratings)


attacked_ratings = pd.concat(
    [ratings, fake_ratings_df],
    ignore_index=True
)


print(
    "Fake ratings injected:",
    len(fake_ratings_df)
)


# ------------------------------------------------------------
# 9. SAVE ATTACK DATA
# ------------------------------------------------------------

attacked_users.to_csv(
    OUTPUT_DIR / "users_attacked.csv",
    index=False
)


attacked_comments.to_csv(
    OUTPUT_DIR / "comments_attacked.csv",
    index=False
)


attacked_ratings.to_csv(
    OUTPUT_DIR / "ratings_attacked.csv",
    index=False
)


# Also save ONLY the injected attack records
bot_users_df.to_csv(
    OUTPUT_DIR / "injected_bots.csv",
    index=False
)


fake_comments_df.to_csv(
    OUTPUT_DIR / "injected_comments.csv",
    index=False
)


fake_ratings_df.to_csv(
    OUTPUT_DIR / "injected_ratings.csv",
    index=False
)


# ------------------------------------------------------------
# 10. SUMMARY
# ------------------------------------------------------------

print("\n")
print("=" * 65)
print("             ATTACK SIMULATION COMPLETE")
print("=" * 65)

print("\nOriginal users:", len(users))
print("Original comments:", len(comments))
print("Original ratings:", len(ratings))

print("\nBots injected:", len(bot_users_df))
print("Fake comments injected:", len(fake_comments_df))
print("Fake ratings injected:", len(fake_ratings_df))

print("\nFinal datasets:")

print("Users:", len(attacked_users))
print("Comments:", len(attacked_comments))
print("Ratings:", len(attacked_ratings))

print("\nAttack data saved to:")

print(OUTPUT_DIR)

print("\nFiles created:")

print("  users_attacked.csv")
print("  comments_attacked.csv")
print("  ratings_attacked.csv")
print("  injected_bots.csv")
print("  injected_comments.csv")
print("  injected_ratings.csv")

print("\n" + "=" * 65)