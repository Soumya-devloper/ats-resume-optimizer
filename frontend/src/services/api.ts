const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export class ApiService {
  /**
   * Extract text from PDF or use provided text
   */
  static async extractText(file: File | null, text: string) {
    const formData = new FormData();

    if (file) {
      formData.append('file', file);
    }
    if (text) {
      formData.append('text', text);
    }

    const response = await fetch(`${API_BASE_URL}/api/extract-text`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to extract text');
    }

    return response.json();
  }

  /**
   * Score resume against job description
   */
  static async scoreResume(resumeText: string, jobDescription: string) {
    const formData = new FormData();
    formData.append('text', resumeText);
    formData.append('job_description', jobDescription);

    const response = await fetch(`${API_BASE_URL}/api/score`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to score resume');
    }

    return response.json();
  }

  /**
   * Optimize resume for job description
   */
  static async optimizeResume(
    resumeText: string,
    jobDescription: string,
    autoIterate: boolean = true,
    targetScore: number = 85,
    maxIterations: number = 5
  ) {
    const formData = new FormData();
    formData.append('text', resumeText);
    formData.append('job_description', jobDescription);
    formData.append('auto_iterate', autoIterate.toString());
    formData.append('target_score', targetScore.toString());
    formData.append('max_iterations', maxIterations.toString());

    const response = await fetch(`${API_BASE_URL}/api/optimize`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to optimize resume');
    }

    return response.json();
  }

  /**
   * Optimize resume with user feedback
   */
  static async optimizeWithFeedback(
    jobDescription: string,
    resumeText: string,
    feedback: string,
    currentVersion: number = 1
  ) {
    const formData = new FormData();
    formData.append('job_description', jobDescription);
    formData.append('resume_text', resumeText);
    formData.append('feedback', feedback);
    formData.append('current_version', currentVersion.toString());

    const response = await fetch(`${API_BASE_URL}/api/optimize/feedback`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to process feedback');
    }

    return response.json();
  }

  /**
   * Download generated PDF
   */
  static async downloadPDF(filename: string) {
    const response = await fetch(`${API_BASE_URL}/api/download/${filename}`, {
      method: 'GET',
    });

    if (!response.ok) {
      throw new Error('Failed to download PDF');
    }

    return response.blob();
  }

  /**
   * Health check
   */
  static async healthCheck() {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      return response.ok;
    } catch {
      return false;
    }
  }
}
