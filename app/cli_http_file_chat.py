import os
import requests
from dotenv import load_dotenv
from mimetypes import guess_type

# Load your Gemini API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ GEMINI_API_KEY not found in .env")
    exit()

# Step 1: Ask user for file path
file_path = input("📄 Enter path to your PDF file: ").strip()

# Step 2: Upload file to Gemini from memory
mime_type, _ = guess_type(file_path)
if not mime_type:
    mime_type = "application/pdf"

with open(file_path, "rb") as f:
    upload_resp = requests.post(
    f"https://generativelanguage.googleapis.com/v1beta/files:upload?key={api_key}",
        files={"file": (os.path.basename(file_path), f, mime_type)}
    )

    print("🔍 Upload response:", upload_resp.status_code)
    print("📦 Full response JSON:", upload_resp.text)

    if upload_resp.status_code != 200:
        print("❌ Upload failed.")
        exit()

    file_id = upload_resp.json()["name"]

print(f"✅ Uploaded! File ID: {file_id}")

# Step 3: Ask Gemini about the file
question = input("\n💬 What do you want to ask about the PDF? ").strip()

# Step 4: Send question and file_id to Gemini
chat_resp = requests.post(
    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={api_key}",
    headers={"Content-Type": "application/json"},
    json={
        "contents": [{
            "role": "user",
            "parts": [
                {"text": question},
                {"file_data": {
                    "file_id": file_id,
                    "mime_type": "application/pdf"
                }}
            ]
        }]
    }
)

# Step 5: Show Gemini's response
print("\n🤖 Gemini says:\n")
print(chat_resp.json()["candidates"][0]["content"]["parts"][0]["text"])