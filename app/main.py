# app/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os
import google.generativeai as genai
from dotenv import load_dotenv
import io
from PIL import Image
import pillow_heif
import pandas as pd
import subprocess
import tempfile
import shutil


# Ubuntu/Debian
# sudo apt-get install libreoffice

# macOS
# brew install --cask libreoffice

# Windows
# Download from https://www.libreoffice.org/
# Load API key


load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Create FastAPI app
app = FastAPI(title="File Upload to Gemini API")

# Model setup (must support files)
model = genai.GenerativeModel("models/gemini-1.5-flash")  # Use gemini-1.5-pro for file support

# Store uploaded files in memory (for chat session) files store thayy che
uploaded_files_store = {}

def convert_office_to_pdf_memory(file_content: bytes, filename: str) -> tuple[bytes, str]:
    """
    Convert Office documents (PPTX, DOCX, ODT, etc.) to PDF using LibreOffice
    Returns: (converted_pdf_bytes, new_filename)
    """
    temp_dir = None
    try:
        # Create temporary directory for processing
        temp_dir = tempfile.mkdtemp()
        
        # Save input file temporarily
        input_path = os.path.join(temp_dir, filename)
        with open(input_path, 'wb') as f:
            f.write(file_content)
        
        # Run LibreOffice conversion
        cmd = [
            'soffice',
            '--headless',
            '--convert-to', 'pdf',
            '--outdir', temp_dir,
            input_path
        ]
        
        # Execute conversion command
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            raise Exception(f"LibreOffice conversion failed: {result.stderr}")
        
        # Generate output filename
        base_name = os.path.splitext(filename)[0]
        pdf_filename = base_name + ".pdf"
        pdf_path = os.path.join(temp_dir, pdf_filename)
        
        # Check if PDF was created
        if not os.path.exists(pdf_path):
            raise Exception("PDF file was not created by LibreOffice")
        
        # Read converted PDF file
        with open(pdf_path, 'rb') as f:
            pdf_content = f.read()
        
        return pdf_content, pdf_filename
        
    except subprocess.TimeoutExpired:
        raise Exception("LibreOffice conversion timed out (30 seconds)")
    except Exception as e:
        raise Exception(f"Failed to convert Office document to PDF: {str(e)}")
    finally:
        # Clean up temporary directory
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

def convert_excel_to_csv_memory(file_content: bytes, filename: str) -> tuple[bytes, str]:
    """
    Convert Excel file content (XLS/XLSX) to CSV in memory
    Returns: (converted_csv_bytes, new_filename)
    """
    try:
        # Create a BytesIO object from the file content
        excel_buffer = io.BytesIO(file_content)
        
        # Choose the correct engine based on file extension
        engine = 'xlrd' if filename.lower().endswith('.xls') else 'openpyxl'
        
        # Read Excel file from memory
        df = pd.read_excel(excel_buffer, engine=engine)
        
        # Convert to CSV in memory
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        
        # Convert string to bytes for consistency
        csv_bytes = csv_buffer.getvalue().encode('utf-8')
        
        # Generate new filename
        new_filename = filename.rsplit(".", 1)[0] + ".csv"
        
        return csv_bytes, new_filename
        
    except Exception as e:
        raise Exception(f"Failed to convert Excel to CSV: {str(e)}")

def convert_heic_to_jpg_memory(file_content: bytes, filename: str) -> tuple[bytes, str]:
    """
    Convert HEIC file content to JPG in memory
    Returns: (converted_jpg_bytes, new_filename)
    """
    try:
        # Create a BytesIO object from the file content
        heic_buffer = io.BytesIO(file_content)
        
        # Read HEIC file from memory
        heif_file = pillow_heif.read_heif(heic_buffer)
        
        # Convert to PIL Image
        image = Image.frombytes(
            heif_file.mode,
            heif_file.size,
            heif_file.data,
            "raw"
        )
        
        # Convert to JPG in memory
        jpg_buffer = io.BytesIO()
        image.save(jpg_buffer, "JPEG", quality=95)
        jpg_buffer.seek(0)
        
        # Generate new filename
        new_filename = os.path.splitext(filename)[0] + ".jpg"
        
        return jpg_buffer.getvalue(), new_filename
        
    except Exception as e:
        raise Exception(f"Failed to convert HEIC to JPG: {str(e)}")

@app.post("/upload-file/")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload file directly to Gemini API without saving to server
    Converts HEIC files to JPG before uploading
    """
    try:
        # Read file content into memory
        file_content = await file.read()
        original_filename = file.filename
        content_type = file.content_type
        
        # Check if file is HEIC and convert to JPG
        if file.filename.lower().endswith(('.heic', '.heif')):
            print(f"[INFO] Converting HEIC file: {file.filename}")
            try:
                # Convert HEIC to JPG
                converted_content, new_filename = convert_heic_to_jpg_memory(file_content, file.filename)
                
                # Update file details
                file_content = converted_content
                file.filename = new_filename
                content_type = "image/jpeg"
                
                print(f"[✓] Converted: {original_filename} → {new_filename}")
                
            except Exception as conv_error:
                print(f"[!] HEIC conversion failed: {conv_error}")
                raise HTTPException(
                    status_code=400, 
                    detail=f"Failed to convert HEIC file: {str(conv_error)}"
                )
        
        # Check if file is Excel and convert to CSV
        elif file.filename.lower().endswith(('.xls', '.xlsx')):
            print(f"[INFO] Converting Excel file: {file.filename}")
            try:
                # Convert Excel to CSV
                converted_content, new_filename = convert_excel_to_csv_memory(file_content, file.filename)
                
                # Update file details
                file_content = converted_content
                file.filename = new_filename
                content_type = "text/csv"
                
                print(f"[✓] Converted: {original_filename} → {new_filename}")
                
            except Exception as conv_error:
                print(f"[!] Excel conversion failed: {conv_error}")
                raise HTTPException(
                    status_code=400, 
                    detail=f"Failed to convert Excel file: {str(conv_error)}"
                )
        
        # Check if file is Office document and convert to PDF
        elif file.filename.lower().endswith(('.pptx', '.ppt', '.docx', '.doc', '.odt', '.odp', '.ods')):
            print(f"[INFO] Converting Office document: {file.filename}")
            try:
                # Convert Office document to PDF
                converted_content, new_filename = convert_office_to_pdf_memory(file_content, file.filename)
                
                # Update file details
                file_content = converted_content
                file.filename = new_filename
                content_type = "application/pdf"
                
                print(f"[✓] Converted: {original_filename} → {new_filename}")
                
            except Exception as conv_error:
                print(f"[!] Office document conversion failed: {conv_error}")
                raise HTTPException(
                    status_code=400, 
                    detail=f"Failed to convert Office document: {str(conv_error)}"
                )
        
        # Create a temporary file path (but keep in memory)
        temp_file = io.BytesIO(file_content)
        temp_file.name = file.filename  # Add name attribute
        
        # Upload to Gemini directly from memory
        uploaded = genai.upload_file(
            temp_file,
            mime_type=content_type,
            display_name=file.filename
        )
        
        # Store file reference for chat (use session ID in real app)
        session_id = "default"  # In real app, generate unique session IDs
        uploaded_files_store[session_id] = [uploaded]
        
        return {
            "message": "File uploaded successfully!",
            "original_filename": original_filename,
            "processed_filename": file.filename,
            "file_id": uploaded.name,
            "session_id": session_id,
            "converted_from_heic": original_filename != file.filename
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions (like conversion errors)
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

@app.post("/chat/")
async def chat_with_file(question: str, session_id: str = "default"):
    """
    Chat with uploaded files
    """
    try:
        # Get uploaded files for this session
        if session_id not in uploaded_files_store:
            raise HTTPException(status_code=404, detail="No files found for this session")
        
        files_to_use = uploaded_files_store[session_id]
        
        # Generate response with files
        response = model.generate_content([
            {
                "role": "user", 
                "parts": [
                    {"text": question},
                    *files_to_use  # Include uploaded files
                ]
            }
        ])
        
        return {
            "question": question,
            "response": response.text.strip()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

@app.get("/")
async def root():
    return {"message": "File Upload to Gemini API with HEIC, Excel, and Office document conversion is running!"}

# Run with: uvicorn main:app --reload