import React, { useState } from 'react';
import { ApiService } from '../services/api';

interface OptimizationPageProps {
  resumeData: {
    text: string;
    parsed?: any;
  };
  onSubmit: (data: any) => void;
  onBack: () => void;
}

export default function OptimizationPage({ resumeData, onSubmit, onBack }: OptimizationPageProps) {
  const [jobDescription, setJobDescription] = useState('');
  const [autoIterate, setAutoIterate] = useState(true);
  const [targetScore, setTargetScore] = useState(85);
  const [maxIterations, setMaxIterations] = useState(5);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showScore, setShowScore] = useState(false);
  const [scoreData, setScoreData] = useState<any>(null);

  const handleScoreResume = async () => {
    if (!jobDescription.trim()) {
      setError('Please provide a job description');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const result = await ApiService.scoreResume(resumeData.text, jobDescription);
      setScoreData(result.score);
      setShowScore(true);
      setLoading(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to score resume');
      setLoading(false);
    }
  };

  const handleOptimize = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!jobDescription.trim()) {
      setError('Please provide a job description');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const result = await ApiService.optimizeResume(
        resumeData.text,
        jobDescription,
        autoIterate,
        targetScore,
        maxIterations
      );

      onSubmit(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to optimize resume');
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <h2 className="page-title">Step 2: Add Job Description & Optimize</h2>
        <p className="page-description">
          Paste the job description you're applying for. We'll analyze it and optimize your resume to match.
        </p>
      </div>

      {error && (
        <div className="alert alert-error">
          <span className="alert-icon">⚠️</span>
          <span className="alert-text">{error}</span>
        </div>
      )}

      <form onSubmit={handleOptimize} className="form">
        {/* Job Description Input */}
        <div className="form-group">
          <label className="form-label">Job Description *</label>
          <textarea
            className="form-textarea"
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            placeholder="Paste the complete job description here..."
            disabled={loading}
            style={{ minHeight: '200px' }}
          />
          <p className="form-hint">
            {jobDescription.length} characters
          </p>
        </div>

        {/* Score Preview Button */}
        <div className="form-group">
          <button
            type="button"
            className="btn btn-secondary"
            onClick={handleScoreResume}
            disabled={loading || !jobDescription.trim()}
          >
            {loading && showScore ? 'Calculating...' : 'Preview Score'}
          </button>
        </div>

        {/* Score Display */}
        {showScore && scoreData && (
          <div className="score-container">
            <div className="score-card">
              <div className="score-label">Current ATS Score</div>
              <div className="score-value">{scoreData.total_score}</div>
              <div className="score-bar">
                <div
                  className="score-fill"
                  style={{ width: `${scoreData.total_score}%` }}
                />
              </div>
            </div>

            <div className="score-card">
              <div className="score-label">Keyword Match</div>
              <div className="score-value">{scoreData.keyword_match}</div>
              <div className="score-bar">
                <div
                  className="score-fill"
                  style={{ width: `${scoreData.keyword_match}%` }}
                />
              </div>
            </div>

            <div className="score-card">
              <div className="score-label">Required Keywords</div>
              <div className="score-value">{scoreData.required_match}</div>
              <div className="score-bar">
                <div
                  className="score-fill"
                  style={{ width: `${scoreData.required_match}%` }}
                />
              </div>
            </div>

            <div className="score-card">
              <div className="score-label">Formatting</div>
              <div className="score-value">{scoreData.formatting}</div>
              <div className="score-bar">
                <div
                  className="score-fill"
                  style={{ width: `${scoreData.formatting}%` }}
                />
              </div>
            </div>
          </div>
        )}

        {/* Optimization Settings */}
        <div style={{ backgroundColor: '#f8f9fa', padding: '24px', borderRadius: '8px', marginBottom: '24px' }}>
          <h3 style={{ marginBottom: '16px', color: '#2c3e50' }}>Optimization Settings</h3>

          <div className="form-group">
            <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={autoIterate}
                onChange={(e) => setAutoIterate(e.target.checked)}
                disabled={loading}
                style={{ width: '18px', height: '18px', cursor: 'pointer' }}
              />
              <span style={{ fontWeight: 600, color: '#2c3e50' }}>
                Auto-iterate for better results
              </span>
            </label>
            <p className="form-hint">
              Automatically refine the resume multiple times to achieve your target score
            </p>
          </div>

          {autoIterate && (
            <>
              <div className="form-group">
                <label className="form-label">Target ATS Score</label>
                <input
                  type="range"
                  min="50"
                  max="100"
                  value={targetScore}
                  onChange={(e) => setTargetScore(Number(e.target.value))}
                  disabled={loading}
                  style={{ width: '100%', cursor: 'pointer' }}
                />
                <p className="form-hint">Current target: {targetScore} points</p>
              </div>

              <div className="form-group">
                <label className="form-label">Maximum Iterations</label>
                <select
                  className="form-select"
                  value={maxIterations}
                  onChange={(e) => setMaxIterations(Number(e.target.value))}
                  disabled={loading}
                >
                  <option value={1}>1 iteration</option>
                  <option value={2}>2 iterations</option>
                  <option value={3}>3 iterations</option>
                  <option value={5}>5 iterations (recommended)</option>
                  <option value={10}>10 iterations</option>
                </select>
                <p className="form-hint">More iterations = better results but takes longer</p>
              </div>
            </>
          )}
        </div>

        {/* Action Buttons */}
        <div className="btn-group">
          <button
            type="button"
            className="btn btn-secondary"
            onClick={onBack}
            disabled={loading}
          >
            ← Back
          </button>
          <button
            type="submit"
            className="btn btn-success"
            disabled={loading || !jobDescription.trim()}
          >
            {loading ? 'Optimizing...' : 'Optimize Resume'}
          </button>
        </div>
      </form>

      {loading && (
        <div className="loading">
          <div className="spinner" />
          <p className="loading-text">Optimizing your resume with AI...</p>
        </div>
      )}

      <div style={{ marginTop: '40px', padding: '24px', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
        <h3 style={{ marginBottom: '12px', color: '#2c3e50' }}>💡 How it works:</h3>
        <ul style={{ marginLeft: '20px', color: '#7f8c8d', lineHeight: '1.8' }}>
          <li>We analyze the job description to identify key skills and requirements</li>
          <li>Your resume is enhanced to better match the job</li>
          <li>Keywords are naturally integrated without sacrificing quality</li>
          <li>Multiple iterations refine the results for maximum ATS compatibility</li>
        </ul>
      </div>
    </div>
  );
}
