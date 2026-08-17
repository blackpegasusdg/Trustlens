import { useState } from "react";

function Login({ onLogin, onRegister }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const submit = (e) => {
    e.preventDefault();

    if (!username || !password) {
      alert("Please enter username and password");
      return;
    }

    onLogin(username);
  };

  return (
    <div className="auth-page">
      <div className="auth-card">

        <div className="logo">
          🔍 TrustLens
        </div>

        <p className="subtitle">
          Social Media Authenticity & Security Platform
        </p>

        <h2>Welcome Back</h2>

        <form onSubmit={submit}>

          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />

          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          <button className="primary-btn">
            Login
          </button>

        </form>

        <p className="switch-text">
          Don't have an account?
          <button
            className="link-btn"
            onClick={onRegister}
          >
            Register
          </button>
        </p>

      </div>
    </div>
  );
}

export default Login;