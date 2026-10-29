import React, { useState } from 'react';

interface ResultsPageProps {
  data: {
    jobDescription: string;
    originalScore: number;
    optimizedScore: number;
    optimizedResume: string;
    improvements: string[];
    iterations: number;
    pdfPath?: string;
  };
  onBack: () => void;
  onReset: () => void;
}

export default function ResultsPage({ data, onBack, onReset }: ResultsPageProps) {
  const [showComparison, setShowComparison] = useState(false);
  const scoreDifference = data.optimizedScore - data.originalScore;

  const handleDownloadPDF = () => {
    if (data.pdfPath) {
      const link = document.createElement('a');
      link.href = `http://localhost:8000/api/download/${data.pdfPath.split('/').pop()}`;
      link.download = 'optimized-resume.pdf';
      link.click();
    }
  };

  const handleCopyToClipboard = () => {
    navigator.clipboard.writeText(data.optimizedResume);
    alert('Resume copied to clipboard!');
  };

  const scoreFraction = data.optimizedScore / 100;
  const scoreColor = data.optimizedScore >= 80 ? '#27ae60' : data.optimizedScore >= 70 ? '#f39c12' : '#e74c3c';

  return (
    <div className="page">
      <div className="page-header">
        <h2 className="page-title">✨ Optimization Complete!</h2>
        <p className="page-description">
          Your resume has been optimized for ATS compatibility. See the improvements below.
        </p>
      </div>

      {/* Score Improvement Cards */}
      <div className="score-container" style={{ marginBottom: '30px' }}>
        <div className="score-card">
          <div className="score-label">Original Score</div>
          <div className="score-value" style={{ color: '#95a5a6' }}>
            {data.originalScore}
          </div>
          <div className="score-bar">
            <div
              className="score-fill"
              style={{
                width: `${data.originalScore}%`,
                background: 'linear-gradient(90deg, #95a5a6, #bdc3c7)',
              }}
            />
          </div>
        </div>

        <div className="score-card">
          <div className="score-label">Optimized Score</div>
          <div className="score-value" style={{ color: scoreColor }}>
            {data.optimizedScore}
          </div>
          <div className="score-bar">
            <div
              className="score-fill"
              style={{
                width: `${data.optimizedScore}%`,
                background: `linear-gradient(90deg, ${scoreColor}, ${scoreColor}cc)`,
              }}
            />
          </div>
        </div>

        <div className="score-card">
          <div className="score-label">Improvement</div>
          <div className="score-value" style={{ color: scoreDifference >= 0 ? '#27ae60' : '#e74c3c' }}>
            +{scoreDifference}
          </div>
          <div style={{ marginTop: '16px', fontSize: '0.9rem', color: '#7f8c8d' }}>
            {scoreDifference > 0 && '📈 Great improvement!'}
            {scoreDifference === 0 && '→ Maintained'}
            {scoreDifference < 0 && '⚠️ Score decreased'}
          </div>
        </div>

        <div className="score-card">
          <div className="score-label">Iterations</div>
          <div className="score-value">{data.iterations}</div>
          <div style={{ marginTop: '16px', fontSize: '0.9rem', color: '#7f8c8d' }}>
            Refinement passes
          </div>
        </div>
      </div>

      {/* Alert for excellent score */}
      {data.optimizedScore >= 80 && (
        <div className="alert alert-success" style={{ marginBottom: '24px' }}>
          <span className="alert-icon">🎉</span>
          <span className="alert-text">
            Excellent! Your optimized resume has a strong ATS compatibility score. You're ready to apply!
          </span>
        </div>
      )}

      {/* Improvements List */}
      {data.improvements.length > 0 && (
        <div className="improvements-container">
          <h3 className="improvements-title">Key Improvements Made</h3>
          <ul className="improvements-list">
            {data.improvements.map((improvement, index) => (
              <li key={index} className="improvement-item">
                <span className="improvement-icon">✓</span>
                <span className="improvement-text">{improvement}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Resume Content */}
      <div style={{ marginTop: '30px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <h3 style={{ fontSize: '1.3rem', fontWeight: 700, color: '#2c3e50' }}>
            Optimized Resume
          </h3>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => setShowComparison(!showComparison)}
            style={{ fontSize: '0.9rem' }}
          >
            {showComparison ? 'Hide Comparison' : 'Show Comparison'}
          </button>
        </div>

        {showComparison ? (
          <div style={{ marginTop: '20px' }}>
            <p style={{ color: '#7f8c8d', marginBottom: '16px', fontSize: '0.9rem' }}>
              💡 Side-by-side comparison coming soon. For now, review the optimized version below.
            </p>
            <div className="resume-display">
              {data.optimizedResume}
            </div>
          </div>
        ) : (
          <div className="resume-display">
            {data.optimizedResume}
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div style={{ marginTop: '30px', backgroundColor: '#f8f9fa', padding: '24px', borderRadius: '8px' }}>
        <h3 style={{ marginBottom: '16px', color: '#2c3e50' }}>What's next?</h3>
        <div className="btn-group" style={{ flexDirection: 'column', gap: '12px' }}>
          <button
            type="button"
            className="btn btn-success"
            onClick={handleCopyToClipboard}
            style={{ width: '100%' }}
          >
            📋 Copy Optimized Resume
          </button>
          {data.pdfPath && (
            <button
              type="button"
              className="btn btn-primary"
              onClick={handleDownloadPDF}
              style={{ width: '100%' }}
            >
              📥 Download as PDF
            </button>
          )}
          <button
            type="button"
            className="btn btn-secondary"
            onClick={onBack}
            style={{ width: '100%' }}
          >
            ← Refine Further
          </button>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={onReset}
            style={{ width: '100%' }}
          >
            🔄 Start Over
          </button>
        </div>
      </div>

      {/* Tips Section */}
      <div style={{ marginTop: '30px', padding: '24px', backgroundColor: '#f0f1ff', borderRadius: '8px' }}>
        <h3 style={{ marginBottom: '12px', color: '#667eea' }}>🎯 Tips for submitting:</h3>
        <ul style={{ marginLeft: '20px', color: '#5a6c7d', lineHeight: '1.8' }}>
          <li>Use the optimized resume exactly as shown for maximum ATS compatibility</li>
          <li>Paste it into the application form's text field if available</li>
          <li>If uploading as PDF, use the downloaded version for best results</li>
          <li>Keep the formatting simple - avoid tables, images, and special characters</li>
          <li>Double-check that all information is accurate and truthful</li>
          <li>Customize for each job application when possible</li>
        </ul>
      </div>

      {/* Additional Resources */}
      <div style={{ marginTop: '30px', padding: '24px', backgroundColor: '#fef5e7', borderRadius: '8px' }}>
        <h3 style={{ marginBottom: '12px', color: '#f39c12' }}>📚 Additional Resources:</h3>
        <ul style={{ marginLeft: '20px', color: '#7f8c8d', lineHeight: '1.8' }}>
          <li>Review common ATS keywords for your industry</li>
          <li>Make sure contact information is clear and up-to-date</li>
          <li>Use standard section headers (Experience, Education, Skills)</li>
          <li>Include quantifiable achievements and metrics</li>
          <li>Keep your resume to 1-2 pages when possible</li>
        </ul>
      </div>
    </div>
  );
}
