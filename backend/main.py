from fastapi import FastAPI, UploadFile, File
from PyPDF2 import PdfReader
import io

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/upload-pdf")
async def extract_text_from_pdf(pdf_file: UploadFile = File(...)):
    try:
        # Read the uploaded file
        pdf_content = await pdf_file.read()
        
        # Create a PDF reader object
        pdf_reader = PdfReader(io.BytesIO(pdf_content))
        
        # Extract text from all pages
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        
        return {"text": text}
    except Exception as e:
        return {"error": str(e)}