from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, **kwargs):
        return iterable

from .constants import GenerationStatus
from .data_splitter import apply_split_strategy
from .models.gguf_adapter import GGUFAdapter
from .schemas import FrameworkConfig, InferenceRecord
from .writers import append_jsonl

def _load_dataset(path: str) -> list[dict[str, Any]]:
    records = []
    p = Path(path)
    
    if p.is_dir():
        files = list(p.glob("*.jsonl"))
    else:
        files = [p]

    for f_path in files:
        with open(f_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
    return records

def _load_prompt_template(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("instruction_text", "")

def _build_prompt(record: dict[str, Any], template_text: str) -> str:
    source_lang = record.get("source_lang", "")
    target_langs = record.get("target_lang", "")
    
    if isinstance(target_langs, list):
        target_str = ", ".join(target_langs)
    else:
        target_str = str(target_langs)
        
    source_text = record.get("source_text", "")
    family = record.get("family", "")

    if template_text:
        formatted_instruction = template_text.format(
            source_lang_display=source_lang,
            family=family,
            target_lang_display=target_str
        )
        return f"{formatted_instruction}\nSOURCE:\n{source_text}"
    
    return (
        f"Translate the following text from {source_lang} to {target_str}.\n\n"
        f"Text: {source_text}\n\n"
        f"Translation:"
    )

def _get_processed_ids(output_dir: Path) -> set[str]:
    processed = set()
    if output_dir.exists():
        for file_path in output_dir.glob("*.jsonl"):
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        try:
                            record = json.loads(line)
                            if "data_id" in record:
                                processed.add(record["data_id"])
                        except json.JSONDecodeError:
                            pass
    return processed

def run(config: FrameworkConfig, output_base_dir: str) -> dict[str, dict[str, Any]]:
    dataset = _load_dataset(config.dataset_path)
    
    seed = config.seed if config.seed is not None else 42
    dataset = apply_split_strategy(
        dataset,
        config.split_strategy,
        config.stratified_target_size,
        seed
    )

    template_text = ""
    if config.prompt_template_path:
        template_text = _load_prompt_template(config.prompt_template_path)

    timing: dict[str, dict[str, Any]] = {}

    for model_config in config.models:
        model_run_start = time.time()
        
        model_output_dir = Path(output_base_dir) / model_config.model_name
        model_output_dir.mkdir(parents=True, exist_ok=True)
        
        processed_ids = _get_processed_ids(model_output_dir)
        pending_dataset = [item for item in dataset if item.get("data_id") not in processed_ids]
        
        if not pending_dataset:
            print(f"Skipping {model_config.model_name} (all {len(dataset)} items already processed).")
            timing[model_config.model_name] = {
                "total_time": 0.0,
                "num_prompts": 0,
            }
            continue
            
        print(f"Running {model_config.model_name}: {len(pending_dataset)} items pending ({len(processed_ids)} already done).")

        from datetime import datetime
        now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = model_output_dir / f"output_{now_str}.jsonl"

        adapter = GGUFAdapter(model_config)
        
        processed_count = 0

        try:
            batch_size = getattr(config, "batch_size", 1)
            
            for i in tqdm(range(0, len(pending_dataset), batch_size), desc=f"Inferencing {model_config.model_name}"):
                batch_items = pending_dataset[i:i + batch_size]
                prompts = [_build_prompt(item, template_text) for item in batch_items]
                
                try:
                    results = adapter.generate_batch(
                        prompts,
                        max_output_tokens=config.max_output_tokens,
                        temperature=config.temperature,
                        top_p=config.top_p,
                        top_k=config.top_k,
                        repeat_penalty=config.repeat_penalty,
                        seed=config.seed,
                        disable_reasoning=config.disable_reasoning,
                        calculate_latency=config.calculate_latency,
                    )
                except Exception as e:
                    # If entire batch fails completely
                    results = []
                    for _ in batch_items:
                        mock = type("MockResult", (), {
                            "raw_response": "",
                            "status": GenerationStatus.ERROR,
                            "input_tokens": 0,
                            "output_tokens": 0,
                            "latency_ms": 0.0,
                            "error_message": f"Adapter exception in batch: {str(e)}"
                        })()
                        results.append(mock)

                for item, result in zip(batch_items, results):
                    target_langs = item.get("target_lang", [])
                    if isinstance(target_langs, str):
                        target_langs = [target_langs]

                    record = InferenceRecord(
                        data_id=item.get("data_id", ""),
                        alignment_id=item.get("alignment_id", ""),
                        family=item.get("family", ""),
                        translation_direction=item.get("translation_direction", ""),
                        source_lang=item.get("source_lang", ""),
                        target_lang=target_langs,
                        source_text=item.get("source_text", ""),
                        reference_text_ind=item.get("reference_text_ind"),
                        reference_text_eng=item.get("reference_text_eng"),
                        model_name=model_config.model_name,
                        generated_text=result.raw_response,
                        generation_status=result.status,
                        input_tokens=result.input_tokens,
                        output_tokens=result.output_tokens,
                        latency_ms=result.latency_ms,
                        error_message=result.error_message,
                    )
                    
                    append_jsonl(record, output_path)
                    processed_count += 1
                
        finally:
            adapter.close()

        timing[model_config.model_name] = {
            "total_time": time.time() - model_run_start,
            "num_prompts": processed_count,
        }

    return timing
