import { useState } from 'react';
import { tailorResume } from '../api';
import './AIPage.css';
import './TailorResume.css';

export default function TailorResume() {
  const [jobDescription, setJobDescription] = useState('');
  const [resumeText, setResumeText] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    setError(null);
    try {
      const res = await tailorResume(jobDescription, resumeText);
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.error ?? 'Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <h1>Tailor Resume</h1>
      <p className="page-desc">
        Paste your master resume and a job description — Claude will reframe your
        experience to match the role's language and priorities.
      </p>

      <form onSubmit={handleSubmit} className="ai-form tailor-form">
        <div className="tailor-columns">
          <div className="tailor-col">
            <label htmlFor="resume">Your Resume</label>
            <textarea
              id="resume"
              rows={16}
              placeholder="Paste your full resume here…"
              value={resumeText}
              onChange={(e) => setResumeText(e.target.value)}
              required
            />
          </div>
          <div className="tailor-col">
            <label htmlFor="jd">Job Description</label>
            <textarea
              id="jd"
              rows={16}
              placeholder="Paste the full job description here…"
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              required
            />
          </div>
        </div>

        <div>
          <button
            type="submit"
            className="btn-primary"
            disabled={loading || !jobDescription.trim() || !resumeText.trim()}
          >
            {loading ? 'Tailoring resume…' : 'Tailor My Resume'}
          </button>
        </div>
      </form>

      {error && <p className="error" style={{ marginTop: '1rem' }}>{error}</p>}

      {result && (
        <div className="result-box">
          <div className="result-header">
            <h2>Tailored Resume</h2>
            {result.s3Key && <span className="s3-badge">Saved to S3</span>}
          </div>
          <div className="result-body">
            <pre className="result-pre">{result.tailoredResume}</pre>
          </div>
        </div>
      )}
    </div>
  );
}
