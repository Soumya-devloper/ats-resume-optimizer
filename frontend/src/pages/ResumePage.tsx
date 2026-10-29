import React, { useState } from 'react';
import FileUpload from '../components/FileUpload';
import TextInput from '../components/TextInput';
import { ApiService } from '../services/api';

interface ResumePage {
  text: string;
  parsed?: any;
}

interface ResumePage_Props {
  onSubmit: (data: ResumePage) => void;
}

export default function ResumePage({ onSubmit }: ResumePage_Props) {
  const [resumeText, setResumeText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [inputMethod, setInputMethod] = useState<'file' | 'text'>('text');

  const handleFileUpload = async (file: File) => {
    setError('');
    setLoading(true);

    try {
      const result = await ApiService.extractText(file, '');
      setResumeText(result.text);
      setLoading(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upload file');
      setLoading(false);
    }
  };

  const handleTextChange = (text: string) => {
    setResumeText(text);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!resumeText.trim()) {
      setError('Please provide resume text');
      return;
    }

    if (resumeText.trim().length < 100) {
      setError('Resume text seems too short. Please provide a complete resume.');
      return;
    }

    setLoading(true);

    try {
      const result = await ApiService.extractText(null, resumeText);
      onSubmit({
        text: resumeText,
        parsed: result.parsed,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to process resume');
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <h2 className="page-title">Step 1: Upload Your Resume</h2>
        <p className="page-description">
          Start by uploading your resume or pasting the text directly. We'll analyze it and prepare it for optimization.
        </p>
      </div>

      {error && (
        <div className="alert alert-error">
          <span className="alert-icon">⚠️</span>
          <span className="alert-text">{error}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="form">
        <div className="form-group">
          <label className="form-label">Choose input method:</label>
          <div className="btn-group" style={{ marginBottom: '24px' }}>
            <button
              type="button"
              className={inputMethod === 'text' ? 'btn btn-primary' : 'btn btn-secondary'}
              onClick={() => setInputMethod('text')}
            >
              Paste Text
            </button>
            <button
              type="button"
              className={inputMethod === 'file' ? 'btn btn-primary' : 'btn btn-secondary'}
              onClick={() => setInputMethod('file')}
            >
              Upload PDF
            </button>
          </div>
        </div>

        {inputMethod === 'text' ? (
          <div className="form-group">
            <label className="form-label">Resume Text *</label>
            <textarea
              className="form-textarea"
              value={resumeText}
              onChange={(e) => handleTextChange(e.target.value)}
              placeholder="Paste your resume text here..."
              disabled={loading}
            />
            <p className="form-hint">
              {resumeText.length} characters
            </p>
          </div>
        ) : (
          <div className="form-group">
            <label className="form-label">Upload PDF *</label>
            <FileUpload
              onFileSelect={handleFileUpload}
              loading={loading}
              accept=".pdf"
            />
          </div>
        )}

        <div className="btn-group">
          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading || !resumeText.trim()}
          >
            {loading ? 'Processing...' : 'Next: Add Job Description'}
          </button>
        </div>
      </form>

      <div style={{ marginTop: '40px', padding: '24px', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
        <h3 style={{ marginBottom: '12px', color: '#2c3e50' }}>📋 Tips:</h3>
        <ul style={{ marginLeft: '20px', color: '#7f8c8d', lineHeight: '1.8' }}>
          <li>Copy your resume from Word, Google Docs, or your favorite editor</li>
          <li>Make sure all your experience, education, and skills are included</li>
          <li>The more detailed your resume, the better the optimization</li>
          <li>We support both text and PDF formats</li>
        </ul>
      </div>
    </div>
  );
}
