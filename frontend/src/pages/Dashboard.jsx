import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getApplications } from '../api';
import './Dashboard.css';

const STATUSES = {
  applied:   { label: 'Applied',    color: '#3d6b4a' },
  interview: { label: 'Interviews', color: '#b87333' },
  offer:     { label: 'Offers',     color: '#2d5238' },
  rejected:  { label: 'Rejected',   color: '#a04040' },
};

export default function Dashboard() {
  const [apps, setApps] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    getApplications()
      .then((res) => setApps(res.data.applications ?? []))
      .catch(() => setError('Could not load applications.'))
      .finally(() => setLoading(false));
  }, []);

  const counts = apps.reduce((acc, a) => {
    acc[a.status] = (acc[a.status] ?? 0) + 1;
    return acc;
  }, {});

  const recent = [...apps]
    .sort((a, b) => new Date(b.appliedDate) - new Date(a.appliedDate))
    .slice(0, 5);

  return (
    <div className="page">
      <h1>Dashboard</h1>

      {loading && <p className="muted">Loading…</p>}
      {error && <p className="error">{error}</p>}

      {!loading && !error && (
        <>
          <div className="stat-grid">
            <div className="stat-card" style={{ borderTopColor: 'var(--brown-300)' }}>
              <span className="stat-number">{apps.length}</span>
              <span className="stat-label">Total</span>
            </div>
            {Object.entries(STATUSES).map(([key, { label, color }]) => (
              <div className="stat-card" key={key} style={{ borderTopColor: color }}>
                <span className="stat-number">{counts[key] ?? 0}</span>
                <span className="stat-label">{label}</span>
              </div>
            ))}
          </div>

          <div className="section-header">
            <h2>Recent Applications</h2>
            <Link to="/applications">View all →</Link>
          </div>

          {recent.length === 0 ? (
            <div className="empty-state">
              <p>No applications tracked yet.</p>
              <Link to="/applications">Add your first one →</Link>
            </div>
          ) : (
            <table className="table">
              <thead>
                <tr>
                  <th>Company</th>
                  <th>Role</th>
                  <th>Status</th>
                  <th>Applied</th>
                </tr>
              </thead>
              <tbody>
                {recent.map((a) => (
                  <tr key={a.applicationId}>
                    <td>{a.companyName}</td>
                    <td>{a.roleTitle}</td>
                    <td>
                      <span className={`badge badge-${a.status}`}>{a.status}</span>
                    </td>
                    <td>{a.appliedDate ?? '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}

          <div className="quick-actions">
            <h2>Quick Actions</h2>
            <div className="action-grid">
              <Link to="/tailor" className="action-card">
                <span className="action-icon">✦</span>
                <span>Tailor Resume</span>
              </Link>
              <Link to="/decode" className="action-card">
                <span className="action-icon">⬡</span>
                <span>Decode a Job</span>
              </Link>
              <Link to="/outreach" className="action-card">
                <span className="action-icon">✉</span>
                <span>Generate Outreach</span>
              </Link>
              <Link to="/applications" className="action-card">
                <span className="action-icon">◈</span>
                <span>Track Application</span>
              </Link>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
