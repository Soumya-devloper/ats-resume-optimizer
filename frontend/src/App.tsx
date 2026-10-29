import React, { useState } from 'react';
import './App.css';
import ResumePage from './pages/ResumePage';
import OptimizationPage from './pages/OptimizationPage';
import ResultsPage from './pages/ResultsPage';

type AppPage = 'resume' | 'optimization' | 'results';

interface ResumeData {
  text: string;
  parsed?: any;
}

interface OptimizationData {
  jobDescription: string;
  originalScore: number;
  optimizedScore: number;
  optimizedResume: string;
  improvements: string[];
  iterations: number;
  pdfPath?: string;
}

function App() {
  const [currentPage, setCurrentPage] = useState<AppPage>('resume');
  const [resumeData, setResumeData] = useState<ResumeData | null>(null);
  const [optimizationData, setOptimizationData] = useState<OptimizationData | null>(null);

  const handleResumeSubmit = (data: ResumeData) => {
    setResumeData(data);
    setCurrentPage('optimization');
  };

  const handleOptimizationSubmit = (data: OptimizationData) => {
    setOptimizationData(data);
    setCurrentPage('results');
  };

  const handleReset = () => {
    setCurrentPage('resume');
    setResumeData(null);
    setOptimizationData(null);
  };

  const handleBackToOptimization = () => {
    setCurrentPage('optimization');
  };

  return (
    <div className="App">
      <header className="app-header">
        <div className="container">
          <h1 className="app-title">ATS Resume Optimizer</h1>
          <p className="app-subtitle">Optimize your resume for Applicant Tracking Systems</p>
        </div>
      </header>

      <main className="app-main">
        <div className="container">
          {currentPage === 'resume' && (
            <ResumePage onSubmit={handleResumeSubmit} />
          )}

          {currentPage === 'optimization' && resumeData && (
            <OptimizationPage
              resumeData={resumeData}
              onSubmit={handleOptimizationSubmit}
              onBack={handleReset}
            />
          )}

          {currentPage === 'results' && optimizationData && (
            <ResultsPage
              data={optimizationData}
              onBack={handleBackToOptimization}
              onReset={handleReset}
            />
          )}
        </div>
      </main>

      <footer className="app-footer">
        <p>&copy; 2024 ATS Resume Optimizer. Powered by AI.</p>
      </footer>
    </div>
  );
}

export default App;
