import React, { useState } from "react";

function Login({ onLoginSuccess }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();

    try {
      // Make a POST request to your Django backend
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/login/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email,
            password,
          }),
        }
      );

      if (response.ok) {
        const result = await response.json();
        console.log("Login successful:", result);
        onLoginSuccess(); // Notify parent component about login success
      } else {
        const errorData = await response.json();
        console.error("Login failed:", errorData);
        setError(errorData.message || "Login failed. Please try again.");
      }
    } catch (err) {
      console.error("An error occurred:", err);
      setError("An error occurred. Please try again later.");
    }
  };

  return (
    <div>
      <h2>Login</h2>
      <form onSubmit={handleLogin}>
        <div>
          <label>Email:</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <div>
          <label>Password:</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <button type="submit">Login</button>
      </form>
      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}

export default Login;
