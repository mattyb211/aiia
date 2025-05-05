import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

export default function Signup() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const nav = useNavigate();

  const handle = async () => {
    await api.post('/auth/signup', { name, email, password });
    nav('/login');
  };

  return (
    <div className="h-screen flex items-center justify-center">
      <div className="card w-80 space-y-4">
        <h1 className="text-xl">Sign Up</h1>
        <input
          className="input"
          placeholder="Full Name"
          value={name}
          onChange={e => setName(e.target.value)}
        />
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
          Create Account
        </button>
        <p>
          Have one?{' '}
          <a className="text-primary-600" href="/login">
            Login
          </a>
        </p>
      </div>
    </div>
  );
}