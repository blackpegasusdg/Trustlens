import { useState } from "react";
import Login from "./components/Login";
import Register from "./components/Register";
import Feed from "./components/Feed";
import "./index.css";

function App() {
  const [page, setPage] = useState("login");
  const [user, setUser] = useState(null);

  const handleLogin = (username) => {
    setUser(username);
    setPage("feed");
  };

  const handleLogout = () => {
    setUser(null);
    setPage("login");
  };

  if (page === "login") {
    return (
      <Login
        onLogin={handleLogin}
        onRegister={() => setPage("register")}
      />
    );
  }

  if (page === "register") {
    return (
      <Register
        onRegister={handleLogin}
        onLogin={() => setPage("login")}
      />
    );
  }

  return (
    <Feed
      user={user}
      onLogout={handleLogout}
    />
  );
}

export default App;