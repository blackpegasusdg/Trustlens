import { useState } from "react";
import CreatePost from "./CreatePost";
import TrustLensDashboard from "./TrustLensDashboard";

function Feed({ user, onLogout }) {

  const [posts, setPosts] = useState([
    {
      id: "initial-1",
      user: "Alex",
      text: "Amazing product! Everyone should try this.",
      likes: 24,
      comments: 5,
    },
    {
      id: "initial-2",
      user: "Rahul",
      text: "This news is completely unbelievable!",
      likes: 12,
      comments: 3,
    }
  ]);

  const [showDashboard, setShowDashboard] = useState(false);

  // ============================================================
  // SEND POST TO TRUSTLENS BACKEND
  // ============================================================

  const addPost = async (text) => {

    const response = await fetch(
      "http://127.0.0.1:8001/posts",
      {
        method: "POST",

        headers: {
          "Content-Type": "application/json"
        },

        body: JSON.stringify({
          user: user,
          text: text
        })
      }
    );

    if (!response.ok) {
      throw new Error(
        `TrustLens server returned ${response.status}`
      );
    }

    const result = await response.json();

    console.log(
      "TrustLens received post:",
      result
    );

    console.log(
      "TrustLens analysis:",
      result.analysis
    );

    // ============================================================
    // ADD POST TO SOCIAL FEED
    // ============================================================

    const newPost = {
      id: result.post_id || `POST_${Date.now()}`,

      user: user,

      text: text,

      likes: 0,

      comments: 0,

      analysis: result.analysis
    };

    setPosts((previousPosts) => [
      newPost,
      ...previousPosts
    ]);

    // Send result back to CreatePost
    return result;
  };


  // ============================================================
  // LOGOUT
  // ============================================================

  const handleLogout = () => {
    setPosts([]);
    onLogout();
  };


  // ============================================================
  // UI
  // ============================================================

  return (
    <div className="social-app">

      {/* ======================================================
          NAVBAR
      ====================================================== */}

      <header className="navbar">

        <div className="nav-logo">
          🔍 TrustLens
        </div>

        <div className="nav-user">

          <span>
            @{user}
          </span>

          <button
            className="dashboard-btn"
            onClick={() =>
              setShowDashboard((previous) => !previous)
            }
          >
            TrustLens Analysis
          </button>

          <button
            className="logout-btn"
            onClick={handleLogout}
          >
            Logout
          </button>

        </div>

      </header>


      {/* ======================================================
          MAIN
      ====================================================== */}

      <main className="feed-container">

        {!showDashboard ? (

          <>

            {/* CREATE POST */}

            <CreatePost
              onPost={addPost}
            />


            {/* FEED TITLE */}

            <h2 className="feed-title">
              Social Feed
            </h2>


            {/* ==================================================
                POSTS
            ================================================== */}

            {posts.map((post) => (

              <div
                className="post-card"
                key={post.id}
              >

                {/* USER */}

                <div className="post-header">

                  <div className="avatar">

                    {post.user
                      ? post.user[0].toUpperCase()
                      : "U"}

                  </div>

                  <div>

                    <strong>
                      {post.user}
                    </strong>

                    <span className="username">
                      @{post.user?.toLowerCase()}
                    </span>

                  </div>

                </div>


                {/* POST TEXT */}

                <p className="post-text">
                  {post.text}
                </p>


                {/* ==================================================
                    TRUSTLENS RESULT
                ================================================== */}

                {post.analysis && (

                  <div className="trustlens-result">

                    <strong>
                      🛡️ TrustLens Analysis
                    </strong>

                    <div>
                      Spam Score:{" "}
                      {post.analysis.spam_score}
                    </div>

                    <div>
                      Duplicate Score:{" "}
                      {post.analysis.duplicate_score}
                    </div>

                    <div>
                      Risk Score:{" "}
                      {post.analysis.risk_score}
                    </div>

                    <div>
                      Risk Level:{" "}
                      {post.analysis.risk_level}
                    </div>

                    <div>
                      Status:{" "}
                      {post.analysis.suspicious
                        ? "⚠️ SUSPICIOUS"
                        : "✅ SAFE"}
                    </div>

                  </div>

                )}


                {/* ==================================================
                    POST ACTIONS
                ================================================== */}

                <div className="post-actions">

                  <span>
                    ❤️ {post.likes}
                  </span>

                  <span>
                    💬 {post.comments}
                  </span>

                  <span>
                    ↗ Share
                  </span>

                </div>

              </div>

            ))}

          </>

        ) : (

          <TrustLensDashboard
            posts={posts}
          />

        )}

      </main>

    </div>
  );
}

export default Feed;