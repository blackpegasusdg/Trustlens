function TrustLensDashboard({ posts }) {

  const totalPosts = posts.length;

  // Only posts that have actually been analyzed
  const analyzedPosts = posts.filter(
    (post) => post.analysis
  );

  // Posts marked suspicious by TrustLens
  const suspiciousPosts = analyzedPosts.filter(
    (post) =>
      post.analysis?.suspicious === true
  ).length;

  const safePosts = analyzedPosts.length - suspiciousPosts;

  // Calculate average risk score
  const riskScores = analyzedPosts
    .map((post) =>
      Number(post.analysis?.risk_score)
    )
    .filter((score) => !isNaN(score));

  const averageRisk =
    riskScores.length > 0
      ? Math.round(
          riskScores.reduce(
            (sum, score) => sum + score,
            0
          ) / riskScores.length
        )
      : 0;

  // Overall risk level
  let overallRisk = "LOW";

  if (averageRisk >= 70) {
    overallRisk = "HIGH";
  } else if (averageRisk >= 40) {
    overallRisk = "MEDIUM";
  }

  return (
    <div className="dashboard">

      {/* =====================================================
          HEADER
      ===================================================== */}

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


      {/* =====================================================
          STATISTICS
      ===================================================== */}

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


      {/* =====================================================
          DETECTION PIPELINE
      ===================================================== */}

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


      {/* =====================================================
          OVERALL RISK
      ===================================================== */}

      <div className="analysis-card">

        <h2>
          Overall TrustLens Risk
        </h2>

        <div className="overall-risk">

          <strong>
            {overallRisk}
          </strong>

          <p>
            Based on {analyzedPosts.length} analyzed post
            {analyzedPosts.length !== 1 ? "s" : ""}
          </p>

        </div>

      </div>


      {/* =====================================================
          RECENT RESULTS
      ===================================================== */}

      <div className="analysis-card">

        <h2>
          Recent Detection Results
        </h2>

        {posts.length === 0 && (

          <p>
            No posts available.
          </p>

        )}


        {posts.map((post) => {

          const analysis = post.analysis;

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

              {/* POST INFORMATION */}

              <div>

                <strong>
                  {post.user}
                </strong>

                <p>
                  {post.text}
                </p>

              </div>


              {/* TRUSTLENS RESULT */}

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

    </div>
  );
}

export default TrustLensDashboard;