import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Landing.css';

const FEATURES = [
  {
    icon: '✦',
    title: 'Tailor Your Resume',
    desc: 'Claude rewrites your resume to match each job\'s language and priorities — in seconds.',
  },
  {
    icon: '⬡',
    title: 'Decode Any Job',
    desc: 'Paste a posting and get required skills, red flags, and a fit score before you apply.',
  },
  {
    icon: '✉',
    title: 'Generate Outreach',
    desc: 'Craft genuine LinkedIn and email messages that don\'t sound like everyone else\'s.',
  },
  {
    icon: '◈',
    title: 'Track Applications',
    desc: 'One place for every application — status, follow-up dates, and fit scores.',
  },
];

export default function Landing() {
  const { signInWithGoogle } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState(null);

  const handleSignIn = async () => {
    setLoading(true);
    setError(null);
    try {
      await signInWithGoogle();
      navigate('/dashboard');
    } catch (err) {
      setError('Sign-in failed. Please try again.');
      setLoading(false);
    }
  };

  return (
    <div className="landing">
      {/* Hero */}
      <header className="landing-hero">
        <div className="landing-hero-inner">
          <div className="landing-logo">Launch<span>Pad</span></div>
          <h1 className="landing-headline">
            Your job search,<br />powered by AI.
          </h1>
          <p className="landing-sub">
            Stop sending generic applications. LaunchPad uses Claude to tailor your
            resume, decode job postings, and draft outreach — so every application
            feels personal and lands stronger.
          </p>

          <button
            className="btn-google"
            onClick={handleSignIn}
            disabled={loading}
          >
            <GoogleIcon />
            {loading ? 'Signing in…' : 'Sign in with Google'}
          </button>

          {error && <p className="landing-error">{error}</p>}
        </div>
      </header>

      {/* Features */}
      <section className="landing-features">
        <p className="landing-features-label">What's inside</p>
        <div className="landing-feature-grid">
          {FEATURES.map((f) => (
            <div className="landing-feature-card" key={f.title}>
              <span className="landing-feature-icon">{f.icon}</span>
              <h3>{f.title}</h3>
              <p>{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="landing-footer">
        Built by Hussain · Powered by Claude on AWS Bedrock
      </footer>
    </div>
  );
}

function GoogleIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
      <path d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844c-.209 1.125-.843 2.078-1.796 2.717v2.258h2.908c1.702-1.567 2.684-3.875 2.684-6.615z" fill="#4285F4"/>
      <path d="M9 18c2.43 0 4.467-.806 5.956-2.184l-2.908-2.258c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332A8.997 8.997 0 009 18z" fill="#34A853"/>
      <path d="M3.964 10.707A5.41 5.41 0 013.682 9c0-.593.102-1.17.282-1.707V4.961H.957A8.996 8.996 0 000 9c0 1.452.348 2.827.957 4.039l3.007-2.332z" fill="#FBBC05"/>
      <path d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0A8.997 8.997 0 00.957 4.961L3.964 7.293C4.672 5.166 6.656 3.58 9 3.58z" fill="#EA4335"/>
    </svg>
  );
}
