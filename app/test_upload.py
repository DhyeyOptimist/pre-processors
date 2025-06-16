# test_upload.py
import requests
import os

# Your API URL
API_URL = "http://127.0.0.1:8000"

def test_file_upload():
    """Test file upload to your API"""
    
    # Ask for file path
    file_path = input("📄 Enter path to your file (PDF/Excel/Image): ").strip()
    
    if not os.path.exists(file_path):
        print("❌ File not found!")
        return
    
    print(f"📤 Uploading: {file_path}")
    
    try:
        # Get correct MIME type
        from mimetypes import guess_type
        mime_type, _ = guess_type(file_path)
        
        # Fallback MIME types for common files
        if not mime_type:
            if file_path.lower().endswith('.pdf'):
                mime_type = 'application/pdf'
            elif file_path.lower().endswith(('.xlsx', '.xls')):
                mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            elif file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                mime_type = 'image/jpeg'
            else:
                mime_type = 'application/pdf'  # Default fallback
        
        print(f"🔍 MIME Type: {mime_type}")
        
        # Open and send file with correct MIME type
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, mime_type)}
            
            response = requests.post(f"{API_URL}/upload-file/", files=files)
            
            print(f"📡 Status Code: {response.status_code}")
            print(f"📦 Response: {response.text}")
            
            if response.status_code == 200:
                print("✅ Upload successful!")
                
                # Test chat
                test_chat()
            else:
                print("❌ Upload failed!")
                
    except Exception as e:
        print(f"💥 Error: {e}")

def test_chat():
    """Test chat functionality"""
    question = input("\n💬 Ask a question about your file: ").strip()
    
    try:
        chat_data = {
            "question": question,
            "session_id": "default"
        }
        
        response = requests.post(f"{API_URL}/chat/", params=chat_data)
        
        print(f"📡 Status Code: {response.status_code}")
        print(f"🤖 Response: {response.json()}")
        
    except Exception as e:
        print(f"💥 Chat Error: {e}")

if __name__ == "__main__":
    print("🧪 Testing File Upload API")
    print("Make sure your server is running: uvicorn main:app --reload")
    print()
    
    test_file_upload()