import os
import csv
import fitz  # PyMuPDF
from pymediainfo import MediaInfo

def extract_audio_video_info(folder_path):
    summary = []
    for file in os.listdir(folder_path):
        if file.lower().endswith((".mp3", ".mp4")):
            path = os.path.join(folder_path, file)
            try:
                media_info = MediaInfo.parse(path)
                duration_ms = None

                for track in media_info.tracks:
                    if track.track_type in ["Audio", "Video"]:
                        duration_ms = track.duration
                        break

                duration_str = ""
                if duration_ms:
                    seconds = int(duration_ms / 1000)
                    duration_str = f", duration ≈ {seconds} seconds"

                summary.append(f"- {file}: type = {file.split('.')[-1].upper()}{duration_str}")

            except Exception as e:
                summary.append(f"- {file}: [Error reading file] {e}")
    return "\n".join(summary)


def extract_csv_summary(folder_path):
    summary = []
    for file in os.listdir(folder_path):
        if file.endswith(".csv"):
            path = os.path.join(folder_path, file)
            if not os.path.exists(folder_path):
                return "Converted folder not found."
            try:
                with open(path, newline='') as f:
                    reader = csv.reader(f)
                    headers = next(reader, [])
                    first_row = next(reader, [])
                    summary.append(
                        f"- {file}: columns = {headers}, sample row = {first_row}"
                    )
            except Exception as e:
                summary.append(f"- {file}: [Error reading file] {e}")
    return "\n".join(summary)

def extract_pdf_text(folder_path):
    summary = []
    for file in os.listdir(folder_path):
        if file.endswith(".pdf"):
            path = os.path.join(folder_path, file)
            try:
                doc = fitz.open(path)
                text = ""
                for page in doc:
                    text += page.get_text()
                doc.close()
                cleaned = text.strip().replace("\n", " ")
                summary.append(f"- {file}:\n  \"{cleaned[:300]}...\"")  # Limit preview
            except Exception as e:
                summary.append(f"- {file}: [Error reading PDF] {e}")
    return "\n".join(summary)

from PIL import Image

def extract_image_info(folder_path):
    summary = []
    for file in os.listdir(folder_path):
        if file.lower().endswith((".jpg", ".jpeg", ".png")):
            path = os.path.join(folder_path, file)
            try:
                with Image.open(path) as img:
                    format = img.format
                    size = img.size  # (width, height)
                    summary.append(f"- {file}: format = {format}, size = {size[0]}x{size[1]}")
            except Exception as e:
                summary.append(f"- {file}: [Error reading image] {e}")
    return "\n".join(summary)