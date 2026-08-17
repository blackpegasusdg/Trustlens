import { useState } from "react";
import CreatePost from "./CreatePost";
import TrustLensDashboard from "./TrustLensDashboard";

const BACKEND_URL = "https://trustlens-9idp.onrender.com";

function Feed({ user, onLogout }) {

  const [posts, setPosts] = useState([
    {
      id: "initial-1",
      user: "Alex",
      text: "Amazing product! Everyone should try this.",
      likes: 24,
      comments: 5,
      analysis: null
    },
    {
      id: "initial-2",
      user: "Rahul",
      text: "This news is completely unbelievable!",
      likes: 12,
      comments: 3,
      analysis: null
    }
  ]);

  const [showDashboard, setShowDashboard] = useState(false);

  // ============================================================
  // SEND POST TO TRUSTLENS BACKEND
  // ============================================================

  const addPost = async (text) => {

    try {

      console.log("Sending post to TrustLens:", {
        user,
        text
      });

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

      // --------------------------------------------------------
      // READ RESPONSE
      // --------------------------------------------------------

      const result = await response.json();

      console.log(
        "TrustLens backend response:",
        result
      );

      // --------------------------------------------------------
      // HANDLE BACKEND ERROR
      // --------------------------------------------------------

      if (!response.ok) {

        throw new Error(
          result.message ||
          `TrustLens server returned ${response.status}`
        );

      }

      if (result.success === false) {

        throw new Error(
          result.message ||
          "TrustLens rejected the post"
        );

      }

      // --------------------------------------------------------
      // GET POST DATA
      // --------------------------------------------------------

      const backendPost =
        result.post || {};

      const analysis =
        result.analysis || null;


      console.log(
        "TrustLens analysis:",
        analysis
      );


      // --------------------------------------------------------
      // CREATE LOCAL POST OBJECT
      // --------------------------------------------------------

      const newPost = {

        id:
          backendPost.post_id ||
          result.post_id ||
          `POST_${Date.now()}`,

        user:
          backendPost.user_id ||
          user,

        text:
          backendPost.text ||
          text,

        likes: 0,

        comments: 0,

        analysis: analysis

      };


      console.log(
        "Adding post to social feed:",
        newPost
      );


      // --------------------------------------------------------
      // ADD TO FEED
      // --------------------------------------------------------

      setPosts((previousPosts) => [

        newPost,

        ...previousPosts

      ]);


      // --------------------------------------------------------
      // RETURN RESULT TO CREATE POST
      // --------------------------------------------------------

      return result;

    } catch (error) {

      console.error(
        "TrustLens backend connection error:",
        error
      );

      // Let CreatePost handle the error
      throw error;

    }

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
              setShowDashboard(
                (previous) => !previous
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

                      {post.analysis.risk_level ?? "UNKNOWN"}

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