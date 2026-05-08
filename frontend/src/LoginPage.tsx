import React, { useState } from 'react';
import { authAPI } from './api';

export default function LoginPage({ onLogin }: { onLogin: () => void }) {
  const [email, setEmail] = useState('admin@healthcare.com');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    setLoading(true);
    setError('');
    try {
      await authAPI.login(email, password);
      onLogin();
    } catch (e) {
      setError('Invalid email or password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh', display: 'flex', alignItems: 'center',
      justifyContent: 'center', background: '#f0f4f8'
    }}>
      <div style={{
        background: 'white', padding: '40px', borderRadius: '12px',
        boxShadow: '0 4px 20px rgba(0,0,0,0.1)', width: '380px'
      }}>
        <h2 style={{ marginBottom: '8px', color: '#1a365d' }}>
          Healthcare Analytics
        </h2>
        <p style={{ color: '#666', marginBottom: '24px' }}>
          Predictive Risk Stratification
        </p>
        {error && (
          <div style={{
            background: '#fee', color: '#c00', padding: '10px',
            borderRadius: '6px', marginBottom: '16px'
          }}>{error}</div>
        )}
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={e => setEmail(e.target.value)}
          style={{
            width: '100%', padding: '12px', marginBottom: '12px',
            border: '1px solid #ddd', borderRadius: '6px',
            fontSize: '14px', boxSizing: 'border-box'
          }}
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleLogin()}
          style={{
            width: '100%', padding: '12px', marginBottom: '20px',
            border: '1px solid #ddd', borderRadius: '6px',
            fontSize: '14px', boxSizing: 'border-box'
          }}
        />
        <button
          onClick={handleLogin}
          disabled={loading}
          style={{
            width: '100%', padding: '12px', background: '#2b6cb0',
            color: 'white', border: 'none', borderRadius: '6px',
            fontSize: '16px', cursor: 'pointer'
          }}
        >
          {loading ? 'Logging in...' : 'Login'}
        </button>
      </div>
    </div>
  );
}