from fastapi import FastAPI, UploadFile, File, Form
from PyPDF2 import PdfReader
import io
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer
import numpy as np
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/analyze")
async def analyze_resume(pdf_file: UploadFile = File(...), job_description: str = Form(...)):
    try:
        # Read the uploaded file
        pdf_content = await pdf_file.read()
        
        # Create a PDF reader object
        pdf_reader = PdfReader(io.BytesIO(pdf_content))
        
        # Extract text from all pages
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()

        # Convert texts to vector embeddings
        job_description_embedding = model.encode(job_description)
        resume_embedding = model.encode(text)

        # Calculate cosine similarity
        similarity_score = float(np.dot(job_description_embedding, resume_embedding) / (
            np.linalg.norm(job_description_embedding) * np.linalg.norm(resume_embedding)
        ) * 100)

        return {
            "similarity": round(similarity_score, 2),
            "resume_text": text,
            "job_description": job_description
        }

    except Exception as e:
        return {"error": str(e)}
