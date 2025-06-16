# app/cli_chat.py

import os
import google.generativeai as genai
from dotenv import load_dotenv
from google.generativeai.types import File
from mimetypes import guess_type

# Load API key
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Model setup (must support files)
model = genai.GenerativeModel("models/gemma-3-4b-it")

# Upload files from /converted/

# 📌 Point to your in-memory PDF
pdf_path = input("📄 Enter path to PDF: ").strip() # <--- You control the source path
files_to_upload = []
try:
    mime_type, _ = guess_type(pdf_path)
    with open(pdf_path, "rb") as f:
        uploaded = genai.upload_file(
            file=f,
            mime_type=mime_type,
            display_name=os.path.basename(pdf_path)
        )
        files_to_upload.append(uploaded)
        print(f"✅ Uploaded in-memory: {pdf_path}")
except Exception as e:
    print(f"[!] Error uploading PDF in-memory: {e}")
# above block of code is for having path as variable.

# Start chat loop
print("\n💬 Gemini CLI Chat | Type 'exit' to quit\n")

while True:
    user_input = input("You: ").strip()
    if user_input.lower() in ["exit", "quit"]:
        break
    try:
        response = model.generate_content([
            {
                "role": "user",
                "parts": [
                    {"text": user_input},
                    *files_to_upload # real files sent
                ]
            }
        ])
        print("\nGemini:", response.text.strip(), "\n")

    except Exception as e:
        print("⚠️ Error:", e)
