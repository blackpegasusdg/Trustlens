import { useEffect, useState } from "react";

const BACKEND_URL = "https://trustlens-9idp.onrender.com";

function TrustLensDashboard({ posts = [] }) {

  const [backendPosts, setBackendPosts] = useState([]);
  const [backendAnalysis, setBackendAnalysis] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // ============================================================
  // LOAD DATA FROM TRUSTLENS BACKEND
  // ============================================================

  const loadTrustLensData = async () => {

    try {

      setLoading(true);
      setError("");

      console.log("Loading TrustLens data...");

      const [postsResponse, analysisResponse] =
        await Promise.all([
          fetch(`${BACKEND_URL}/posts`),
          fetch(`${BACKEND_URL}/analysis`)
        ]);

      if (!postsResponse.ok) {
        throw new Error(
          `Posts API returned ${postsResponse.status}`
        );
      }

      if (!analysisResponse.ok) {
        throw new Error(
          `Analysis API returned ${analysisResponse.status}`
        );
      }

      const postsData =
        await postsResponse.json();

      const analysisData =
        await analysisResponse.json();

      console.log(
        "TrustLens backend posts:",
        postsData
      );

      console.log(
        "TrustLens backend analysis:",
        analysisData
      );

      setBackendPosts(
        Array.isArray(postsData)
          ? postsData
          : []
      );

      setBackendAnalysis(
        Array.isArray(analysisData)
          ? analysisData
          : []
      );

    } catch (err) {

      console.error(
        "TrustLens dashboard error:",
        err
      );

      setError(
        err.message ||
        "Unable to connect to TrustLens backend"
      );

    } finally {

      setLoading(false);

    }

  };


  // ============================================================
  // LOAD WHEN DASHBOARD OPENS
  // ============================================================

  useEffect(() => {

    loadTrustLensData();

  }, []);


  // ============================================================
  // COMBINE POSTS + ANALYSIS
  // ============================================================

  const analyzedPosts = backendPosts.map((post) => {

    const analysis =
      backendAnalysis.find(
        (item) =>
          String(item.post_id) ===
          String(post.post_id)
      );

    return {

      id: post.post_id,

      user:
        post.user_id || "Unknown",

      text:
        post.text || "",

      likes:
        Number(post.likes || 0),

      comments:
        Number(post.comments || 0),

      analysis: analysis || null

    };

  });


  // ============================================================
  // FALLBACK TO LOCAL POSTS
  // ============================================================

  const displayPosts =
    analyzedPosts.length > 0
      ? analyzedPosts
      : posts;


  // ============================================================
  // STATISTICS
  // ============================================================

  const totalPosts =
    displayPosts.length;


  const analyzed =
    displayPosts.filter(
      (post) => post.analysis
    );


  const suspiciousPosts =
    analyzed.filter(
      (post) =>
        post.analysis?.suspicious === true ||
        post.analysis?.suspicious === "true"
    ).length;


  const safePosts =
    analyzed.length -
    suspiciousPosts;


  const riskScores =
    analyzed
      .map((post) =>
        Number(
          post.analysis?.risk_score
        )
      )
      .filter(
        (score) =>
          !isNaN(score)
      );


  const averageRisk =
    riskScores.length > 0
      ? Math.round(
          riskScores.reduce(
            (sum, score) =>
              sum + score,
            0
          ) /
          riskScores.length
        )
      : 0;


  // ============================================================
  // OVERALL RISK
  // ============================================================

  let overallRisk = "LOW";

  if (averageRisk >= 70) {

    overallRisk = "HIGH";

  } else if (averageRisk >= 40) {

    overallRisk = "MEDIUM";

  }


  // ============================================================
  // LOADING
  // ============================================================

  if (loading) {

    return (

      <div className="dashboard">

        <div className="analysis-card">

          <h2>
            TrustLens Analysis
          </h2>

          <p>
            🔄 Loading live TrustLens data...
          </p>

        </div>

      </div>

    );

  }


  // ============================================================
  // ERROR
  // ============================================================

  if (error) {

    return (

      <div className="dashboard">

        <div className="analysis-card">

          <h2>
            TrustLens Analysis
          </h2>

          <p>
            ⚠️ {error}
          </p>

          <button
            onClick={loadTrustLensData}
          >
            Retry
          </button>

        </div>

      </div>

    );

  }


  // ============================================================
  // UI
  // ============================================================

  return (

    <div className="dashboard">


      {/* ======================================================
          HEADER
      ====================================================== */}

      <div className="dashboard-header">

        <div>

          <h1>
            TrustLens Analysis
          </h1>

          <p>
            AI-powered social media authenticity monitoring
          </p>

        </div>

        <div className="status">

          ● LIVE ANALYSIS

        </div>

      </div>


      {/* ======================================================
          STATISTICS
      ====================================================== */}

      <div className="stats-grid">


        <div className="stat-card">

          <span>
            Total Posts
          </span>

          <strong>
            {totalPosts}
          </strong>

        </div>


        <div className="stat-card suspicious">

          <span>
            Suspicious Posts
          </span>

          <strong>
            {suspiciousPosts}
          </strong>

        </div>


        <div className="stat-card safe">

          <span>
            Normal Posts
          </span>

          <strong>
            {safePosts}
          </strong>

        </div>


        <div className="stat-card">

          <span>
            Average Risk
          </span>

          <strong>
            {averageRisk}
          </strong>

        </div>

      </div>


      {/* ======================================================
          DETECTION PIPELINE
      ====================================================== */}

      <div className="analysis-card">

        <h2>
          Detection Pipeline
        </h2>

        <div className="pipeline">

          <div>
            <b>01</b>
            <span>
              Content Collection
            </span>
          </div>

          <div>
            <b>02</b>
            <span>
              Text Analysis
            </span>
          </div>

          <div>
            <b>03</b>
            <span>
              Behavior Analysis
            </span>
          </div>

          <div>
            <b>04</b>
            <span>
              Coordination Detection
            </span>
          </div>

          <div>
            <b>05</b>
            <span>
              Risk Scoring
            </span>
          </div>

        </div>

      </div>


      {/* ======================================================
          OVERALL RISK
      ====================================================== */}

      <div className="analysis-card">

        <h2>
          Overall TrustLens Risk
        </h2>

        <div className="overall-risk">

          <strong>
            {overallRisk}
          </strong>

          <p>
            Based on {analyzed.length} analyzed post
            {analyzed.length !== 1
              ? "s"
              : ""}
          </p>

        </div>

      </div>


      {/* ======================================================
          RECENT RESULTS
      ====================================================== */}

      <div className="analysis-card">

        <h2>
          Recent Detection Results
        </h2>


        {displayPosts.length === 0 && (

          <p>
            No posts available.
          </p>

        )}


        {displayPosts.map((post) => {

          const analysis =
            post.analysis;


          const suspicious =
            analysis?.suspicious === true ||
            analysis?.suspicious === "true";


          const riskScore =
            Number(
              analysis?.risk_score || 0
            );


          const riskLevel =
            analysis?.risk_level ||
            "NOT ANALYZED";


          return (

            <div
              className="result-row"
              key={post.id}
            >


              {/* POST */}

              <div>

                <strong>
                  {post.user}
                </strong>

                <p>
                  {post.text}
                </p>

              </div>


              {/* ANALYSIS */}

              <div className="result-analysis">

                {analysis ? (

                  <>

                    <div>

                      Risk Score:{" "}

                      <strong>
                        {riskScore}
                      </strong>

                    </div>


                    <div>

                      Risk Level:{" "}

                      <strong>
                        {riskLevel}
                      </strong>

                    </div>


                    <div>

                      Spam Score:{" "}

                      <strong>
                        {analysis.spam_score ?? 0}
                      </strong>

                    </div>


                    <div>

                      Duplicate Score:{" "}

                      <strong>
                        {analysis.duplicate_score ?? 0}
                      </strong>

                    </div>


                    <div
                      className={
                        suspicious
                          ? "risk-badge medium"
                          : "risk-badge low"
                      }
                    >

                      {suspicious
                        ? "⚠️ SUSPICIOUS"
                        : "✅ SAFE"}

                    </div>

                  </>

                ) : (

                  <div className="risk-badge">

                    NOT ANALYZED

                  </div>

                )}

              </div>

            </div>

          );

        })}


      </div>


      {/* ======================================================
          REFRESH
      ====================================================== */}

      <div
        style={{
          marginTop: "20px",
          textAlign: "center"
        }}
      >

        <button
          onClick={loadTrustLensData}
        >
          🔄 Refresh TrustLens Data
        </button>

      </div>

    </div>

  );

}

export default TrustLensDashboard;