from __future__ import annotations

from pathlib import Path

import yaml

from .schemas import FrameworkConfig, ModelConfig

def load_config(config_path: str | Path) -> FrameworkConfig:
    config_path_obj = Path(config_path).resolve()
    with open(config_path_obj, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    models = [
        ModelConfig(
            model_name=m["model_name"],
            model_path=m["model_path"],
            n_ctx=m.get("n_ctx", 8192),
            n_gpu_layers=m.get("n_gpu_layers", 99),
            flash_attn=m.get("flash_attn", False),
            n_batch=m.get("n_batch", 512),
            n_ubatch=m.get("n_ubatch", 512),
            type_k=m.get("type_k", "q4_0"),
            type_v=m.get("type_v", "q4_0"),
        )
        for m in raw.get("models", [])
    ]

    dataset_path = str(raw["dataset_path"])
    dataset_path_obj = Path(dataset_path)
    if not dataset_path_obj.is_absolute():
        dataset_path_obj = (config_path_obj.parent / dataset_path).resolve()

    prompt_template_path = str(raw.get("prompt_template_path", ""))
    if prompt_template_path:
        pt_path_obj = Path(prompt_template_path)
        if not pt_path_obj.is_absolute():
            pt_path_obj = (config_path_obj.parent / prompt_template_path).resolve()
        prompt_template_path = str(pt_path_obj)

    return FrameworkConfig(
        models=models,
        dataset_path=str(dataset_path_obj),
        prompt_template_path=prompt_template_path,
        max_output_tokens=raw.get("max_output_tokens", 512),
        temperature=raw.get("temperature", 0.0),
        seed=raw.get("seed"),
        top_p=raw.get("top_p", 0.95),
        top_k=raw.get("top_k", 40),
        repeat_penalty=raw.get("repeat_penalty", 1.1),
        disable_reasoning=raw.get("disable_reasoning", True),
        split_strategy=raw.get("split_strategy", "full"),
        stratified_target_size=raw.get("stratified_target_size", 1000),
        batch_size=raw.get("batch_size", 1),
        calculate_latency=raw.get("calculate_latency", False),
    )
