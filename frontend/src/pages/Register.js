import { useState } from 'react';
import API from '../services/api';

function Register({ onSwitch }) {
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    try {
      await API.post('/auth/register', {
        email: email,
        username: username,
        password: password,
      });
      setSuccess('Account created! Redirecting to login...');
      setTimeout(() => onSwitch(), 2000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed');
    }
  };

  return (
    <div className="auth-page register-page">
      <div className="auth-left">
        <h1>Vastarion<br />Hunter</h1>
        <p>Start tracking prices today.<br />Never miss a deal again.</p>
      </div>
      <div className="auth-right">
        <div className="auth-form-container">
          <h2>Create Account</h2>
          <p className="auth-subtitle">Join Vastarion Hunter</p>
          <form onSubmit={handleRegister}>
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <input
              type="text"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
            <input
              type="password"
              placeholder="Password (min 6 characters)"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <button type="submit">Create Account</button>
            {error && <p className="error">{error}</p>}
            {success && <p className="success">{success}</p>}
          </form>
          <p className="switch-text">
            Already have an account? <span onClick={onSwitch} className="switch-link">Login</span>
          </p>
        </div>
      </div>
    </div>
  );
}

export default Register;