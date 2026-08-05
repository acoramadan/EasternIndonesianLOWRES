import json
import os

def generate_urls():
    base_dir = r"d:\aco\research\mongondow\data"
    metadata_path = os.path.join(base_dir, "metadata.json")
    
    with open(metadata_path, 'r', encoding='utf-8') as f:
        data_list = json.load(f)
        
    if isinstance(data_list, list):
        data = data_list[0]
    else:
        data = data_list
        
    link_url = data.get("link_url", "https://alkitab.mobi/")
    verse_lr = data.get("verse_lr", {})
    verse_hr = data.get("vers_hr", {})
    
    lr_langs = []
    hr_langs = []
    
    for key, val in data.items():
        if isinstance(val, list):
            if key.endswith('_lr'):
                lr_langs.extend(val)
            elif key.endswith('_hr'):
                hr_langs.extend(val)
                
    # Function to generate book dict
    def get_book_dict(lang_code, verse_data):
        result = {}
        for book_name, book_info in verse_data.items():
            verse_code = book_info['code']
            chapters = int(book_info['chapters'])
            urls = []
            for i in range(1, chapters + 1):
                url = f"{link_url}{lang_code}/{verse_code}/{i}"
                urls.append(url)
            result[book_name] = {"url": urls}
        return result

    # Process LR languages
    for lang in lr_langs:
        lang_data = get_book_dict(lang, verse_lr)
        out_path = os.path.join(base_dir, f"{lang}.json")
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(lang_data, f, indent=4)
            
    # Process HR languages
    for lang in hr_langs:
        lang_data = {}
        # HR supports both verse_lr and vers_hr
        # Let's merge both
        lang_data.update(get_book_dict(lang, verse_lr))
        lang_data.update(get_book_dict(lang, verse_hr))
        
        out_path = os.path.join(base_dir, f"{lang}.json")
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(lang_data, f, indent=4)
            
    print(f"Successfully generated JSON files for {len(lr_langs)} LR languages and {len(hr_langs)} HR languages.")

if __name__ == '__main__':
    generate_urls()
