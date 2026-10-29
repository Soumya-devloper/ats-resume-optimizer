import React from 'react';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  loading?: boolean;
  accept?: string;
}

export default function FileUpload({ onFileSelect, loading = false, accept = '.pdf' }: FileUploadProps) {
  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      onFileSelect(files[0]);
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.currentTarget.files;
    if (files && files.length > 0) {
      onFileSelect(files[0]);
    }
  };

  return (
    <div
      className="file-upload"
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      style={{ opacity: loading ? 0.6 : 1 }}
    >
      <input
        type="file"
        id="file-input"
        onChange={handleFileInput}
        accept={accept}
        disabled={loading}
      />
      <label htmlFor="file-input" style={{ cursor: loading ? 'not-allowed' : 'pointer' }}>
        <div className="file-upload-text">
          {loading ? '📤 Uploading...' : '📁 Drag and drop your file here'}
        </div>
        <div className="file-upload-subtext">
          or click to select a file
        </div>
      </label>
    </div>
  );
}
