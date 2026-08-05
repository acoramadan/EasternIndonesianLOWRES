"""Quick test: scrape one chapter to validate the parser works correctly."""
import json
import sys
sys.path.insert(0, r'd:\aco\research\mongondow\data')
from scraper import fetch_url, parse_verses

# Test with a known URL
test_url = "https://alkitab.mobi/makasar/Kej/1"
print(f"Testing: {test_url}")

html = fetch_url(test_url)
if html is None:
    print("FAILED to fetch URL")
    sys.exit(1)

# Save raw HTML for debugging
with open(r'd:\aco\research\mongondow\data\test_debug.html', 'w', encoding='utf-8') as f:
    f.write(html)
print(f"Saved raw HTML ({len(html)} bytes) to test_debug.html")

verses = parse_verses(html)
print(f"\nFound {len(verses)} verses:")
for v in verses[:5]:
    print(f"  v{v['verse_number']}: {v['text'][:100]}...")

if len(verses) > 5:
    print(f"  ... and {len(verses)-5} more verses")

# Also test a LR language
test_url2 = "https://alkitab.mobi/mongondow/Mat/1"
print(f"\nTesting: {test_url2}")
html2 = fetch_url(test_url2)
if html2:
    verses2 = parse_verses(html2)
    print(f"Found {len(verses2)} verses:")
    for v in verses2[:3]:
        print(f"  v{v['verse_number']}: {v['text'][:100]}...")
