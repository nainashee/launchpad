import { useEffect, useState } from 'react';
import {
  getApplications,
  createApplication,
  updateApplication,
  deleteApplication,
} from '../api';
import './Applications.css';

const STATUSES = ['applied', 'interview', 'offer', 'rejected'];

const EMPTY_FORM = {
  companyName: '',
  roleTitle: '',
  status: 'applied',
  appliedDate: new Date().toISOString().split('T')[0],
  followUpDate: '',
};

export default function Applications() {
  const [apps, setApps] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(EMPTY_FORM);
  const [editingId, setEditingId] = useState(null);
  const [saving, setSaving] = useState(false);

  const load = () => {
    setLoading(true);
    getApplications()
      .then((res) => setApps(res.data.applications ?? []))
      .catch(() => setError('Could not load applications.'))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const openAdd = () => {
    setForm(EMPTY_FORM);
    setEditingId(null);
    setShowForm(true);
  };

  const openEdit = (app) => {
    setForm({
      companyName: app.companyName,
      roleTitle: app.roleTitle,
      status: app.status,
      appliedDate: app.appliedDate ?? '',
      followUpDate: app.followUpDate ?? '',
    });
    setEditingId(app.applicationId);
    setShowForm(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      if (editingId) {
        await updateApplication(editingId, form);
      } else {
        await createApplication({ ...form, userId: 'default' });
      }
      setShowForm(false);
      load();
    } catch {
      alert('Save failed. Check the console.');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this application?')) return;
    try {
      await deleteApplication(id);
      load();
    } catch {
      alert('Delete failed.');
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <h1>Applications</h1>
        <button className="btn-primary" onClick={openAdd}>+ Add Application</button>
      </div>

      {loading && <p className="muted">Loading…</p>}
      {error && <p className="error">{error}</p>}

      {showForm && (
        <div className="modal-overlay" onClick={() => setShowForm(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <p className="modal-title">{editingId ? 'Edit Application' : 'New Application'}</p>
            <form onSubmit={handleSubmit} className="app-form">
              <div className="form-row">
                <label>Company</label>
                <input
                  value={form.companyName}
                  onChange={(e) => setForm({ ...form, companyName: e.target.value })}
                  required
                  placeholder="Acme Corp"
                />
              </div>
              <div className="form-row">
                <label>Role</label>
                <input
                  value={form.roleTitle}
                  onChange={(e) => setForm({ ...form, roleTitle: e.target.value })}
                  required
                  placeholder="Senior Software Engineer"
                />
              </div>
              <div className="form-row">
                <label>Status</label>
                <select
                  value={form.status}
                  onChange={(e) => setForm({ ...form, status: e.target.value })}
                >
                  {STATUSES.map((s) => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
              </div>
              <div className="form-row">
                <label>Applied Date</label>
                <input
                  type="date"
                  value={form.appliedDate}
                  onChange={(e) => setForm({ ...form, appliedDate: e.target.value })}
                />
              </div>
              <div className="form-row">
                <label>Follow-up Date</label>
                <input
                  type="date"
                  value={form.followUpDate}
                  onChange={(e) => setForm({ ...form, followUpDate: e.target.value })}
                />
              </div>
              <div className="form-actions">
                <button type="button" className="btn-ghost" onClick={() => setShowForm(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary" disabled={saving}>
                  {saving ? 'Saving…' : 'Save'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {!loading && !error && apps.length === 0 && (
        <div className="apps-empty">
          <p>No applications tracked yet.</p>
          <p>Hit <strong>+ Add Application</strong> to get started.</p>
        </div>
      )}

      {apps.length > 0 && (
        <table className="table">
          <thead>
            <tr>
              <th>Company</th>
              <th>Role</th>
              <th>Status</th>
              <th>Applied</th>
              <th>Follow-up</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {apps.map((a) => (
              <tr key={a.applicationId}>
                <td>{a.companyName}</td>
                <td>{a.roleTitle}</td>
                <td>
                  <span className={`badge badge-${a.status}`}>{a.status}</span>
                </td>
                <td>{a.appliedDate ?? '—'}</td>
                <td>{a.followUpDate ?? '—'}</td>
                <td className="row-actions">
                  <button className="btn-ghost btn-sm" onClick={() => openEdit(a)}>Edit</button>
                  <button className="btn-danger btn-sm" onClick={() => handleDelete(a.applicationId)}>Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
