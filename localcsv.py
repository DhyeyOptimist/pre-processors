
import pandas as pd
import os

def convert_excel_to_csv(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith(".xls") or filename.endswith(".xlsx"):
            file_path = os.path.join(folder_path, filename)

            try:
                # Choose the correct engine
                engine = 'xlrd' if filename.endswith('.xls') else 'openpyxl'
                df = pd.read_excel(file_path, engine=engine)

                # Convert to .csv
                new_filename = filename.rsplit(".", 1)[0] + ".csv"
                new_path = os.path.join(folder_path, new_filename)

                df.to_csv(new_path, index=False)
                print(f"[✓] Converted {filename} to {new_filename}")
            except Exception as e:
                print(f"[!] Failed to convert {filename}: {e}")

if __name__ == "__main__":
    folder_path = os.path.join(os.getcwd(), "files")
    convert_excel_to_csv(folder_path)

# import pandas as pd
# import os

# def convert_xls_to_csv(folder_path):
#     # List all files in the given folder
#     for filename in os.listdir(folder_path):
#         if filename.endswith(".xls"):
#             # Build full path to the .xls file
#             file_path = os.path.join(folder_path, filename)

#             # Read Excel file using pandas
#             try:
#                 df = pd.read_excel(file_path, engine='xlrd')

#                 # Create new filename by replacing .xls with .csv
#                 new_filename = filename.replace(".xls", ".csv")
#                 new_path = os.path.join(folder_path, new_filename)

#                 # Write CSV file
#                 df.to_csv(new_path, index=False)
#                 print(f"[✓] Converted {filename} to {new_filename}")
#             except Exception as e:
#                 print(f"[!] Failed to convert {filename}: {e}")


# if __name__ == "__main__":
#     # Adjust folder path relative to this Python file
#     folder_path = os.path.join(os.getcwd(), "/Users/dhyeysutariya/Developer/preprocessors/files")
#     convert_xls_to_csv(folder_path)


# soffice --headless --convert-to pdf --outdir ./converted ./files/example.pptx 
# convert into pdf cmd 
