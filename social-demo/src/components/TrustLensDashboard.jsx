import { useEffect, useState } from "react";

const API_URL = "https://trustlens-9idp.onrender.com";

function TrustLensDashboard({ posts = [] }) {

  const [livePosts, setLivePosts] = useState(posts);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // ============================================================
  // LOAD LIVE DATA FROM TRUSTLENS BACKEND
  // ============================================================

  const loadTrustLensData = async () => {

    try {

      setError("");

      const [postsResponse, analysisResponse] =
        await Promise.all([

          fetch(`${API_URL}/posts`),

          fetch(`${API_URL}/analysis`)

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


      const backendPosts =
        await postsResponse.json();

      const backendAnalysis =
        await analysisResponse.json();


      console.log(
        "TrustLens backend posts:",
        backendPosts
      );

      console.log(
        "TrustLens backend analysis:",
        backendAnalysis
      );


      // ========================================================
      // MERGE POSTS + ANALYSIS
      // ========================================================

      const mergedPosts = backendPosts.map(
        (post) => {

          const analysis =
            backendAnalysis.find(
              (item) =>
                String(item.post_id) ===
                String(post.post_id)
            );


          return {

            id:
              post.post_id,

            user:
              post.user_id,

            text:
              post.text,

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
                      ),

                    duplicate_score:
                      Number(
                        analysis.duplicate_score
                      ),

                    risk_score:
                      Number(
                        analysis.risk_score
                      ),

                    risk_level:
                      analysis.risk_level,

                    suspicious:
                      analysis.suspicious === true ||
                      String(
                        analysis.suspicious
                      ).toLowerCase() === "true"
                  }
                : null

          };

        }
      );


      setLivePosts(mergedPosts);


    } catch (err) {

      console.error(
        "TrustLens dashboard error:",
        err
      );

      setError(
        "Unable to load live TrustLens analysis."
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
  // REFRESH EVERY 5 SECONDS
  // ============================================================

  useEffect(() => {

    const interval = setInterval(
      loadTrustLensData,
      5000
    );

    return () => clearInterval(interval);

  }, []);


  // ============================================================
  // STATISTICS
  // ============================================================

  const totalPosts =
    livePosts.length;


  const analyzedPosts =
    livePosts.filter(
      (post) => post.analysis
    );


  const suspiciousPosts =
    analyzedPosts.filter(
      (post) =>
        post.analysis?.suspicious === true
    ).length;


  const safePosts =
    analyzedPosts.length -
    suspiciousPosts;


  // ============================================================
  // AVERAGE RISK
  // ============================================================

  const riskScores =
    analyzedPosts

      .map(
        (post) =>
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
          ) / riskScores.length
        )

      : 0;


  // ============================================================
  // OVERALL RISK
  // ============================================================

  let overallRisk =
    "LOW";


  if (averageRisk >= 70) {

    overallRisk =
      "HIGH";

  } else if (averageRisk >= 40) {

    overallRisk =
      "MEDIUM";

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
            Loading live TrustLens data...
          </p>

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
          ERROR
      ====================================================== */}

      {error && (

        <div className="analysis-card">

          <strong>
            ⚠️ {error}
          </strong>

        </div>

      )}


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

            Based on{" "}

            {analyzedPosts.length}

            {" "}analyzed post

            {analyzedPosts.length !== 1
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


        {livePosts.length === 0 && (

          <p>
            No posts available.
          </p>

        )}


        {livePosts.map(
          (post) => {

            const analysis =
              post.analysis;


            const suspicious =
              analysis?.suspicious === true;


            const riskScore =
              analysis?.risk_score ?? 0;


            const riskLevel =
              analysis?.risk_level ??
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
                        Spam Score:{" "}

                        <strong>
                          {analysis.spam_score}
                        </strong>

                      </div>


                      <div>
                        Duplicate Score:{" "}

                        <strong>
                          {analysis.duplicate_score}
                        </strong>

                      </div>


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

          }
        )}

      </div>

    </div>

  );

}

export default TrustLensDashboard;