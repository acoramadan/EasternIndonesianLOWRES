"""
Bible Scraper for alkitab.mobi
Scrapes all verses from all languages defined in the URL JSON files.
Supports resume capability - skips already scraped books.
"""

import json
import os
import re
import time
import sys
import glob
import traceback
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from html.parser import HTMLParser

# Fix Windows console encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')


# ============================================================
# HTML Parser - extracts verses from alkitab.mobi HTML
# ============================================================
class VerseParser(HTMLParser):
    """
    Parses alkitab.mobi HTML to extract verses.
    
    Target HTML structure:
    <p>
      <span class="reftext">
        <a name="v1" href="...">1</a>
      </span>
      Verse text here...
    </p>
    """
    
    def __init__(self):
        super().__init__()
        self.verses = []
        self.current_verse_num = None
        self.current_text = []
        self.in_reftext = False
        self.in_reftext_a = False
        self.in_verse_p = False
        self.in_footnote = False
        self.depth = 0
        self.p_depth = 0
        
    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        
        if tag == 'span' and attr_dict.get('class', '') == 'reftext':
            self.in_reftext = True
            return
            
        if self.in_reftext and tag == 'a':
            self.in_reftext_a = True
            return
        
        # Detect footnote/sup elements to skip
        if tag in ('sup', 'span') and self.in_verse_p:
            cls = attr_dict.get('class', '')
            if 'footnote' in cls or 'note' in cls or tag == 'sup':
                self.in_footnote = True
                return
        
        if tag == 'p':
            self.p_depth += 1
            
    def handle_endtag(self, tag):
        if tag == 'span' and self.in_reftext:
            self.in_reftext = False
            # After reftext span closes, we are now reading verse text
            if self.current_verse_num is not None:
                self.in_verse_p = True
            return
            
        if tag == 'a' and self.in_reftext_a:
            self.in_reftext_a = False
            return
            
        if tag in ('sup', 'span') and self.in_footnote:
            self.in_footnote = False
            return
            
        if tag == 'p':
            self.p_depth -= 1
            if self.in_verse_p:
                # End of verse paragraph
                text = ''.join(self.current_text).strip()
                # Clean up whitespace
                text = re.sub(r'\s+', ' ', text).strip()
                if text and self.current_verse_num is not None:
                    self.verses.append({
                        'verse_number': self.current_verse_num,
                        'text': text
                    })
                self.current_verse_num = None
                self.current_text = []
                self.in_verse_p = False
    
    def handle_data(self, data):
        if self.in_reftext_a:
            # This is the verse number
            try:
                self.current_verse_num = int(data.strip())
                self.current_text = []
            except ValueError:
                pass
            return
            
        if self.in_verse_p and not self.in_footnote and not self.in_reftext:
            self.current_text.append(data)


def fetch_url(url, max_retries=3, delay=1.5):
    """Fetch a URL with retries and delay."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    for attempt in range(max_retries):
        try:
            req = Request(url, headers=headers)
            with urlopen(req, timeout=30) as response:
                html = response.read().decode('utf-8', errors='replace')
                return html
        except (HTTPError, URLError, Exception) as e:
            if attempt < max_retries - 1:
                wait = delay * (attempt + 1)
                print(f"    [RETRY {attempt+1}/{max_retries}] Error fetching {url}: {e}. Waiting {wait}s...")
                time.sleep(wait)
            else:
                print(f"    [FAILED] Could not fetch {url} after {max_retries} attempts: {e}")
                return None
    return None


def parse_verses(html):
    """Parse verses from HTML content."""
    parser = VerseParser()
    parser.feed(html)
    return parser.verses


def scrape_chapter(url, delay=1.0):
    """Scrape a single chapter URL and return verses."""
    time.sleep(delay)
    html = fetch_url(url)
    if html is None:
        return []
    
    verses = parse_verses(html)
    return verses


def scrape_language(lang_name, lang_json_path, output_dir, request_delay=1.0):
    """Scrape all books for a single language."""
    
    with open(lang_json_path, 'r', encoding='utf-8') as f:
        books_data = json.load(f)
    
    os.makedirs(output_dir, exist_ok=True)
    
    total_books = len(books_data)
    books_done = 0
    books_skipped = 0
    
    for book_name, book_info in books_data.items():
        urls = book_info.get('url', [])
        if not urls:
            continue
        
        # Determine book_id from the URL pattern: .../lang/CODE/chapter
        # e.g., https://alkitab.mobi/mongondow/Mat/1 -> book_id = MAT
        first_url = urls[0]
        url_parts = first_url.rstrip('/').split('/')
        # url_parts: ['https:', '', 'alkitab.mobi', 'mongondow', 'Mat', '1']
        book_code = url_parts[-2] if len(url_parts) >= 3 else book_name[:3]
        book_id = book_code.upper()
        
        # Check if already scraped
        safe_name = book_name.replace(' ', '_').replace('/', '_').replace('-', '_')
        out_file = os.path.join(output_dir, f"{safe_name}.json")
        
        if os.path.exists(out_file):
            # Verify it has the right number of chapters
            try:
                with open(out_file, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
                if len(existing.get('chapters', [])) == len(urls):
                    books_skipped += 1
                    books_done += 1
                    print(f"  [{books_done}/{total_books}] SKIP {book_name} (already scraped)")
                    continue
            except (json.JSONDecodeError, KeyError):
                pass  # Re-scrape if file is corrupted
        
        books_done += 1
        print(f"  [{books_done}/{total_books}] Scraping {book_name} ({len(urls)} chapters)...")
        
        chapters = []
        for url in urls:
            # Extract chapter number from URL
            chapter_num = int(url.rstrip('/').split('/')[-1])
            
            verses = scrape_chapter(url, delay=request_delay)
            
            chapters.append({
                'chapter_number': chapter_num,
                'source_url': url,
                'verses': verses
            })
            
            verse_count = len(verses)
            status = "OK" if verse_count > 0 else "WARN:0 verses"
            print(f"    Ch.{chapter_num}: {verse_count} verses [{status}]")
        
        # Build output
        result = {
            'book_id': book_id,
            'book_name': book_name,
            'chapters': chapters
        }
        
        with open(out_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        total_verses = sum(len(ch['verses']) for ch in chapters)
        print(f"    -> Saved {book_name}: {len(chapters)} chapters, {total_verses} verses")
    
    if books_skipped > 0:
        print(f"  (Skipped {books_skipped} already-scraped books)")


def main():
    base_dir = r"d:\aco\research\mongondow\data"
    scraped_dir = os.path.join(base_dir, "scraped")
    
    # Discover all language JSON files (exclude metadata.json)
    all_json_files = glob.glob(os.path.join(base_dir, "*.json"))
    lang_files = []
    exclude = {'metadata.json'}
    
    for fpath in sorted(all_json_files):
        fname = os.path.basename(fpath)
        if fname not in exclude:
            lang_name = os.path.splitext(fname)[0]
            lang_files.append((lang_name, fpath))
    
    print(f"Found {len(lang_files)} languages to scrape.")
    print(f"Output directory: {scraped_dir}")
    print("=" * 60)
    
    # Count total URLs across all languages
    total_urls = 0
    for lang_name, lang_path in lang_files:
        with open(lang_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for book_info in data.values():
            total_urls += len(book_info.get('url', []))
    
    print(f"Total URLs to scrape: {total_urls}")
    print("=" * 60)
    
    for idx, (lang_name, lang_path) in enumerate(lang_files, 1):
        lang_output = os.path.join(scraped_dir, lang_name)
        print(f"\n[{idx}/{len(lang_files)}] === {lang_name.upper()} ===")
        
        try:
            scrape_language(lang_name, lang_path, lang_output, request_delay=1.0)
        except KeyboardInterrupt:
            print("\n\nInterrupted by user. Progress has been saved. Run again to resume.")
            sys.exit(1)
        except Exception as e:
            print(f"  ERROR processing {lang_name}: {e}")
            traceback.print_exc()
            continue
    
    print("\n" + "=" * 60)
    print("SCRAPING COMPLETE!")
    
    # Summary
    print("\nSummary per language:")
    for lang_name, _ in lang_files:
        lang_dir = os.path.join(scraped_dir, lang_name)
        if os.path.exists(lang_dir):
            files = [f for f in os.listdir(lang_dir) if f.endswith('.json')]
            total_v = 0
            for fpath in files:
                try:
                    with open(os.path.join(lang_dir, fpath), 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    total_v += sum(len(ch['verses']) for ch in data.get('chapters', []))
                except:
                    pass
            print(f"  {lang_name}: {len(files)} books, {total_v} total verses")


if __name__ == '__main__':
    main()
