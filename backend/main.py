from fastapi import FastAPI, UploadFile, File, Form
from PyPDF2 import PdfReader
import io
from fastapi.middleware.cors import CORSMiddleware

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

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/analyze")
async def analyze_resume(pdf_file: UploadFile = File(...), job_description: str = Form(...)):
    #extract job description and convert to vector embeddings
    #store vector embeddings in vector database


    #extract text from uploaded PDF file
    #convert extracted text to vector embeddings
    #send vector embeddings to vector database
    #conduct vector search to find similar keywords between job description and resume
    #return results with similarity scores



    try:
        # Read the uploaded file
        pdf_content = await pdf_file.read()
        
        # Create a PDF reader object
        pdf_reader = PdfReader(io.BytesIO(pdf_content))
        
        # Extract text from all pages
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        
        # TODO: Implement actual similarity analysis
        # Placeholder response
        return {
            "similarity": 75,  # Example similarity score
            "resume_text": text,
            "job_description": job_description
        }
    except Exception as e:
        return {"error": str(e)}
