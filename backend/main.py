from fastapi import FastAPI, UploadFile, File, Form
from PyPDF2 import PdfReader
import io
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer
import numpy as np
from dotenv import load_dotenv
import os
from pinecone import Pinecone, ServerlessSpec
try:
    import readline
except ImportError:
    import pyreadline3 as readline
import time
from time import sleep  # Add this import at the top

app = FastAPI()

load_dotenv()

pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))

index_name = "vector-resume-index"

if not pc.has_index(index_name):
    pc.create_index_for_model(
        name=index_name,
        cloud="aws",
        region="us-east-1",
        embed={
            "model":"llama-text-embed-v2",
            "field_map":{"text": "chunk_text"}
        }
    )

# Get the index after creation
index = pc.Index(index_name)

origins = [
    "http://localhost:3000",  # Add this line for Next.js frontend
    "http://127.0.0.1:3000",  # Add this line as alternative localhost
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
model = SentenceTransformer('BAAI/bge-large-en-v1.5')  # This model also produces 1024d vectors

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
    
@app.post("/analyze/pinecone")
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

        # Create vector embeddings with normalization for cosine similarity
        resume_embedding = model.encode(text, normalize_embeddings=True).tolist()
        job_description_embedding = model.encode(job_description, normalize_embeddings=True).tolist()

        # Add explicit dimension check
        if len(resume_embedding) != 1024 or len(job_description_embedding) != 1024:
            raise ValueError("Vector dimensions do not match required 1024 dimensions")

        # Use the index with unique IDs for each request
        unique_id = str(int(time.time()))
        resume_id = f"resume_{unique_id}"
        job_desc_id = f"job_desc_{unique_id}"
        
        # Upsert vectors with unique IDs
        index.upsert(vectors=[{
            "id": job_desc_id,
            "values": job_description_embedding,
            "metadata": {
                "type": "job_description",
                "timestamp": unique_id
            }
        }])

        index.upsert(vectors=[{
            "id": resume_id,
            "values": resume_embedding,
            "metadata": {
                "type": "resume",
                "timestamp": unique_id
            }
        }])

        # Add a small delay to allow Pinecone to process the upserts
        sleep(1)

        # Query using resume vector to find similarity with job description
        query_response = index.query(
            vector=resume_embedding,
            top_k=1,
            include_values=True,
            include_metadata=True,
            filter={
                "type": "job_description",
                "timestamp": unique_id
            }
        )

        print(f"Query response: {query_response}")  # Debug print

        # Check if matches were found
        if not query_response['matches']:
            return {
                "similarity": 0.0,
                "resume_text": text,
                "job_description": job_description,
                "warning": "No matches found in vector database"
            }

        # Calculate similarity score
        similarity_score = float(query_response['matches'][0]['score'] * 100)

        # Clean up vectors after use
        index.delete(ids=[resume_id, job_desc_id])

        return {
            "similarity": round(similarity_score, 2),
            "resume_text": text,
            "job_description": job_description
        }

    except Exception as e:
        print(f"Error in analyze_resume: {str(e)}")  # Debug print
        return {"error": str(e)}
