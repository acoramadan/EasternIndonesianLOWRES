import sys
from pathlib import Path

from framework.yaml_config import load_config
from framework.runner import run

def main() -> None:
    base_dir = Path(__file__).resolve().parent
    config_path = base_dir / "configs" / "config.yaml"
    output_dir = base_dir / "output" / "inference_output"

    config = load_config(config_path)
    config.dataset_path = str(base_dir / "data" / "test_datasets")
    config.split_strategy = "test_2"
    config.calculate_latency = True

    print(f"Testing dataset from: {config.dataset_path}")
    print(f"Using split strategy: {config.split_strategy} (Max 2 per language)")
    
    timing_results = run(config, str(output_dir))

    for model_name, stats in timing_results.items():
        total_time = stats["total_time"]
        num_prompts = stats["num_prompts"]
        
        if num_prompts > 0:
            avg_time = total_time / num_prompts
            print(f"  {model_name}: {avg_time:.2f}s per prompt (Total: {total_time:.2f}s for {num_prompts} prompts)")
        else:
            print(f"  {model_name}: 0 prompts processed")

if __name__ == "__main__":
    main()
