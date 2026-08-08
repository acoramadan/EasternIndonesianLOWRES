import os
import json
import glob

base_dir = r"d:\aco\research\mongondow\src\data\scraped"
folders = [f for f in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, f))]

all_data = {}

for folder in folders:
    merged_filename = f"{folder}_merged.json"
    merged_filepath = os.path.join(base_dir, folder, merged_filename)
    
    if os.path.exists(merged_filepath):
        try:
            with open(merged_filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                all_data[folder] = data
        except Exception as e:
            print(f"Error reading {merged_filepath}: {e}")

output_file = os.path.join(base_dir, "all_languages_merged.json")

print("Writing all languages to", output_file)
with open(output_file, "w", encoding="utf-8") as out:
    json.dump(all_data, out, ensure_ascii=False, indent=2)

print(f"Successfully merged {len(all_data)} languages into a single file.")
