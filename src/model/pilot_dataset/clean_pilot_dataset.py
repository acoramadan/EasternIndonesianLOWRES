import os
import json
import re

def clean_dataset():
    directory = r"d:\aco\research\mongondow\src\output\pilot_dataset"
    
    # Regex to match verse references like (3:17), (1-15), (3:17, 18)
    # It looks for opening parenthesis, numbers, and requires at least one colon or dash
    # followed by numbers/commas/spaces, and closing parenthesis.
    pattern = re.compile(r'\(\s*\d+[\s\d,]*[:\-][\s\d:\-,]*\)')
    
    files_processed = 0
    records_cleaned = 0
    
    for filename in os.listdir(directory):
        if filename.endswith(".jsonl"):
            filepath = os.path.join(directory, filename)
            cleaned_lines = []
            file_modified = False
            
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    data = json.loads(line)
                    modified = False
                    
                    for key in ['source_text', 'reference_text_ind', 'reference_text_eng']:
                        if key in data and isinstance(data[key], str):
                            original_text = data[key]
                            
                            # Remove the matching verse patterns
                            cleaned_text = pattern.sub(' ', original_text)
                            
                            # Remove quotes (straight, smart), backslashes, semicolons, and replace them
                            # The user specifically mentioned \" and ;
                            for char in ['"', '\\', ';', '“', '”', '‘', '’']:
                                cleaned_text = cleaned_text.replace(char, '')
                            
                            # Clean up resulting multiple spaces and strip leading/trailing spaces
                            cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
                            
                            if cleaned_text != original_text:
                                data[key] = cleaned_text
                                modified = True
                    
                    if modified:
                        records_cleaned += 1
                        file_modified = True
                        
                    cleaned_lines.append(json.dumps(data, ensure_ascii=False))
            
            if file_modified:
                with open(filepath, 'w', encoding='utf-8') as f:
                    for line in cleaned_lines:
                        f.write(line + '\n')
            
            files_processed += 1
            print(f"Processed {filename}")
            
    print(f"Done. Processed {files_processed} files. Cleaned {records_cleaned} records.")

if __name__ == "__main__":
    clean_dataset()
