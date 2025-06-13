import os
import google.generativeai as genai
from dotenv import load_dotenv
from load_converted_data import extract_csv_summary

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
model = genai.GenerativeModel(model_name="models/gemma-3-1b-it")

# Load optional context

if os.path.exists("context.txt"):
    with open("context.txt", "r") as file:
        context = file.read().strip()
        print("📄 Context loaded from context.txt\n")
        converted_path = "/Users/dhyeysutariya/Developer/preprocessors/converters/converted"
        context = extract_csv_summary(converted_path)

        if context:
            print("📄 CSV context loaded.\n")
        else:
            print("📭 No CSV files found.\n")
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
