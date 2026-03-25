import { useState } from 'react';
import API from '../services/api';

function AuthPage({ onLogin }) {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const clearForm = () => {
    setEmail('');
    setUsername('');
    setPassword('');
    setError('');
    setSuccess('');
  };

  const switchMode = () => {
    clearForm();
    setIsLogin(!isLogin);
  };

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
      setSuccess('Account created! Redirecting...');
      setTimeout(() => {
        switchMode();
      }, 1500);
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed');
    }
  };

  return (
    <div className={`auth-page ${isLogin ? 'login-mode' : 'register-mode'}`}>
      <div className="auth-forms-container">
        <div className="auth-form-container">
          <h2>{isLogin ? 'Welcome Back' : 'Create Account'}</h2>
          <p className="auth-subtitle">
            {isLogin ? 'Login to your account' : 'Join Vastarion Hunter'}
          </p>
          <form onSubmit={isLogin ? handleLogin : handleRegister}>
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            {!isLogin && (
              <input
                type="text"
                placeholder="Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />
            )}
            <input
              type="password"
              placeholder={isLogin ? 'Password' : 'Password (min 6 characters)'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <button type="submit">{isLogin ? 'Login' : 'Create Account'}</button>
            {error && <p className="error">{error}</p>}
            {success && <p className="success">{success}</p>}
          </form>
          <p className="switch-text">
            {isLogin ? "Don't have an account? " : 'Already have an account? '}
            <span onClick={switchMode} className="switch-link">
              {isLogin ? 'Register' : 'Login'}
            </span>
          </p>
        </div>
      </div>

      <div className="auth-overlay">
        <h1>Vastarion<br />Hunter</h1>
        <p>
          {isLogin
            ? 'Track prices across e-commerce platforms. Get notified when prices drop.'
            : 'Start tracking prices today. Never miss a deal again.'}
        </p>
      </div>
    </div>
  );
}

export default AuthPage;