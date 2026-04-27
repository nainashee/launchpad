import { useState } from 'react';
import { decodeJob } from '../api';
import './AIPage.css';
import './JobDecoder.css';

export default function JobDecoder() {
  const [jobDescription, setJobDescription] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    setError(null);
    try {
      const res = await decodeJob(jobDescription);
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.error ?? 'Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <h1>Job Decoder</h1>
      <p className="page-desc">
        Paste any job posting and Claude will break it down — required skills,
        fit signals, red flags, and an overall match score.
      </p>

      <form onSubmit={handleSubmit} className="ai-form">
        <label htmlFor="jd">Job Posting</label>
        <textarea
          id="jd"
          rows={13}
          placeholder="Paste the full job posting here…"
          value={jobDescription}
          onChange={(e) => setJobDescription(e.target.value)}
          required
        />
        <div>
          <button type="submit" className="btn-primary" disabled={loading || !jobDescription.trim()}>
            {loading ? 'Decoding…' : 'Decode This Job'}
          </button>
        </div>
      </form>

      {error && <p className="error" style={{ marginTop: '1rem' }}>{error}</p>}

      {result && (
        <div className="result-box">
          <div className="result-header">
            <h2>Analysis</h2>
            {result.fitScore !== undefined && (
              <div className="fit-score">
                <span className="fit-score-label">Fit Score</span>
                <span className={`fit-score-value score-${Math.ceil(result.fitScore / 3)}`}>
                  {result.fitScore}/10
                </span>
              </div>
            )}
          </div>
          <div className="result-body">
            {result.summary && <p className="decode-summary">{result.summary}</p>}

            <div className="decode-grid">
              {result.requiredSkills?.length > 0 && (
                <div className="decode-section">
                  <h3>Required Skills</h3>
                  <ul>{result.requiredSkills.map((s, i) => <li key={i}>{s}</li>)}</ul>
                </div>
              )}
              {result.niceToHaves?.length > 0 && (
                <div className="decode-section">
                  <h3>Nice to Haves</h3>
                  <ul>{result.niceToHaves.map((s, i) => <li key={i}>{s}</li>)}</ul>
                </div>
              )}
              {result.keySignals?.length > 0 && (
                <div className="decode-section decode-positive">
                  <h3>Positive Signals</h3>
                  <ul>{result.keySignals.map((s, i) => <li key={i}>{s}</li>)}</ul>
                </div>
              )}
              {result.redFlags?.length > 0 && (
                <div className="decode-section decode-warning">
                  <h3>Red Flags</h3>
                  <ul>{result.redFlags.map((s, i) => <li key={i}>{s}</li>)}</ul>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
