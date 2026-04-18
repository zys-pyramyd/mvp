import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

// Premium styled component for the one‑time admin bootstrap
// Uses glassmorphism card with subtle gradient background and micro‑animations

const gradientBackground = {
  background: 'linear-gradient(135deg, hsl(210, 40%, 95%), hsl(210, 30%, 85%))',
  minHeight: '100vh',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
};

const cardStyle = {
  backdropFilter: 'blur(12px)',
  background: 'rgba(255,255,255,0.6)',
  borderRadius: '1rem',
  padding: '2rem',
  maxWidth: '420px',
  width: '100%',
  boxShadow: '0 8px 32px rgba(0,0,0,0.12)',
  transition: 'transform 0.2s ease',
};

const inputStyle = {
  width: '100%',
  padding: '0.75rem',
  marginBottom: '1rem',
  border: '1px solid #ccc',
  borderRadius: '0.5rem',
  fontSize: '1rem',
  background: 'rgba(255,255,255,0.9)',
  transition: 'border-color 0.2s',
};

const buttonStyle = {
  width: '100%',
  padding: '0.75rem',
  background: 'hsl(210, 70%, 50%)',
  color: '#fff',
  border: 'none',
  borderRadius: '0.5rem',
  fontSize: '1rem',
  cursor: 'pointer',
  transition: 'background 0.2s, transform 0.1s',
};

export default function CreateAdmin() {
  const [secret, setSecret] = useState('');
  const [status, setStatus] = useState(null);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus('loading');
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/setup/create-admin`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ setup_secret: secret.trim() }),
      });

      const data = await response.json();
      if (response.ok) {
        setStatus('success');
        // Brief pause then redirect to admin login
        setTimeout(() => navigate('/pyadmin'), 2000);
      } else {
        setStatus({ error: data.detail || 'Unexpected error' });
      }
    } catch (err) {
      setStatus({ error: err.message });
    }
  };

  return (
    <div style={gradientBackground}>
      <form style={cardStyle} onSubmit={handleSubmit} onMouseEnter={() => (cardStyle.transform = 'scale(1.02)')} onMouseLeave={() => (cardStyle.transform = 'scale(1)')}>
        <h2 style={{ textAlign: 'center', marginBottom: '1rem', fontFamily: 'Inter, sans-serif' }}>Create First Admin</h2>
        <p style={{ fontSize: '0.9rem', marginBottom: '1rem', color: '#333' }}>
          This page bootstraps the initial admin account. Provide the <strong>setup secret</strong> configured in your Render environment variables.
        </p>
        <input
          type="password"
          placeholder="Setup secret"
          value={secret}
          onChange={(e) => setSecret(e.target.value)}
          required
          style={inputStyle}
        />
        <button
          type="submit"
          style={buttonStyle}
          onMouseOver={(e) => (e.currentTarget.style.background = 'hsl(210, 70%, 45%)')}
          onMouseOut={(e) => (e.currentTarget.style.background = 'hsl(210, 70%, 50%)')}
          disabled={status === 'loading'}
        >
          {status === 'loading' ? 'Creating…' : 'Create Admin'}
        </button>
        {status && typeof status === 'object' && status.error && (
          <p style={{ color: 'red', marginTop: '1rem', textAlign: 'center' }}>{status.error}</p>
        )}
        {status === 'success' && (
          <p style={{ color: 'green', marginTop: '1rem', textAlign: 'center' }}>
            Admin created! Redirecting to login…
          </p>
        )}
      </form>
    </div>
  );
}
