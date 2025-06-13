import os
import google.generativeai as genai
from dotenv import load_dotenv
from load_converted_data import extract_csv_summary
from load_converted_data import extract_csv_summary, extract_pdf_text
from load_converted_data import extract_csv_summary, extract_pdf_text, extract_image_info
from load_converted_data import (
    extract_csv_summary,
    extract_pdf_text,
    extract_image_info,
    extract_audio_video_info,  # 👈 add this
)


# Load API key from .env file
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# for model in genai.list_models():
#     print(f"🧠 Model ID: {model.name}")
#     print(f"🔧 Supported methods: {model.supported_generation_methods}\n")


if not api_key:
    print("❌ GEMINI_API_KEY not found in .env file.")
    exit()

genai.configure(api_key=api_key)
model = genai.GenerativeModel(model_name="models/gemini-2.0-flash")


if os.path.exists("context.txt"):
    with open("context.txt", "r") as file:
        context = file.read().strip()
        print("📄 Context loaded from context.txt\n")
        converted_path = "/Users/dhyeysutariya/Developer/preprocessors/converters/converted"
        csv_context = extract_csv_summary(converted_path)
        pdf_context = extract_pdf_text(converted_path)
        image_context = extract_image_info(converted_path)
        media_context = extract_audio_video_info(converted_path)

        if csv_context:
            context += "🧾 CSV Summary:\n" + csv_context + "\n\n"
        if pdf_context:
            context += "📄 PDF Text:\n" + pdf_context + "\n\n"
        if image_context:
            context += "🖼️ Image Info:\n" + image_context + "\n\n"
        if media_context:
            context += "🎵 Media Files:\n" + media_context + "\n\n"

if context:
    print("📄 Context loaded from converted/ folder.\n")
else:
    print("📭 No supported files found in converted/.\n")

if context:
    print("📄 Context loaded from converted/ folder.\n")
else:
    print("📭 No CSV or PDF files found.\n")
# Chat loop
print("💬 Gemini CLI Chat | Type 'exit' to quit")
while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit"]:
        print("👋 Goodbye!")
        break

    prompt = f"context: {context}\n\nUser: {user_input}\nAI:"
    try:
        response = model.generate_content(prompt)
        print(f"Gemini: {response.text.strip()}\n")
    except Exception as e:
        print(f"⚠️ Error: {e}\n")
