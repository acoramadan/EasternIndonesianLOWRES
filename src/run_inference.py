import sys
from pathlib import Path

from framework.yaml_config import load_config
from framework.runner import run

def main() -> None:
    # Set up paths relative to this script
    base_dir = Path(__file__).resolve().parent
    config_path = base_dir / "configs" / "config.yaml"
    output_dir = base_dir / "output" / "inference_output"

    # Make sure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading configuration from: {config_path}")
    config = load_config(config_path)

    print(f"\n--- Starting Inference ---")
    print(f"Dataset Path: {config.dataset_path}")
    print(f"Split Strategy: {config.split_strategy}")
    if config.split_strategy == "stratified":
        print(f"Stratified Target Size: {config.stratified_target_size}")
    
    print("\nExecuting generation models...")
    timing_results = run(config, str(output_dir))

    print("\n--- Inference Completed ---")
    print("Execution Summary:")
    for model_name, stats in timing_results.items():
        total_time = stats["total_time"]
        num_prompts = stats["num_prompts"]
        
        if num_prompts > 0:
            print(f"  [{model_name}]")
            print(f"    - Prompts Processed: {num_prompts}")
        else:
            print(f"  [{model_name}] processed 0 prompts.")
            
    print(f"\nAll outputs are saved in: {output_dir}")

if __name__ == "__main__":
    main()
