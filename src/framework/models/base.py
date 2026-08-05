from __future__ import annotations

from abc import ABC, abstractmethod

from ..schemas import GenerationResult, ModelConfig


class Model(ABC):
    def __init__(self, config: ModelConfig) -> None:
        self.config = config
        self.model_name = config.model_name
        self.model_path = config.model_path

    @abstractmethod
    def generate(
        self,
        prompt: str,
        *,
        max_output_tokens: int = 512,
        temperature: float | None = None,
        calculate_latency: bool = False,
    ) -> GenerationResult:
        raise NotImplementedError

    @abstractmethod
    def generate_batch(
        self,
        prompts: list[str],
        *,
        max_output_tokens: int = 512,
        temperature: float | None = None,
        calculate_latency: bool = False,
    ) -> list[GenerationResult]:
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        raise NotImplementedError
