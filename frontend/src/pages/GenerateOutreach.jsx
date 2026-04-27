import { useState } from 'react';
import { generateOutreach } from '../api';
import './AIPage.css';
import './GenerateOutreach.css';

const TYPES = [
  { value: 'linkedin', label: 'LinkedIn Message' },
  { value: 'email',    label: 'Email' },
];

export default function GenerateOutreach() {
  const [jobDescription, setJobDescription] = useState('');
  const [type, setType]                     = useState('linkedin');
  const [name, setName]                     = useState('');
  const [skills, setSkills]                 = useState('');
  const [result, setResult]                 = useState(null);
  const [loading, setLoading]               = useState(false);
  const [error, setError]                   = useState(null);
  const [copied, setCopied]                 = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    setError(null);
    setCopied(false);
    try {
      const res = await generateOutreach(jobDescription, type, name, skills);
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.error ?? 'Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    if (!result?.message) return;
    navigator.clipboard.writeText(result.message).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  return (
    <div className="page">
      <h1>Generate Outreach</h1>
      <p className="page-desc">
        Paste a job posting and Claude will write a genuine LinkedIn message or email
        that stands out — specific to the role, not generic.
      </p>

      <form onSubmit={handleSubmit} className="ai-form outreach-form">
        {/* Type toggle */}
        <div className="outreach-type-row">
          {TYPES.map((t) => (
            <label key={t.value} className={`type-pill${type === t.value ? ' active' : ''}`}>
              <input
                type="radio"
                name="outreachType"
                value={t.value}
                checked={type === t.value}
                onChange={() => setType(t.value)}
              />
              {t.label}
            </label>
          ))}
        </div>

        <label htmlFor="jd">Job Posting</label>
        <textarea
          id="jd"
          rows={10}
          placeholder="Paste the full job posting here…"
          value={jobDescription}
          onChange={(e) => setJobDescription(e.target.value)}
          required
        />

        <div className="outreach-extras">
          <div className="outreach-extra-field">
            <label htmlFor="name">Your Name <span className="optional">(optional)</span></label>
            <input
              id="name"
              type="text"
              placeholder="e.g. Hussain"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>
          <div className="outreach-extra-field">
            <label htmlFor="skills">Key Skills <span className="optional">(optional)</span></label>
            <input
              id="skills"
              type="text"
              placeholder="e.g. Python, AWS, React"
              value={skills}
              onChange={(e) => setSkills(e.target.value)}
            />
          </div>
        </div>

        <div>
          <button
            type="submit"
            className="btn-primary"
            disabled={loading || !jobDescription.trim()}
          >
            {loading ? 'Writing…' : `Write ${type === 'linkedin' ? 'LinkedIn Message' : 'Email'}`}
          </button>
        </div>
      </form>

      {error && <p className="error" style={{ marginTop: '1rem' }}>{error}</p>}

      {result && (
        <div className="result-box">
          <div className="result-header">
            <h2>{result.type === 'linkedin' ? 'LinkedIn Message' : 'Email Draft'}</h2>
            <button className="copy-btn" onClick={handleCopy}>
              {copied ? 'Copied!' : 'Copy'}
            </button>
          </div>
          <div className="result-body">
            <pre className="result-pre outreach-message">{result.message}</pre>
          </div>
        </div>
      )}
    </div>
  );
}
