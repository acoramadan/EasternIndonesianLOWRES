from __future__ import annotations

import re
import time

from llama_cpp import Llama

from .base import Model
from ..constants import GenerationStatus
from ..schemas import GenerationResult, ModelConfig


class GGUFAdapter(Model):
    def __init__(self, config: ModelConfig) -> None:
        super().__init__(config)

        path = self.config.model_path

        if not path.lower().endswith(".gguf") and not __import__("pathlib").Path(path).exists():
            from huggingface_hub import HfApi, hf_hub_download
            api = HfApi()
            files = api.list_repo_files(repo_id=path)
            gguf_files = [f for f in files if f.lower().endswith(".gguf")]
            if not gguf_files:
                raise ValueError(f"No .gguf files found in repo {path}")
            target_file = next((f for f in gguf_files if "q4_k_m" in f.lower()), gguf_files[0])
            path = hf_hub_download(repo_id=path, filename=target_file)

        import llama_cpp

        def get_ggml_type(type_str: str):
            attr_name = f"GGML_TYPE_{type_str.upper()}"
            return getattr(llama_cpp, attr_name, getattr(llama_cpp, "GGML_TYPE_F16", 1))

        type_k_val = get_ggml_type(self.config.type_k)
        type_v_val = get_ggml_type(self.config.type_v)

        self.llm = self._create_llama_with_fallback(path, type_k_val, type_v_val)

    def _create_llama_with_fallback(self, path: str, type_k_val, type_v_val) -> Llama:
        import llama_cpp

        f16_type = getattr(llama_cpp, "GGML_TYPE_F16", 1)

        fallback_chain = [
            {
                "label": "user config",
                "flash_attn": self.config.flash_attn,
                "n_ctx": self.config.n_ctx,
                "type_k": type_k_val,
                "type_v": type_v_val,
                "n_batch": self.config.n_batch,
                "n_ubatch": self.config.n_ubatch,
            },
            {
                "label": "flash_attn=False",
                "flash_attn": False,
                "n_ctx": self.config.n_ctx,
                "type_k": type_k_val,
                "type_v": type_v_val,
                "n_batch": self.config.n_batch,
                "n_ubatch": self.config.n_ubatch,
            },
            {
                "label": "flash_attn=False + KV cache f16",
                "flash_attn": False,
                "n_ctx": self.config.n_ctx,
                "type_k": f16_type,
                "type_v": f16_type,
                "n_batch": self.config.n_batch,
                "n_ubatch": self.config.n_ubatch,
            },
            {
                "label": "flash_attn=False + KV f16 + n_ctx=4096",
                "flash_attn": False,
                "n_ctx": min(self.config.n_ctx, 4096),
                "type_k": f16_type,
                "type_v": f16_type,
                "n_batch": min(self.config.n_batch, 512),
                "n_ubatch": min(self.config.n_ubatch, 512),
            },
            {
                "label": "minimal safe (n_ctx=2048, no flash, KV f16)",
                "flash_attn": False,
                "n_ctx": 2048,
                "type_k": f16_type,
                "type_v": f16_type,
                "n_batch": 512,
                "n_ubatch": 512,
            },
        ]

        last_err = None
        for i, params in enumerate(fallback_chain):
            try:
                llm = Llama(
                    model_path=path,
                    n_ctx=params["n_ctx"],
                    n_gpu_layers=self.config.n_gpu_layers,
                    flash_attn=params["flash_attn"],
                    n_batch=params["n_batch"],
                    n_ubatch=params["n_ubatch"],
                    type_k=params["type_k"],
                    type_v=params["type_v"],
                    verbose=False,
                )
                if i > 0:
                    print(f"[INFO] Context created successfully with: {params['label']}")
                return llm
            except Exception as e:
                last_err = e
                if i < len(fallback_chain) - 1:
                    next_label = fallback_chain[i + 1]["label"]
                    print(
                        f"[WARN] Failed to create context with [{params['label']}]: {e}"
                        f"\n       Trying fallback: {next_label}..."
                    )

        raise RuntimeError(
            f"Failed to create llama context after all fallback attempts. "
            f"Last error: {last_err}"
        )

    def generate(
        self,
        prompt: str,
        *,
        max_output_tokens: int = 512,
        temperature: float = 0.0,
        top_p: float = 0.95,
        top_k: int = 40,
        repeat_penalty: float = 1.1,
        seed: int | None = None,
        disable_reasoning: bool = True,
        calculate_latency: bool = False,
    ) -> GenerationResult:
        start_time = time.time()

        system_content = (
            "You are a professional translation assistant. "
            "Output ONLY the requested translation. "
            "Do not include any explanations, notes, conversational filler, or reasoning."
        )

        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": prompt},
        ]

        try:
            raw_text = self._try_chat_completion(
                messages=messages,
                max_output_tokens=max_output_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                repeat_penalty=repeat_penalty,
                seed=seed,
                disable_reasoning=disable_reasoning,
            )

            latency = time.time() - start_time

            usage = self._last_usage
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)

            status = GenerationStatus.SUCCESS

            if output_tokens >= max_output_tokens:
                status = GenerationStatus.TRUNCATED
            elif "<think>" in raw_text and "</think>" not in raw_text:
                status = GenerationStatus.FAILED_REASONING_INCOMPLETE
            elif not raw_text.strip():
                status = GenerationStatus.EMPTY

            if disable_reasoning:
                raw_text = re.sub(r"<think>.*?</think>", "", raw_text, flags=re.DOTALL).strip()

            return GenerationResult(
                raw_response=raw_text.strip(),
                status=status,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                latency_ms=latency * 1000 if calculate_latency else 0.0,
            )
        except Exception as e:
            latency = time.time() - start_time
            return GenerationResult(
                raw_response="",
                status=GenerationStatus.ERROR,
                latency_ms=latency * 1000 if calculate_latency else 0.0,
                error_message=str(e),
            )

    def _try_chat_completion(
        self,
        *,
        messages: list[dict],
        max_output_tokens: int,
        temperature: float,
        top_p: float,
        top_k: int,
        repeat_penalty: float,
        seed: int | None,
        disable_reasoning: bool,
    ) -> str:
        self._last_usage = {}

        common_kwargs = dict(
            messages=messages,
            max_tokens=max_output_tokens,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            repeat_penalty=repeat_penalty,
            seed=seed,
        )

        if disable_reasoning:
            try:
                response = self.llm.create_chat_completion(
                    **common_kwargs,
                    chat_template_kwargs={"enable_thinking": False},
                )
                self._last_usage = response.get("usage", {})
                return response["choices"][0]["message"].get("content", "")
            except TypeError:
                pass

        response = self.llm.create_chat_completion(**common_kwargs)
        self._last_usage = response.get("usage", {})
        return response["choices"][0]["message"].get("content", "")

    def generate_batch(
        self,
        prompts: list[str],
        *,
        max_output_tokens: int = 512,
        temperature: float = 0.0,
        top_p: float = 0.95,
        top_k: int = 40,
        repeat_penalty: float = 1.1,
        seed: int | None = None,
        disable_reasoning: bool = True,
        calculate_latency: bool = False,
    ) -> list[GenerationResult]:
        results = []
        for prompt in prompts:
            results.append(
                self.generate(
                    prompt=prompt,
                    max_output_tokens=max_output_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    top_k=top_k,
                    repeat_penalty=repeat_penalty,
                    seed=seed,
                    disable_reasoning=disable_reasoning,
                    calculate_latency=calculate_latency,
                )
            )
        return results

    def close(self) -> None:
        if hasattr(self, "llm"):
            del self.llm
