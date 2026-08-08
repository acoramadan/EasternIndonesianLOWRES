import os
import json
import glob

base_dir = r"d:\aco\research\mongondow\src\data\scraped"
folders = [f for f in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, f))]

for folder in folders:
    folder_path = os.path.join(base_dir, folder)
    json_files = glob.glob(os.path.join(folder_path, "*.json"))
    
    # Exclude any previously merged file if it exists
    merged_filename = f"{folder}_merged.json"
    merged_filepath = os.path.join(folder_path, merged_filename)
    if merged_filepath in json_files:
        json_files.remove(merged_filepath)
        
    all_books = []
    for jf in json_files:
        try:
            with open(jf, "r", encoding="utf-8") as f:
                data = json.load(f)
                all_books.append(data)
        except Exception as e:
            print(f"Error reading {jf}: {e}")
            
    if all_books:
        with open(merged_filepath, "w", encoding="utf-8") as out:
            json.dump(all_books, out, ensure_ascii=False, indent=2)
        print(f"Merged {len(json_files)} files into {merged_filepath}")
