import { useState } from 'react';
import AuthPage from './pages/AuthPage';
import Dashboard from './pages/Dashboard';
import './App.css';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(
    localStorage.getItem('token') ? true : false
  );

  if (isLoggedIn) {
    return <Dashboard onLogout={() => setIsLoggedIn(false)} />;
  }

  return <AuthPage onLogin={() => setIsLoggedIn(true)} />;
}

export default App;