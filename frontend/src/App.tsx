import React, { useState } from 'react';
import { login, logout, isAuthenticated } from './api';
import { Chat } from './components/Chat';

function LoginScreen({ onLogin }: { onLogin: () => void }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const success = await login(username, password);
      if (success) {
        onLogin();
      } else {
        setError('Invalid username or password');
      }
    } catch {
      setError('Connection failed. Check the server.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-screen">
      <div className="login-card">
        <div className="login-header">
          <h1>Hermes Gateway</h1>
          <p>AI Chat Orchestrator</p>
        </div>
        <form onSubmit={handleSubmit} className="login-form">
          {error && <div className="login-error">{error}</div>}
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter username"
              autoFocus
              disabled={loading}
            />
          </div>
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter password"
              disabled={loading}
            />
          </div>
          <button type="submit" className="login-btn" disabled={loading}>
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default function App() {
  const [authenticated, setAuthenticated] = useState(isAuthenticated);

  if (!authenticated) {
    return <LoginScreen onLogin={() => setAuthenticated(true)} />;
  }

  return (
    <div className="app-shell">
      <header className="app-header">
        <span className="app-title">Hermes Gateway</span>
        <button
          className="logout-btn"
          onClick={() => {
            logout();
            setAuthenticated(false);
          }}
        >
          Logout
        </button>
      </header>
      <main className="app-main">
        <ErrorBoundary>
          <Chat />
        </ErrorBoundary>
      </main>
    </div>
  );
}

class ErrorBoundary extends React.Component<{ children: React.ReactNode }, { error: string | null }> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { error: null };
  }
  static getDerivedStateFromError(error: Error) {
    return { error: error.message };
  }
  render() {
    if (this.state.error) {
      return (
        <div style={{ padding: 40, color: 'var(--text-primary)', textAlign: 'center' }}>
          <h2>Something went wrong</h2>
          <p style={{ color: 'var(--text-muted)', marginTop: 8 }}>{this.state.error}</p>
          <button onClick={() => window.location.reload()} style={{ marginTop: 16, padding: '8px 20px', background: 'var(--accent)', color: '#fff', border: 'none', borderRadius: 'var(--radius-sm)', cursor: 'pointer' }}>Reload</button>
        </div>
      );
    }
    return this.props.children;
  }
}
