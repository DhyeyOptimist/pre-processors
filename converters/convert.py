#convert heic to jpg

import os
from PIL import Image
import pillow_heif

def convert_heic_to_jpg(input_folder, output_folder):
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(".heic"):
            input_path = os.path.join(input_folder, filename)
            output_filename = os.path.splitext(filename)[0] + ".jpg"
            output_path = os.path.join(output_folder, output_filename)
            try:
                heif_file = pillow_heif.read_heif(input_path)
                image = Image.frombytes(
                    heif_file.mode,
                    heif_file.size,
                    heif_file.data,
                    "raw"
                )
                image.save(output_path, "JPEG")
                print(f"[✓] Converted: {filename} → {output_filename}")
            except Exception as e:
                print(f"[!] Failed to convert {filename}: {e}")

if __name__ == "__main__":
    input_dir = os.path.join(os.getcwd(), "files")
    output_dir = os.path.join(os.getcwd(), "converted")
    os.makedirs(output_dir, exist_ok=True)

    convert_heic_to_jpg(input_dir, output_dir)