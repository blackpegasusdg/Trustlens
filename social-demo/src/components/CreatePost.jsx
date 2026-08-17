import { useState } from "react";

function CreatePost({ onPost }) {

  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {

    e.preventDefault();

    const postText = text.trim();

    if (!postText) {
      return;
    }

    setLoading(true);
    setError("");

    try {

      // Send post to Feed.jsx
      // Feed.jsx sends it to TrustLens backend
      const result = await onPost(postText);

      console.log(
        "TrustLens analysis:",
        result
      );

      // Clear textbox after successful post
      setText("");

    } catch (error) {

      console.error(
        "Post error:",
        error
      );

      setError(
        "Unable to connect to TrustLens. Make sure the backend is running on port 8001."
      );

    } finally {

      setLoading(false);

    }
  };

  return (
    <div className="create-post">

      <form onSubmit={handleSubmit}>

        <textarea
          value={text}
          onChange={(e) => {
            setText(e.target.value);
            setError("");
          }}
          placeholder="What's happening?"
          rows="3"
          disabled={loading}
        />

        <button
          type="submit"
          disabled={loading || !text.trim()}
        >
          {loading ? "Analyzing..." : "Post"}
        </button>

      </form>

      {error && (
        <div
          style={{
            marginTop: "10px",
            padding: "10px",
            borderRadius: "8px",
            background: "#3a1515",
            color: "#ff8f8f",
            fontSize: "13px"
          }}
        >
          ⚠️ {error}
        </div>
      )}

    </div>
  );
}

export default CreatePost;