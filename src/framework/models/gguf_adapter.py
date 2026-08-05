from __future__ import annotations

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
            
        self.llm = Llama(
            model_path=path,
            n_ctx=self.config.n_ctx,
            n_gpu_layers=self.config.n_gpu_layers,
            flash_attn=self.config.flash_attn,
            n_batch=self.config.n_batch,
            n_ubatch=self.config.n_ubatch,
            type_k=type_k_val,
            type_v=type_v_val,
            verbose=False,
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
        
        system_content = "You are a professional translation assistant. Output ONLY the requested translation. Do not include any explanations, notes, conversational filler, or reasoning."
        
        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": prompt}
        ]

        stop_tokens = ["<|im_end|>"]
        if disable_reasoning:
            stop_tokens.extend(["</think>", "<think>"])

        try:
            try:
                # Try the native chat_template_kwargs (like llama-cli) if supported by python bindings
                kwargs = {"chat_template_kwargs": {"enable_thinking": False}} if disable_reasoning else {}
                response = self.llm.create_chat_completion(
                    messages=messages,
                    max_tokens=max_output_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    top_k=top_k,
                    repeat_penalty=repeat_penalty,
                    seed=seed,
                    stop=stop_tokens,
                    **kwargs
                )
                raw_text = response["choices"][0]["message"].get("content", "")
            except TypeError as te:
                # If python wrapper doesn't support chat_template_kwargs yet, fallback to manual template bypass
                if "chat_template_kwargs" in str(te) or "unexpected keyword argument" in str(te):
                    if disable_reasoning:
                        prompt_str = (
                            f"<|im_start|>system\n{system_content}<|im_end|>\n"
                            f"<|im_start|>user\n{prompt}<|im_end|>\n"
                            f"<|im_start|>assistant\n<think>\n\n</think>\n\n"
                        )
                    else:
                        prompt_str = (
                            f"<|im_start|>system\n{system_content}<|im_end|>\n"
                            f"<|im_start|>user\n{prompt}<|im_end|>\n"
                            f"<|im_start|>assistant\n"
                        )
                    
                    response = self.llm(
                        prompt_str,
                        max_tokens=max_output_tokens,
                        temperature=temperature,
                        top_p=top_p,
                        top_k=top_k,
                        repeat_penalty=repeat_penalty,
                        seed=seed,
                        stop=stop_tokens,
                        echo=False,
                    )
                    raw_text = response["choices"][0]["text"]
                else:
                    raise te
            
            latency = time.time() - start_time
            
            usage = response.get("usage", {})
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
                import re
                raw_text = re.sub(r'<think>.*?</think>', '', raw_text, flags=re.DOTALL).strip()

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
        # llama-cpp-python standard Llama API processes single prompts
        # We loop sequentially. True batched generation is best done via vLLM.
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
