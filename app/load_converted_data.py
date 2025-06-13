import os
import csv

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
    