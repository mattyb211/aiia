import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { useAuth } from '../AuthContext';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login } = useAuth();
  const nav = useNavigate();

  const handle = async () => {
    const res = await api.post('/auth/login', { email, password });
    login(res.data.access_token);
    nav('/');
  };

  return (
    <div className="h-screen flex items-center justify-center">
      <div className="card w-80 space-y-4">
        <h1 className="text-xl">Login</h1>
        <input
          className="input"
          placeholder="Email"
          value={email}
          onChange={e => setEmail(e.target.value)}
        />
        <input
          className="input"
          type="password"
          placeholder="Password"
          value={password}
          onChange={e => setPassword(e.target.value)}
        />
        <button className="btn btn-primary w-full" onClick={handle}>
          Sign In
        </button>
        <p>
          No account?{' '}
          <a className="text-primary-600" href="/signup">
            Sign up
          </a>
        </p>
      </div>
    </div>
  );
}

