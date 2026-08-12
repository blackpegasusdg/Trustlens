import streamlit as st


def show_attack_lab():
    st.title("🧪 Controlled Attack Lab")
    st.write(
        "Simulate controlled manipulation attacks and test how well "
        "TrustLens detects them."
    )

    st.divider()

    attack_type = st.selectbox(
        "Select Attack Type",
        [
            "🤖 Bot Attack",
            "💬 Fake Comment Attack",
            "⭐ Fake Rating Attack",
        ]
    )

    st.subheader("⚙️ Attack Configuration")

    col1, col2 = st.columns(2)

    with col1:
        attackers = st.number_input(
            "Number of Attackers",
            min_value=1,
            max_value=500,
            value=20,
            step=1
        )

        target_items = st.number_input(
            "Target Items",
            min_value=1,
            max_value=100,
            value=10,
            step=1
        )

    with col2:
        intensity = st.slider(
            "Attack Intensity",
            min_value=10,
            max_value=100,
            value=80,
            step=5
        )

        coordination = st.slider(
            "Coordination Level",
            min_value=0,
            max_value=100,
            value=80,
            step=5
        )

    st.divider()

    if attack_type == "🤖 Bot Attack":

        st.subheader("🤖 Bot Attack Settings")

        rating_direction = st.radio(
            "Rating Behaviour",
            [
                "Positive manipulation (5 stars)",
                "Negative manipulation (1 star)",
                "Mixed ratings"
            ]
        )

        ratings_per_bot = st.number_input(
            "Ratings per Bot",
            min_value=1,
            max_value=100,
            value=5,
            step=1
        )

        st.info(
            "This attack creates coordinated bot accounts that interact "
            "with selected items."
        )

    elif attack_type == "💬 Fake Comment Attack":

        st.subheader("💬 Comment Attack Settings")

        comment_type = st.selectbox(
            "Comment Attack Type",
            [
                "Exact Duplicate",
                "Near Duplicate",
                "Spam",
                "Coordinated Comments",
                "Mixed Attack"
            ]
        )

        fake_comments = st.number_input(
            "Number of Fake Comments",
            min_value=1,
            max_value=1000,
            value=100,
            step=10
        )

        st.info(
            "This attack creates artificial comments designed to simulate "
            "review manipulation."
        )

    else:

        st.subheader("⭐ Rating Attack Settings")

        rating_value = st.radio(
            "Attack Rating",
            [
                "5 Stars",
                "1 Star",
                "Mixed"
            ]
        )

        fake_ratings = st.number_input(
            "Number of Fake Ratings",
            min_value=1,
            max_value=1000,
            value=60,
            step=10
        )

        st.info(
            "This attack creates coordinated rating manipulation against "
            "selected items."
        )

    st.divider()

    st.subheader("🚀 Launch Simulation")

    launch = st.button(
        "🚀 LAUNCH CONTROLLED ATTACK",
        use_container_width=True,
        type="primary"
    )

    if launch:

        st.session_state["attack_config"] = {
            "attack_type": attack_type,
            "attackers": attackers,
            "target_items": target_items,
            "intensity": intensity,
            "coordination": coordination
        }

        if attack_type == "🤖 Bot Attack":

            st.session_state["attack_config"].update({
                "rating_direction": rating_direction,
                "ratings_per_bot": ratings_per_bot
            })

        elif attack_type == "💬 Fake Comment Attack":

            st.session_state["attack_config"].update({
                "comment_type": comment_type,
                "fake_comments": fake_comments
            })

        else:

            st.session_state["attack_config"].update({
                "rating_value": rating_value,
                "fake_ratings": fake_ratings
            })

        st.success("Attack configuration created successfully.")

        st.json(st.session_state["attack_config"])

        st.warning(
            "Simulation controller is ready. The next step is connecting "
            "this configuration to your existing attack simulator."
        )