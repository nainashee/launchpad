import { useState } from 'react';
import { decodeJob } from '../api';
import './AIPage.css';

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
      setError(err.response?.data?.message ?? 'Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <h1>Job Decoder</h1>
      <p className="page-desc">
        Paste any job posting and Claude will break it down — extracting must-have skills,
        fit signals, potential red flags, and your overall match score.
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
          </div>
          <div className="result-body">
            {result.fitScore !== undefined && (
              <div className="fit-score">
                <span className="fit-score-label">Fit Score</span>
                <span className="fit-score-value">{result.fitScore} / 10</span>
              </div>
            )}
            <pre className="result-pre">
              {result.analysis ?? JSON.stringify(result, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}
