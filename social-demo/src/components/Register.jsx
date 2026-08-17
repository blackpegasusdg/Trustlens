import { useState } from "react";

function Register({ onRegister, onLogin }) {

  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const submit = (e) => {
    e.preventDefault();

    if (!username || !email || !password) {
      alert("Please fill all fields");
      return;
    }

    onRegister(username);
  };

  return (
    <div className="auth-page">

      <div className="auth-card">

        <div className="logo">
          🔍 TrustLens
        </div>

        <p className="subtitle">
          Create your account
        </p>

        <h2>Register</h2>

        <form onSubmit={submit}>

          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) =>
              setUsername(e.target.value)
            }
          />

          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) =>
              setEmail(e.target.value)
            }
          />

          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) =>
              setPassword(e.target.value)
            }
          />

          <button className="primary-btn">
            Create Account
          </button>

        </form>

        <p className="switch-text">
          Already have an account?

          <button
            className="link-btn"
            onClick={onLogin}
          >
            Login
          </button>
        </p>

      </div>

    </div>
  );
}

export default Register;