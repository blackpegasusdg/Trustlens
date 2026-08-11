import pandas as pd
import networkx as nx
from itertools import combinations


# ============================================================
# 1. LOAD
# ============================================================

comments = pd.read_csv(
    "data/comments_scored.csv"
)

comments["timestamp"] = pd.to_datetime(
    comments["timestamp"]
)


print(
    "Comments loaded:",
    len(comments)
)


# ============================================================
# 2. GRAPH
# ============================================================

G = nx.Graph()


for user_id in comments["user_id"].unique():

    G.add_node(
        user_id
    )


# ============================================================
# 3. FIND COORDINATED EVENTS
# ============================================================

coordination_events = []


for item_id, group in comments.groupby(
    "item_id"
):

    for idx1, idx2 in combinations(
        group.index,
        2
    ):

        row1 = comments.loc[idx1]

        row2 = comments.loc[idx2]


        user1 = row1["user_id"]

        user2 = row2["user_id"]


        if user1 == user2:

            continue


        # Time difference

        time_difference = abs(

            (

                row1["timestamp"]

                -

                row2["timestamp"]

            ).total_seconds()

        )


        text1 = str(
            row1["normalized_text"]
        )

        text2 = str(
            row2["normalized_text"]
        )


        same_text = (

            text1 == text2

        )


        # ====================================================
        # COORDINATION CONDITION
        # ====================================================

        if (

            same_text

            and

            time_difference <= 300

        ):

            coordination_events.append({

                "user1": user1,

                "user2": user2,

                "item_id": item_id,

                "time_difference":
                    time_difference,

                "text": text1

            })


            if G.has_edge(
                user1,
                user2
            ):

                G[user1][user2][
                    "weight"
                ] += 1

            else:

                G.add_edge(

                    user1,

                    user2,

                    weight=1

                )


# ============================================================
# 4. EVENTS DATAFRAME
# ============================================================

events_df = pd.DataFrame(
    coordination_events
)


# ============================================================
# 5. USER EVENT COUNTS
# ============================================================

coordination_counts = {

    user: 0

    for user in G.nodes()

}


if len(events_df) > 0:

    for _, row in events_df.iterrows():

        coordination_counts[
            row["user1"]
        ] += 1

        coordination_counts[
            row["user2"]
        ] += 1


# ============================================================
# 6. GRAPH FEATURES
# ============================================================

degree = dict(
    G.degree()
)

weighted_degree = dict(
    G.degree(
        weight="weight"
    )
)


results = pd.DataFrame({

    "user_id":
        list(G.nodes()),

    "degree":
        [
            degree[u]
            for u in G.nodes()
        ],

    "weighted_degree":
        [
            weighted_degree[u]
            for u in G.nodes()
        ],

    "coordination_events":
        [
            coordination_counts[u]
            for u in G.nodes()
        ]

})


# ============================================================
# 7. COORDINATION SCORE
# ============================================================

max_events = (

    results[
        "coordination_events"
    ].max()

)


if max_events > 0:

    results[
        "coordination_score"
    ] = (

        results[
            "coordination_events"
        ]

        /

        max_events

    ) * 100

else:

    results[
        "coordination_score"
    ] = 0


results[
    "coordination_score"
] = results[
    "coordination_score"
].clip(
    0,
    100
)


# ============================================================
# 8. SAVE
# ============================================================

results.to_csv(
    "data/graph_features.csv",
    index=False
)

events_df.to_csv(
    "data/coordination_events.csv",
    index=False
)


# ============================================================
# 9. DISPLAY
# ============================================================

print()
print("======================================")
print("       COORDINATION ANALYSIS")
print("======================================")

print()

print(
    "Coordination events:",
    len(events_df)
)

print()

print(
    "Users involved:",
    sum(
        results[
            "coordination_events"
        ] > 0
    )
)

print()

print("Top coordinated users:")

print()

print(

    results[
        [
            "user_id",
            "degree",
            "weighted_degree",
            "coordination_events",
            "coordination_score"
        ]
    ]

    .sort_values(
        "coordination_score",
        ascending=False
    )

    .head(20)

    .to_string(
        index=False
    )

)

print()

print(
    "Saved:"
)

print(
    "data/graph_features.csv"
)

print(
    "data/coordination_events.csv"
)