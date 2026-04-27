import { useState } from 'react';
import { tailorResume } from '../api';
import './AIPage.css';

export default function TailorResume() {
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
      const res = await tailorResume(jobDescription);
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.message ?? 'Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <h1>Tailor Resume</h1>
      <p className="page-desc">
        Paste a job description below and Claude will tailor your master resume to highlight
        the most relevant experience and skills for that role.
      </p>

      <form onSubmit={handleSubmit} className="ai-form">
        <label htmlFor="jd">Job Description</label>
        <textarea
          id="jd"
          rows={13}
          placeholder="Paste the full job description here…"
          value={jobDescription}
          onChange={(e) => setJobDescription(e.target.value)}
          required
        />
        <div>
          <button type="submit" className="btn-primary" disabled={loading || !jobDescription.trim()}>
            {loading ? 'Tailoring resume…' : 'Tailor My Resume'}
          </button>
        </div>
      </form>

      {error && <p className="error" style={{ marginTop: '1rem' }}>{error}</p>}

      {result && (
        <div className="result-box">
          <div className="result-header">
            <h2>Tailored Resume</h2>
          </div>
          <div className="result-body">
            {result.s3Key && (
              <p className="s3-key">Saved to S3: <code>{result.s3Key}</code></p>
            )}
            <pre className="result-pre">
              {result.tailoredResume ?? JSON.stringify(result, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}
