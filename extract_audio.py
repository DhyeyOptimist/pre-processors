# python3 extract_audio.py
import os
import subprocess

def convert_video_to_audio(input_folder, output_folder):
    for filename in os.listdir(input_folder):
        if filename.lower().endswith((".mp4", ".mov", ".mkv")):
            input_path = os.path.join(input_folder, filename)
            base_name = os.path.splitext(filename)[0]
            output_filename = base_name + ".mp3"
            output_path = os.path.join(output_folder, output_filename)

            try:
                command = [
                    "ffmpeg",
                    "-i", input_path,
                    "-vn",  # no video
                    "-acodec", "libmp3lame",  # use mp3 format
                    output_path
                ]
                subprocess.run(command, check=True)
                print(f"[✓] Converted: {filename} → {output_filename}")
            except Exception as e:
                print(f"[!] Failed to convert {filename}: {e}")

if __name__ == "__main__":
    input_dir = os.path.join(os.getcwd(), "files")
    output_dir = os.path.join(os.getcwd(), "converted")
    os.makedirs(output_dir, exist_ok=True)

    convert_video_to_audio(input_dir, output_dir)