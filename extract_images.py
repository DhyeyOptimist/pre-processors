


import os
import subprocess

def extract_frames_from_video(video_path, output_folder, interval=10):
    os.makedirs(output_folder, exist_ok=True)

    # Output filename pattern
    output_pattern = os.path.join(output_folder, "frame_%03d.jpg")

    command = [
        "ffmpeg",
        "-i", video_path,
        "-vf", f"fps=1/{interval}",  # 1 frame every `interval` seconds
        "-qscale:v", "1",  # quality level (1 = best, 31 = worst)
        output_pattern
    ]

    try:
        subprocess.run(command, check=True)
        print(f"[✓] Extracted frames from {video_path}")
    except subprocess.CalledProcessError as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    input_video = os.path.join(os.getcwd(), "files", "short.mp4")
    output_dir = os.path.join(os.getcwd(), "frames")
    
    extract_frames_from_video(input_video, output_dir, interval=1)

# python3 extract_images.py run this cmd and also change the interval
