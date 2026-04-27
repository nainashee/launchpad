import { useState } from 'react';
import { NavLink } from 'react-router-dom';
import './Nav.css';

export default function Nav() {
  const [open, setOpen] = useState(false);

  const close = () => setOpen(false);

  return (
    <nav className="nav">
      <NavLink to="/" className="nav-logo" onClick={close}>
        Launch<span>Pad</span>
      </NavLink>

      {/* Desktop links */}
      <div className="nav-links">
        <NavLink to="/" end>Dashboard</NavLink>
        <NavLink to="/tailor">Tailor Resume</NavLink>
        <NavLink to="/decode">Job Decoder</NavLink>
        <NavLink to="/applications">Applications</NavLink>
      </div>

      {/* Hamburger button — mobile only */}
      <button
        className={`nav-hamburger${open ? ' is-open' : ''}`}
        onClick={() => setOpen((o) => !o)}
        aria-label="Toggle menu"
        aria-expanded={open}
      >
        <span />
        <span />
        <span />
      </button>

      {/* Mobile dropdown */}
      {open && (
        <div className="nav-drawer">
          <NavLink to="/" end onClick={close}>Dashboard</NavLink>
          <NavLink to="/tailor" onClick={close}>Tailor Resume</NavLink>
          <NavLink to="/decode" onClick={close}>Job Decoder</NavLink>
          <NavLink to="/applications" onClick={close}>Applications</NavLink>
        </div>
      )}
    </nav>
  );
}
