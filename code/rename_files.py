import csv
import os

folder_path = r"data\on_off_10sec"  # or "/path/to/files" on macOS/Linux
csv_file = r"data\on_off_10sec\250110_filenames.csv"

with open(csv_file, newline='') as f:
    reader = csv.reader(f)
    for row in reader:
        old_name, new_name = row
        old_path = os.path.join(folder_path, old_name)
        new_path = os.path.join(folder_path, new_name)
        if os.path.exists(old_path):
            os.rename(old_path, new_path)
            print(f"Renamed {old_name} to {new_name}")
        else:
            print(f"File not found: {old_name}")