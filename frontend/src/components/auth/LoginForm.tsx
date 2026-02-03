import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { loginStart, loginSuccess, loginFailure } from '../../store/slices/authSlice';
import { RootState } from '../../store';
import axios from '../../utils/axios';
import { getApiErrorMessage } from '../../utils/apiError';
import type { User } from '../../store/slices/authSlice';

interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

const LoginForm: React.FC = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { loading, error } = useSelector((state: RootState) => state.auth);

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    dispatch(loginStart());

    try {
      const { data } = await axios.post<LoginResponse>('/auth/login', { email, password });
      dispatch(loginSuccess({ user: data.user, token: data.access_token }));
      navigate('/dashboard');
    } catch (err: unknown) {
      dispatch(loginFailure(getApiErrorMessage(err, 'Login failed')));
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: '#f5f5f5',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    }}>
      <div style={{
        width: '100%',
        maxWidth: 400,
        padding: 32,
        background: '#fff',
        borderRadius: 8,
        boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
      }}>
        <h1 style={{ margin: '0 0 24px', fontSize: 24 }}>Sign In</h1>
        {error && (
          <div style={{ padding: 12, marginBottom: 16, background: '#ffebee', color: '#c62828', borderRadius: 4 }}>
            {error}
          </div>
        )}
        <form onSubmit={handleSubmit}>
          <label style={{ display: 'block', marginBottom: 4, fontWeight: 500 }}>Email Address *</label>
          <input
            type="email"
            name="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            autoComplete="email"
            style={{
              width: '100%',
              boxSizing: 'border-box',
              padding: '12px 14px',
              marginBottom: 16,
              border: '1px solid #ccc',
              borderRadius: 4,
              fontSize: 16,
            }}
          />
          <label style={{ display: 'block', marginBottom: 4, fontWeight: 500 }}>Password *</label>
          <input
            type="password"
            name="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
            style={{
              width: '100%',
              boxSizing: 'border-box',
              padding: '12px 14px',
              marginBottom: 24,
              border: '1px solid #ccc',
              borderRadius: 4,
              fontSize: 16,
            }}
          />
          <button
            type="submit"
            disabled={loading}
            style={{
              width: '100%',
              padding: 12,
              background: loading ? '#90a4ae' : '#1976d2',
              color: '#fff',
              border: 'none',
              borderRadius: 4,
              fontSize: 16,
              fontWeight: 500,
              cursor: loading ? 'not-allowed' : 'pointer',
            }}
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default LoginForm;
