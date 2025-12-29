# ATS Resume Reviewer

An AI-powered Applicant Tracking System (ATS) resume reviewer that analyzes resumes against job descriptions and provides actionable feedback to optimize your job applications.

## 🚀 Features

### Core Functionality
- **Resume Analysis**: Upload PDF resumes and compare them against job descriptions
- **Similarity Scoring**: Get a percentage match score using advanced vector embeddings
- **AI-Powered Feedback**: Receive detailed recommendations to improve your resume
- **Comprehensive Reports**: Download professional PDF reports with analysis and original resume

### Technical Features
- **Vector Database Integration**: Uses Pinecone for efficient similarity matching
- **Advanced NLP**: Leverages OpenAI GPT-4 for intelligent feedback generation
- **Modern UI**: Built with Next.js, TypeScript, and Tailwind CSS
- **RESTful API**: FastAPI backend with automatic OpenAPI documentation

## 📋 Prerequisites

### Required Accounts & API Keys
1. **OpenAI API Key**: For AI feedback generation
2. **Pinecone API Key**: For vector database operations

### System Requirements
- Python 3.8+
- Node.js 18+
- npm or pnpm

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd ats-resume-reviewer
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the `backend/` directory:
```env
OPENAI_API_KEY=your_openai_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
```

### 4. Frontend Setup
```bash
cd frontend
pnpm install
```

## 🏃‍♂️ Running the Application

### Start the Backend Server
```bash
cd backend
# Activate virtual environment first
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # macOS/Linux

# Start the FastAPI server
fastapi dev main.py
```
The backend will be available at: `http://127.0.0.1:8000`

### Start the Frontend Server
In a new terminal:
```bash
cd frontend
npm run dev
# or
pnpm dev
```
The frontend will be available at: `http://localhost:3000`

## 🎯 Usage Guide

### 1. Access the Application
Open your browser and navigate to `http://localhost:3000`

### 2. Upload Resume & Job Description
- **Resume**: Upload a PDF file (max 10MB)
- **Job Description**: Paste the job requirements in the text area

### 3. Analyze
Click "Analyze Resume" to:
- Calculate similarity score
- Extract resume text
- Generate AI feedback
- Display visual results

### 4. Download Report
After analysis, click "Download PDF Report" to get:
- Professional analysis report
- Similarity score visualization
- AI feedback and recommendations
- Complete resume document embedded
- Job description analysis

## 📁 Project Structure

```
ats-resume-reviewer/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   ├── .env                 # Environment variables (create this)
│   └── data/
│       ├── job-descriptions/ # Sample job descriptions
│       └── resumes/         # Sample resume files
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── app/            # Next.js app structure
│   │   ├── hooks/          # Custom React hooks
│   │   └── lib/            # Utility functions
│   ├── package.json        # Node.js dependencies
│   └── components.json     # UI component configuration
└── README.md
```

## 🔧 API Endpoints

### Core Analysis Endpoints

#### POST `/analyze/pinecone`
Analyzes resume similarity using Pinecone vector database
- **Body**: `multipart/form-data`
  - `pdf_file`: Resume PDF file
  - `job_description`: Job description text
- **Response**: Similarity score and extracted text

#### POST `/feedback`
Generates AI-powered feedback using OpenAI GPT-4
- **Body**: `multipart/form-data`
  - `pdf_file`: Resume PDF file
  - `job_description`: Job description text
- **Response**: Detailed AI feedback

#### POST `/download`
Generates comprehensive PDF report
- **Body**: `multipart/form-data`
  - `pdf_file`: Resume PDF file
  - `job_description`: Job description text
  - `similarity`: Similarity percentage
  - `feedback`: AI feedback text
- **Response**: Downloadable PDF report

### Documentation
Interactive API documentation available at: `http://127.0.0.1:8000/docs`

## 🎨 Frontend Components

### Key Components
- **ResumeAnalyzer**: Main analysis interface
- **CircularProgress**: Visual similarity score display
- **Button, Card, Textarea**: Reusable UI components

### Styling
- **Tailwind CSS**: Utility-first CSS framework
- **Dark Theme**: Modern dark mode design
- **Responsive Design**: Mobile-friendly interface

## 🔍 Sample Data

### Job Descriptions
Located in `backend/data/job-descriptions/`:
- `google.txt` - Google SDE position
- `cisco.txt` - Cisco engineering role
- `coinbase.txt` - Coinbase technical position
- And more...

### Resume Samples
Located in `backend/data/resumes/`:
- `Aaron_s_SWE_Resume_v0.pdf` - Sample software engineering resume

## 🐛 Troubleshooting

### Common Issues

#### Vector Database Issues
```bash
# If Pinecone operations fail:
1. Check your PINECONE_API_KEY in .env
2. Ensure you have sufficient Pinecone credits
3. Try running the analysis twice (first run may initialize indexes)
```

#### OpenAI API Issues
```bash
# If AI feedback fails:
1. Verify your OPENAI_API_KEY is correct
2. Check your OpenAI API credits/balance
3. Ensure network connectivity to OpenAI endpoints
```

#### Frontend Issues
```bash
# If the frontend doesn't load:
1. Ensure backend is running on port 8000
2. Check for CORS issues (should be handled automatically)
3. Verify npm packages installed correctly
```

### Performance Tips
- **Large PDFs**: Keep resumes under 10MB for optimal performance
- **First Run**: Initial analysis may be slower due to vector index creation
- **Multiple Analyses**: Subsequent analyses are faster with warm cache

