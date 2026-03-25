import { useState } from 'react';
import API from '../services/api';

function Login({ onLogin, onSwitch }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);
      const response = await API.post('/auth/login', formData);
      localStorage.setItem('token', response.data.access_token);
      onLogin();
    } catch (err) {
      setError('Wrong email or password');
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-left">
        <h1>Vastarion<br />Hunter</h1>
        <p>Track prices across e-commerce platforms.<br />Get notified when prices drop.</p>
      </div>
      <div className="auth-right">
        <div className="auth-form-container">
          <h2>Welcome Back</h2>
          <p className="auth-subtitle">Login to your account</p>
          <form onSubmit={handleLogin}>
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <button type="submit">Login</button>
            {error && <p className="error">{error}</p>}
          </form>
          <p className="switch-text">
            Don't have an account? <span onClick={onSwitch} className="switch-link">Register</span>
          </p>
        </div>
      </div>
    </div>
  );
}

export default Login;