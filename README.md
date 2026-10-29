# ATS Resume Optimizer

An AI-powered resume optimization tool that analyzes your resume against job descriptions and provides ATS-friendly recommendations.

## Features

✨ **Core Features**
- 📄 PDF & text resume upload
- 🎯 Job description analysis
- 🤖 AI-powered resume optimization using GPT
- 📊 ATS compatibility scoring
- 🔄 Auto-iteration for continuous improvement
- 📥 PDF download of optimized resume
- 📋 Copy-to-clipboard functionality

✅ **Optimization Capabilities**
- Keyword matching and integration
- Formatting improvements for ATS
- Action verb enhancement
- Quantifiable results highlighting
- Section reorganization
- Professional summary generation

## Project Structure

```
ats-resume-optimizer/
├── backend/                 # FastAPI Python backend
│   ├── main.py             # Main FastAPI application
│   ├── pdf_processor.py    # PDF extraction
│   ├── resume_parser.py    # Resume parsing & structuring
│   ├── ats_scorer.py       # ATS scoring engine
│   ├── ai_optimizer.py     # AI-powered optimization
│   ├── pdf_generator.py    # PDF generation
│   ├── requirements.txt    # Python dependencies
│   ├── .env               # Environment variables (add your API key)
│   └── .env.example       # Example environment file
│
└── frontend/               # React TypeScript frontend
    ├── src/
    │   ├── pages/         # Page components
    │   │   ├── ResumePage.tsx
    │   │   ├── OptimizationPage.tsx
    │   │   └── ResultsPage.tsx
    │   ├── components/    # Reusable components
    │   │   ├── FileUpload.tsx
    │   │   └── TextInput.tsx
    │   ├── services/      # API service
    │   │   └── api.ts
    │   ├── App.tsx        # Main app component
    │   ├── App.css        # Application styles
    │   └── index.tsx      # Entry point
    ├── package.json       # Node dependencies
    ├── .env              # Environment variables
    └── tsconfig.json     # TypeScript config
```

## Prerequisites

- **Python 3.9+** (for backend)
- **Node.js 16+** and npm (for frontend)
- **OpenAI API Key** (get from https://platform.openai.com/api-keys)

## Installation

### 1. Backend Setup

```bash
cd backend

# Create a Python virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with your API key
# Copy .env.example to .env and add your OpenAI API key:
# OPENAI_API_KEY=sk-your-api-key-here
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# The .env file is already configured to use http://localhost:8000
```

## Running the Application

### Start Backend Server

```bash
cd backend

# Make sure your virtual environment is activated
# Then run:
python main.py

# Or with auto-reload:
uvicorn main:app --reload
```

The backend will be available at `http://localhost:8000`

### Start Frontend Development Server

```bash
cd frontend

npm start
```

The frontend will open at `http://localhost:3000`

## API Endpoints

### Extract Text
```
POST /api/extract-text
- file: (optional) PDF file
- text: (optional) Resume text

Response:
{
  "success": true,
  "text": "extracted resume text",
  "parsed": { parsed resume structure }
}
```

### Score Resume
```
POST /api/score
- job_description: Job description text
- text: Resume text (or file upload)

Response:
{
  "success": true,
  "score": {
    "total_score": 75.5,
    "keyword_match": 70.2,
    "required_match": 80.0,
    "formatting": 75.0,
    "ats_compatibility": 60.0,
    "details": { detailed breakdown }
  }
}
```

### Optimize Resume
```
POST /api/optimize
- job_description: Job description text
- text: Resume text (or file upload)
- auto_iterate: bool (default: true)
- target_score: float (default: 85.0)
- max_iterations: int (default: 5)

Response:
{
  "original_score": 65.0,
  "optimized_score": 82.5,
  "optimized_resume": "improved resume text",
  "improvements": ["Improvement 1", "Improvement 2", ...],
  "iterations": 3,
  "pdf_path": "path/to/optimized_resume.pdf"
}
```

### Optimize with Feedback
```
POST /api/optimize/feedback
- job_description: Job description text
- resume_text: Current resume text
- feedback: User feedback/focus areas
- current_version: int (default: 1)

Response:
{
  "success": true,
  "optimized_resume": "refined resume text",
  "improvements": [...],
  "new_score": 87.0,
  "score_breakdown": { score details }
}
```

### Download PDF
```
GET /api/download/{filename}

Downloads the generated PDF file
```

## How to Use

1. **Upload Resume**: Paste your resume text or upload a PDF
2. **Add Job Description**: Paste the job description you're applying for
3. **Preview Score**: Click "Preview Score" to see your current ATS compatibility
4. **Optimize**: Choose optimization settings and click "Optimize Resume"
5. **Review Results**: Check the improvements and final score
6. **Download/Copy**: Download as PDF or copy the optimized text
7. **Apply**: Use the optimized resume for your job application

## Environment Configuration

### Backend (.env)
```
OPENAI_API_KEY=sk-your-api-key-here
API_BASE_URL=https://api.openai.com/v1
MODEL_NAME=gpt-4o-mini
DEBUG=false
```

### Frontend (.env)
```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENV=development
```

## Troubleshooting

### Backend won't start
- Check that Python 3.9+ is installed: `python --version`
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Make sure port 8000 is not in use
- Check that your OpenAI API key is valid

### Frontend won't connect to backend
- Ensure backend is running on port 8000
- Check that `REACT_APP_API_URL` in `.env` is correct
- Check browser console for CORS errors
- Verify firewall settings aren't blocking localhost connections

### API key issues
- Verify your OpenAI API key is correct and has credits
- Check that the key is in the `.env` file (not `.env.example`)
- Restart the backend after adding/changing the API key

### PDF generation fails
- Ensure ReportLab is installed: `pip install reportlab`
- Check that the temp directory has write permissions
- Try generating a smaller resume first

## Performance Tips

1. **Optimization Time**: Auto-iteration with 5 passes typically takes 30-60 seconds
2. **Resume Length**: Shorter, well-organized resumes process faster
3. **Job Description**: Detailed job descriptions yield better matches
4. **Iterations**: Start with 3 iterations, increase if needed

## Security Notes

- Never commit `.env` file with your API key
- Store API keys in environment variables, not in code
- Use HTTPS in production
- Implement rate limiting for production deployment
- Consider implementing user authentication

## Production Deployment

### Backend
```bash
# Use a production ASGI server
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app

# Or with Uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
# Build for production
npm run build

# Serve with a web server (nginx, Apache, etc.)
# Or deploy to services like Vercel, Netlify, AWS, etc.
```

### Docker

```dockerfile
# Dockerfile for backend
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
```

## Contributing

Feel free to fork, modify, and improve this project!

## Future Enhancements

- [ ] Multi-language support
- [ ] Resume templates
- [ ] Skill gap analysis
- [ ] Interview preparation tips
- [ ] Salary negotiation insights
- [ ] Job market trends
- [ ] Application tracking
- [ ] User authentication & history
- [ ] Export to multiple formats
- [ ] Integration with LinkedIn

## License

MIT License - feel free to use this project for personal or commercial purposes

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the API documentation
3. Check the browser console for errors
4. Verify all configuration files are correct

---

**Made with ❤️ to help you land your next job!**
