import { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Nav.css';

function TornadoIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 32 32" fill="none" aria-hidden="true" style={{ flexShrink: 0 }}>
      <path d="M6 5h20l-4 7H10L6 5z"          fill="#3d6b4a" opacity="0.9" />
      <path d="M10 12h12l-3 6H13l-3-6z"        fill="#3d6b4a" opacity="0.75" />
      <path d="M13 18h6l-2 5h-2l-2-5z"          fill="#3d6b4a" opacity="0.6" />
      <path d="M14.5 23h3l-1.5 4-1.5-4z"        fill="#3d6b4a" opacity="0.45" />
      <path d="M7 8q4-1 8 1"   stroke="#5a8f6a" strokeWidth="1.2" strokeLinecap="round" opacity="0.6" />
      <path d="M11 14.5q3-0.8 6 0.5" stroke="#5a8f6a" strokeWidth="1" strokeLinecap="round" opacity="0.5" />
    </svg>
  );
}

export default function Nav() {
  const [open, setOpen] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const { user, signOutUser } = useAuth();
  const navigate = useNavigate();

  const close = () => setOpen(false);

  const handleSignOut = async () => {
    setMenuOpen(false);
    await signOutUser();
    navigate('/');
  };

  return (
    <nav className="nav">
      <NavLink to="/dashboard" className="nav-logo" onClick={close}>
        <TornadoIcon />
        Launch<span>Pad</span>
      </NavLink>

      {/* Desktop links */}
      <div className="nav-links">
        <NavLink to="/dashboard">Dashboard</NavLink>
        <NavLink to="/tailor">Tailor Resume</NavLink>
        <NavLink to="/decode">Job Decoder</NavLink>
        <NavLink to="/outreach">Outreach</NavLink>
        <NavLink to="/applications">Applications</NavLink>
      </div>

      <div className="nav-right">
        {/* User avatar */}
        {user && (
          <div className="nav-user">
            <button
              className="nav-avatar-btn"
              onClick={() => setMenuOpen((o) => !o)}
              aria-label="User menu"
            >
              {user.photoURL ? (
                <img src={user.photoURL} alt={user.displayName} className="nav-avatar-img" />
              ) : (
                <span className="nav-avatar-fallback">
                  {user.displayName?.[0] ?? user.email?.[0] ?? '?'}
                </span>
              )}
            </button>

            {menuOpen && (
              <div className="nav-user-menu">
                <p className="nav-user-name">{user.displayName}</p>
                <p className="nav-user-email">{user.email}</p>
                <hr className="nav-user-divider" />
                <button className="nav-signout-btn" onClick={handleSignOut}>
                  Sign out
                </button>
              </div>
            )}
          </div>
        )}

        {/* Hamburger — mobile only */}
        <button
          className={`nav-hamburger${open ? ' is-open' : ''}`}
          onClick={() => setOpen((o) => !o)}
          aria-label="Toggle menu"
          aria-expanded={open}
        >
          <span /><span /><span />
        </button>
      </div>

      {/* Mobile drawer */}
      {open && (
        <div className="nav-drawer">
          <NavLink to="/dashboard"    onClick={close}>Dashboard</NavLink>
          <NavLink to="/tailor"       onClick={close}>Tailor Resume</NavLink>
          <NavLink to="/decode"       onClick={close}>Job Decoder</NavLink>
          <NavLink to="/outreach"     onClick={close}>Outreach</NavLink>
          <NavLink to="/applications" onClick={close}>Applications</NavLink>
          <button className="nav-drawer-signout" onClick={handleSignOut}>Sign out</button>
        </div>
      )}
    </nav>
  );
}
