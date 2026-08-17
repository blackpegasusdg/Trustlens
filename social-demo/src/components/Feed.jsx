import { useState, useEffect, useCallback } from "react";
import CreatePost from "./CreatePost";
import TrustLensDashboard from "./TrustLensDashboard";

const BACKEND_URL = "https://trustlens-9idp.onrender.com";

function Feed({ user, onLogout }) {

  // ============================================================
  // STATE
  // ============================================================

  const [posts, setPosts] = useState([]);

  const [showDashboard, setShowDashboard] = useState(false);

  const [loadingPosts, setLoadingPosts] = useState(true);


  // ============================================================
  // LOAD POSTS
  // ============================================================

  const loadPosts = useCallback(async () => {

    try {

      console.log("Loading posts from TrustLens backend...");

      const response = await fetch(
        `${BACKEND_URL}/posts`
      );

      if (!response.ok) {

        throw new Error(
          `Server returned ${response.status}`
        );

      }

      const backendPosts = await response.json();

      console.log(
        "Posts received:",
        backendPosts
      );


      // ========================================================
      // LOAD ANALYSIS
      // ========================================================

      let analysisData = [];

      try {

        const analysisResponse = await fetch(
          `${BACKEND_URL}/analysis`
        );

        if (analysisResponse.ok) {

          analysisData =
            await analysisResponse.json();

        }

      } catch (analysisError) {

        console.warn(
          "Could not load analysis:",
          analysisError
        );

      }


      // ========================================================
      // COMBINE POSTS + ANALYSIS
      // ========================================================

      const formattedPosts =
        backendPosts
          .map((post) => {

            const analysis =
              analysisData.find(
                (item) =>
                  String(item.post_id) ===
                  String(post.post_id)
              );


            return {

              id:
                post.post_id,

              user:
                post.user_id ||
                "Unknown",

              text:
                post.text ||
                "",

              likes:
                Number(post.likes) || 0,

              comments:
                Number(post.comments) || 0,

              timestamp:
                post.timestamp,

              analysis:
                analysis
                  ? {

                      spam_score:
                        Number(
                          analysis.spam_score
                        ) || 0,

                      duplicate_score:
                        Number(
                          analysis.duplicate_score
                        ) || 0,

                      risk_score:
                        Number(
                          analysis.risk_score
                        ) || 0,

                      risk_level:
                        analysis.risk_level ||
                        "LOW",

                      suspicious:
                        analysis.suspicious === true ||
                        String(
                          analysis.suspicious
                        ).toLowerCase() === "true"

                    }
                  : null

            };

          })
          // Newest posts first
          .reverse();


      setPosts(formattedPosts);


    } catch (error) {

      console.error(
        "Failed to load posts:",
        error
      );

    } finally {

      setLoadingPosts(false);

    }

  }, []);


  // ============================================================
  // INITIAL LOAD + AUTO REFRESH
  // ============================================================

  useEffect(() => {

    // Load immediately
    loadPosts();


    // Then check backend every 3 seconds
    const refreshInterval = setInterval(() => {

      console.log(
        "Refreshing TrustLens feed..."
      );

      loadPosts();

    }, 3000);


    // Stop timer when leaving Feed
    return () => {

      clearInterval(
        refreshInterval
      );

    };

  }, [loadPosts]);


  // ============================================================
  // CREATE POST
  // ============================================================

  const addPost = async (text) => {

    try {

      console.log(
        "Sending post to TrustLens:",
        {
          user,
          text
        }
      );


      const response = await fetch(
        `${BACKEND_URL}/posts`,
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


      const result =
        await response.json();


      console.log(
        "TrustLens backend response:",
        result
      );


      if (!response.ok) {

        throw new Error(
          result.message ||
          `Server returned ${response.status}`
        );

      }


      if (result.success === false) {

        throw new Error(
          result.message ||
          "TrustLens rejected the post"
        );

      }


      // ========================================================
      // DON'T ONLY ADD LOCALLY
      // REFRESH FROM BACKEND
      // ========================================================

      await loadPosts();


      return result;


    } catch (error) {

      console.error(
        "TrustLens backend connection error:",
        error
      );

      throw error;

    }

  };


  // ============================================================
  // LOGOUT
  // ============================================================

  const handleLogout = () => {

    onLogout();

  };


  // ============================================================
  // LOADING
  // ============================================================

  if (loadingPosts) {

    return (

      <div className="social-app">

        <main className="feed-container">

          <div className="loading">

            Loading TrustLens feed...

          </div>

        </main>

      </div>

    );

  }


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
              setShowDashboard(
                previous => !previous
              )
            }
          >

            {showDashboard
              ? "Back to Feed"
              : "TrustLens Analysis"}

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


            {/* ==================================================
                CREATE POST
            ================================================== */}

            <CreatePost
              onPost={addPost}
            />


            {/* ==================================================
                FEED TITLE
            ================================================== */}

            <h2 className="feed-title">

              Social Feed

            </h2>


            {/* ==================================================
                NO POSTS
            ================================================== */}

            {posts.length === 0 && (

              <div className="empty-feed">

                No posts yet.

              </div>

            )}


            {/* ==================================================
                POSTS
            ================================================== */}

            {posts.map((post) => (

              <div
                className="post-card"
                key={post.id}
              >


                {/* ==================================================
                    USER
                ================================================== */}

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


                {/* ==================================================
                    POST TEXT
                ================================================== */}

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

                      {post.analysis.spam_score ?? 0}

                    </div>


                    <div>

                      Duplicate Score:{" "}

                      {post.analysis.duplicate_score ?? 0}

                    </div>


                    <div>

                      Risk Score:{" "}

                      {post.analysis.risk_score ?? 0}

                    </div>


                    <div>

                      Risk Level:{" "}

                      {post.analysis.risk_level ??
                        "UNKNOWN"}

                    </div>


                    <div>

                      Status:{" "}

                      {post.analysis.suspicious === true

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

          /* ====================================================
             TRUSTLENS DASHBOARD
          ==================================================== */

          <TrustLensDashboard
            posts={posts}
          />

        )}

      </main>

    </div>

  );

}


export default Feed;