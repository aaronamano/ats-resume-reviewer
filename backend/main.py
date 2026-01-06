from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from PyPDF2 import PdfReader
import io
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os
from pinecone import Pinecone
import time
from time import sleep
from openai import OpenAI
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
from reportlab.platypus import KeepTogether
import re

app = FastAPI()

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

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

# Initialize the sentence transformer model
model = SentenceTransformer('BAAI/bge-large-en-v1.5')  # This model also produces 1024d vectors


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

@app.get("/")
async def root():
    return {"message": "Hello World"}
    
@app.post("/analyze")
async def analyze_files(pdf_file: UploadFile = File(...), job_description: str = Form(...)):
    try:
        # Read the uploaded file
        pdf_content = await pdf_file.read()
        
        # Create a PDF reader object
        pdf_reader = PdfReader(io.BytesIO(pdf_content))
        
        # Extract text from all pages
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        
        text = text.replace("\n", " ").replace("|", " ").replace("•", " ").replace(";", " ").replace(",", " ").replace(":", " ").replace("–", " ")
        text = text.lower()
        
        # Replace common irrelevant words using regex with word boundaries
        common_words = ['and', 'of', 'to', 'with', 'the', 'a', 'an', 'in', 'on', 'at', 'for', 'from', 'by', 'or', 'but', 'as', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their', 'experience', 'work', 'job', 'position', 'role', 'team', 'company', 'project', 'management', 'development', 'design', 'implementation', 'testing', 'deployment', 'maintenance', 'support', 'training', 'education', 'skills', 'knowledge', 'ability', 'expertise', 'proficiency', 'understanding', 'familiarity', 'awareness']
        
        for word in common_words:
            text = re.sub(rf'\b{re.escape(word)}\b', '', text, flags=re.IGNORECASE)
        
        # Clean up extra spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        job_description = job_description.replace(".", " ").replace("(", " ").replace(")", " ").replace(":", " ").replace(";", " ").replace(",", " ").replace("/", " ")
        job_description = job_description.lower()
        
        # Replace common irrelevant words in job description using regex
        for word in common_words:
            job_description = re.sub(rf'\b{re.escape(word)}\b', '', job_description, flags=re.IGNORECASE)
        
        # Clean up extra spaces in job description
        job_description = re.sub(r'\s+', ' ', job_description).strip()

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
        return {"error": str(e)}
    
@app.post("/feedback")
async def provide_feedback(pdf_file: UploadFile = File(...), job_description: str = Form(...)):
    try:
        # Read the uploaded file
        pdf_content = await pdf_file.read()
        
        # Create a PDF reader object
        pdf_reader = PdfReader(io.BytesIO(pdf_content))
        
        # Extract text from all pages
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a senior software engineer who has been reviewing resumes for years. Provide constructive feedback on how the resume can be better aligned with the job description. Focus on skills, experiences, and qualifications that should be highlighted or added."
                },
                {
                    "role": "user",
                    "content": f"Please analyze this job description:\n\n{job_description}\n\nAnd this resume:\n\n{text}\n\nProvide specific feedback on what can be improved to make this resume a better match for the job. Include suggestions for skills to highlight, experiences to emphasize, and any gaps that should be addressed."
                }
            ],
            max_tokens=1000,
            temperature=0.7
        )

        return {"feedback": response.choices[0].message.content}
        
    except Exception as e:
        return {"error": str(e)}

@app.post("/download")
async def download_report(pdf_file: UploadFile = File(...), job_description: str = Form(...), similarity: float = Form(...), feedback: str = Form(...)):
    try:
        # Read the uploaded file to extract resume text and keep original content
        pdf_content = await pdf_file.read()
        pdf_reader = PdfReader(io.BytesIO(pdf_content))
        
        # Extract text from all pages
        resume_text = ""
        for page in pdf_reader.pages:
            resume_text += page.extract_text()

        # Create a PDF in memory for the analysis report
        report_buffer = io.BytesIO()
        doc = SimpleDocTemplate(report_buffer, pagesize=letter, 
                               rightMargin=60, leftMargin=60,
                               topMargin=60, bottomMargin=40)
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=28,
            textColor=colors.darkblue,
            alignment=TA_CENTER,
            spaceAfter=25,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=20,
            textColor=colors.darkblue,
            spaceAfter=15,
            spaceBefore=25,
            fontName='Helvetica-Bold',
            borderLeft=4,
            borderLeftColor=colors.darkblue,
            paddingLeft=12,
            backgroundColor=colors.lightblue,
            leftIndent=0
        )
        
        subheading_style = ParagraphStyle(
            'SubHeading',
            parent=styles['Heading3'],
            fontSize=16,
            textColor=colors.darkgreen,
            spaceAfter=10,
            spaceBefore=15,
            fontName='Helvetica-Bold'
        )
        
        normal_style = ParagraphStyle(
            'NormalStyle',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.black,
            leading=16,
            spaceAfter=8,
            alignment=TA_LEFT,
            fontName='Helvetica'
        )
        
        content_style = ParagraphStyle(
            'ContentStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.black,
            leading=14,
            spaceAfter=6,
            alignment=TA_LEFT,
            fontName='Helvetica',
            leftIndent=20,
            rightIndent=20
        )
        
        # Build the PDF content
        story = []
        
        # Professional Header
        header_data = [
            [Paragraph("Resume Analysis Report", title_style)]
        ]
        header_table = Table(header_data, colWidths=[480])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightblue),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 25),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 25),
            ('BOX', (0, 0), (-1, -1), 3, colors.darkblue),
            ('ROUNDED', (0, 0), (-1, -1), 8),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 20))
        
        # Date and metadata
        date_style = ParagraphStyle(
            'DateStyle',
            parent=normal_style,
            fontSize=10,
            textColor=colors.grey,
            alignment=TA_RIGHT,
            fontName='Helvetica-Oblique'
        )
        story.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", date_style))
        story.append(Spacer(1, 25))
        
        # SIMILARITY SCORE SECTION - Enhanced formatting
        story.append(Paragraph("📊 Resume-Job Match Analysis", heading_style))
        
        # Determine colors and messages
        similarity_color = colors.green if similarity >= 80 else colors.orange if similarity >= 50 else colors.red
        similarity_emoji = "🟢" if similarity >= 80 else "🟡" if similarity >= 50 else "🔴"
        similarity_text = "Excellent Match" if similarity >= 80 else "Good Match" if similarity >= 50 else "Needs Improvement"
        
        # Score display with enhanced formatting
        score_display_data = [
            [
                Paragraph(f"{similarity_emoji} Match Score", ParagraphStyle('ScoreLabel', parent=normal_style, fontSize=14, fontName='Helvetica-Bold')),
                Paragraph(f"{similarity:.1f}%", ParagraphStyle('ScoreValue', parent=normal_style, fontSize=24, textColor=similarity_color, fontName='Helvetica-Bold', alignment=TA_CENTER))
            ],
            [
                "Assessment:",
                Paragraph(similarity_text, ParagraphStyle('ScoreStatus', parent=normal_style, fontSize=14, textColor=similarity_color, fontName='Helvetica-Bold'))
            ]
        ]
        
        score_display_table = Table(score_display_data, colWidths=[150, 200])
        score_display_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 2, colors.grey),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        story.append(KeepTogether([score_display_table, Spacer(1, 20)]))
        
        # Detailed analysis summary
        if similarity >= 80:
            analysis_text = "🎉 <b>Outstanding Match!</b> Your resume strongly aligns with this position. Highlight the key strengths that make you an ideal candidate during your application."
        elif similarity >= 50:
            analysis_text = "👍 <b>Good Potential!</b> Your resume shows relevant alignment. Focus on emphasizing specific skills and experiences mentioned in the job description to strengthen your application."
        else:
            analysis_text = "⚠️ <b>Opportunity for Enhancement!</b> Consider tailoring your resume to better highlight the specific requirements and keywords from this job description."
        
        story.append(Paragraph("📝 Strategic Recommendations", subheading_style))
        story.append(Paragraph(analysis_text, normal_style))
        story.append(Spacer(1, 25))
        
        # JOB DESCRIPTION SECTION - Enhanced formatting
        story.append(Paragraph("💼 Job Description", heading_style))
        story.append(Paragraph("<b>Position Requirements:</b>", subheading_style))
        
        # Format job description with better spacing
        job_desc_formatted = job_description.replace('\n', '<br/>')
        job_desc_text = job_desc_formatted[:5000] + "..." if len(job_desc_formatted) > 5000 else job_desc_formatted
        story.append(Paragraph(job_desc_text, content_style))
        story.append(Spacer(1, 25))
        
        # AI FEEDBACK SECTION - Enhanced formatting
        story.append(Paragraph("🤖 AI-Powered Insights & Recommendations", heading_style))
        
        # Format AI feedback with better structure
        if feedback:
            feedback_formatted = feedback.replace('\n', '<br/>').replace('•', '• ').replace('-', '- ')
            feedback_text = feedback_formatted[:5000] + "..." if len(feedback_formatted) > 5000 else feedback_formatted
            story.append(Paragraph(feedback_text, content_style))
        else:
            story.append(Paragraph("No AI feedback available at this time.", normal_style))
        
        story.append(Spacer(1, 25))
        
        # Add a visual separator
        separator_data = [['']]
        separator_table = Table(separator_data, colWidths=[480])
        separator_table.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 2, colors.darkblue),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.darkblue),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ]))
        story.append(separator_table)
        
        # Footer information
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.grey,
            alignment=TA_CENTER,
            fontName='Helvetica',
            leading=12
        )
        
        story.append(Paragraph("This report was generated using AI-powered resume analysis technology.", footer_style))
        story.append(Paragraph("For optimal results, review the suggestions and customize your resume accordingly.", footer_style))
        story.append(Spacer(1, 10))
        
        # Build the analysis report PDF
        doc.build(story)
        report_buffer.seek(0)
        
        # Create final PDF that combines both the analysis report and the original resume
        final_buffer = io.BytesIO()
        
        # Use PdfReader to merge both PDFs
        from PyPDF2 import PdfMerger
        
        merger = PdfMerger()
        
        # Add the analysis report first
        merger.append(report_buffer)
        
        # Add a separator page
        separator_buffer = io.BytesIO()
        separator_doc = SimpleDocTemplate(separator_buffer, pagesize=letter,
                                         rightMargin=60, leftMargin=60,
                                         topMargin=60, bottomMargin=40)
        
        separator_story = []
        separator_story.append(Paragraph("📄 Original Resume Document", heading_style))
        separator_story.append(Spacer(1, 20))
        separator_story.append(Paragraph(
            f"Below is the complete resume document for {pdf_file.filename}. "
            "This is the original file that was analyzed in this report.", 
            content_style
        ))
        separator_story.append(Spacer(1, 30))
        
        separator_doc.build(separator_story)
        separator_buffer.seek(0)
        merger.append(separator_buffer)
        
        # Add the original resume
        merger.append(io.BytesIO(pdf_content))
        
        # Write the merged PDF to the final buffer
        merger.write(final_buffer)
        final_buffer.seek(0)
        
        # Return the PDF as a streaming response
        filename = f"resume-analysis-{datetime.now().strftime('%Y%m%d-%H%M%S')}.pdf"
        
        return StreamingResponse(
            io.BytesIO(final_buffer.read()),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        return {"error": str(e)}