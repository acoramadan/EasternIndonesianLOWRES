from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .constants import GenerationStatus

@dataclass
class ModelConfig:
    model_name: str
    model_path: str
    repo_filename: str | None = None
    n_ctx: int = 8192
    n_gpu_layers: int = 99
    flash_attn: bool = False
    n_batch: int = 512
    n_ubatch: int = 512
    type_k: str = "q4_0"
    type_v: str = "q4_0"

@dataclass
class FrameworkConfig:
    models: list[ModelConfig]
    dataset_path: str
    prompt_template_path: str = ""
    max_output_tokens: int = 512
    temperature: float = 0.0
    seed: int | None = None
    top_p: float = 0.95
    top_k: int = 40
    repeat_penalty: float = 1.1
    disable_reasoning: bool = True
    split_strategy: str = "full"
    stratified_target_size: int = 1000
    batch_size: int = 1
    calculate_latency: bool = False

@dataclass
class GenerationResult:
    raw_response: str
    status: GenerationStatus
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: float = 0.0
    error_message: str | None = None

@dataclass
class InferenceRecord:
    data_id: str
    alignment_id: str
    family: str
    translation_direction: str
    source_lang: str
    target_lang: list[str]
    source_text: str
    model_name: str
    generated_text: str
    generation_status: GenerationStatus
    input_tokens: int
    output_tokens: int
    latency_ms: float
    reference_text_ind: str | None = None
    reference_text_eng: str | None = None
    error_message: str | None = None
