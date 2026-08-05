import os, json

directory = r"d:\aco\research\mongondow\src\output\pilot_dataset"
for filename in os.listdir(directory):
    if filename.endswith(".jsonl"):
        with open(os.path.join(directory, filename), 'r', encoding='utf-8') as f:
            for line in f:
                data = json.loads(line)
                for key in ['source_text', 'reference_text_ind', 'reference_text_eng']:
                    if key in data and isinstance(data[key], str):
                        val = data[key]
                        if '"' in val or ';' in val or '“' in val or '”' in val or '\\' in val:
                            print(f"{filename} {key}: {repr(val)}")
