import subprocess
import sys
import os
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

scripts = [
    "01_load_and_flatten.py",
    "02_descriptive_stats.py",
    "03_visualizations_static.py",
    "04_visualizations_plotly.py",
    "05_text_analysis.py",
]

print("=" * 70)
print("  RUNNING FULL EDA PIPELINE")
print("=" * 70)

total_start = time.time()

for i, script in enumerate(scripts, 1):
    script_path = os.path.join(SCRIPT_DIR, script)
    print(f"\n{'_' * 70}")
    print(f"  [{i}/{len(scripts)}] Running: {script}")
    print(f"{'_' * 70}\n")

    start = time.time()
    result = subprocess.run(
        [sys.executable, script_path],
        cwd=SCRIPT_DIR,
        capture_output=False
    )
    elapsed = time.time() - start

    if result.returncode != 0:
        print(f"\nFAILED: {script} (exit code {result.returncode})")
        print(f"   Pipeline stopped.")
        sys.exit(1)

    print(f"\n  {script} finished in {elapsed:.1f} seconds")

total_elapsed = time.time() - total_start
print(f"\n{'=' * 70}")
print(f"  FULL EDA PIPELINE COMPLETED in {total_elapsed:.1f} seconds")
print(f"{'=' * 70}")
print(f"\nOutput saved in: src/output/eda/")
print(f"  - CSV & Parquet data")
print(f"  - 13 static figures (PNG)")
print(f"  - 7 interactive visualizations (HTML)")
print(f"  - Word frequency, wordcloud, n-gram per language")
print(f"  - Summary reports (TXT)")
