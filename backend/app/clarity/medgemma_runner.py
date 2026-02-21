"""MedGemma Runner for CLARITY.

This module provides a real MedGemma model runner that implements the
RunnerProtocol interface. It is designed for local GPU inference using
the HuggingFace Transformers library.

CRITICAL CONSTRAINTS (M13+M14):
1. Deterministic: same (prompt, seed) → identical output.
2. No gradient tracking (torch.no_grad).
3. Temperature=0, no sampling.
4. Explicit seed control for all random sources.
5. GPU memory budget: ≤12GB for batch=1.
6. Does NOT modify R2L semantics.
7. Gated behind CLARITY_REAL_MODEL environment variable.
8. (M14) Rich mode: optional logprobs/entropy extraction via generate_rich().
9. (M14) Rich mode gated behind CLARITY_RICH_MODE environment variable.
10. (M14) Full logits hash opt-in via CLARITY_RICH_LOGITS_HASH.

This runner is for LOCAL EXECUTION ONLY. It is NOT used in CI.
CI uses the StubbedRunner for synthetic deterministic outputs.

Adapter wiring follows the CLARITY↔R2L boundary contract:
- CLARITY invokes the adapter but does not modify its internals
- Adapter implementation is isolated in this module
- Model loading and inference are fully encapsulated

Usage:
    from app.clarity.medgemma_runner import MedGemmaRunner, is_real_model_enabled

    if is_real_model_enabled():
        runner = MedGemmaRunner()
        result = runner.run(image, prompt, axis, value, seed)

    # Rich mode (M14)
    from app.clarity.rich_generation import is_rich_mode_enabled
    if is_real_model_enabled() and is_rich_mode_enabled():
        rich_result = runner.generate_rich("Analyze this X-ray", seed=42, image=img)
"""

from __future__ import annotations

import hashlib
import math
import os
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from PIL import Image

# Import rich generation types (M14)
from app.clarity.rich_generation import (
    RichGenerationResult,
    RichMetricsSummary,
    compute_logits_hash_streaming,
    create_rich_metrics_summary,
    is_rich_logits_hash_enabled,
    is_rich_mode_enabled,
)

# Environment variable gate
REAL_MODEL_ENV_VAR = "CLARITY_REAL_MODEL"

# Model configuration (locked for M13)
# Note: medgemma-4b-it is the instruction-tuned variant with multimodal support
MODEL_ID = "google/medgemma-4b-it"
MAX_NEW_TOKENS = 512
TEMPERATURE = 0.0
TOP_P = 1.0
DO_SAMPLE = False


def is_real_model_enabled() -> bool:
    """Check if real model execution is enabled.

    Returns:
        True if CLARITY_REAL_MODEL environment variable is set to a truthy value.
    """
    value = os.getenv(REAL_MODEL_ENV_VAR, "").lower()
    return value in ("true", "1", "yes", "on")


@dataclass(frozen=True)
class MedGemmaResult:
    """Result from MedGemma inference.

    Attributes:
        text: The generated text response.
        model_id: The model identifier used.
        seed: The seed used for generation.
        bundle_sha: SHA256 hash of the result for determinism verification.
        metadata: Additional metadata about the run.
    """

    text: str
    model_id: str
    seed: int
    bundle_sha: str
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "bundle_sha": self.bundle_sha,
            "metadata": self.metadata,
            "model_id": self.model_id,
            "seed": self.seed,
            "text": self.text,
        }


def _compute_result_hash(text: str, model_id: str, seed: int) -> str:
    """Compute deterministic hash of inference result.

    Args:
        text: Generated text.
        model_id: Model identifier.
        seed: Seed used.

    Returns:
        SHA256 hex digest.
    """
    content = f"{model_id}|{seed}|{text}"
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _set_deterministic_seed(seed: int) -> None:
    """Set all random sources to deterministic state.

    This must be called before any model inference to ensure
    reproducibility.

    Args:
        seed: The seed value to use.
    """
    import random

    import numpy as np
    import torch

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def _enable_deterministic_mode() -> None:
    """Enable PyTorch deterministic operations.

    This sets all necessary flags for deterministic CUDA operations.
    May impact performance but guarantees reproducibility.
    """
    import torch

    # Enable deterministic algorithms
    torch.use_deterministic_algorithms(True, warn_only=True)

    # Disable cuDNN benchmark (non-deterministic algorithm selection)
    torch.backends.cudnn.benchmark = False

    # Force deterministic cuDNN operations
    torch.backends.cudnn.deterministic = True


class MedGemmaRunner:
    """Real MedGemma model runner for local GPU inference.

    This runner loads and executes the MedGemma model for real inference.
    It is designed for local execution only and is NOT used in CI.

    The runner:
    - Loads model lazily on first use
    - Enforces deterministic generation
    - Uses no sampling (temperature=0)
    - Tracks VRAM usage
    - Returns structured results with hash for verification

    Attributes:
        model_id: The HuggingFace model ID.
        device: The execution device (cuda/cpu).
        is_loaded: Whether the model has been loaded.

    Example:
        >>> runner = MedGemmaRunner()
        >>> result = runner.generate("Analyze this X-ray", seed=42)
        >>> print(result.text)
    """

    def __init__(
        self,
        model_id: str = MODEL_ID,
        device: str = "cuda",
        dtype: str = "float16",
    ) -> None:
        """Initialize the MedGemma runner.

        Args:
            model_id: HuggingFace model ID. Default: google/medgemma-4b
            device: Execution device. Default: cuda
            dtype: Model dtype. Default: float16 (for VRAM efficiency)

        Raises:
            RuntimeError: If real model execution is not enabled.
        """
        if not is_real_model_enabled():
            raise RuntimeError(
                f"Real model execution is disabled. "
                f"Set {REAL_MODEL_ENV_VAR}=true to enable."
            )

        self._model_id = model_id
        self._device = device
        self._dtype = dtype
        self._model = None
        self._tokenizer = None
        self._processor = None
        self._is_loaded = False

    @property
    def model_id(self) -> str:
        """The HuggingFace model ID."""
        return self._model_id

    @property
    def device(self) -> str:
        """The execution device."""
        return self._device

    @property
    def is_loaded(self) -> bool:
        """Whether the model has been loaded."""
        return self._is_loaded

    def _load_model(self) -> None:
        """Load the model and tokenizer.

        This is called lazily on first use to avoid loading the model
        if it's never needed.

        Raises:
            ImportError: If required libraries are not installed.
            RuntimeError: If model loading fails.
        """
        if self._is_loaded:
            return

        try:
            import torch
            from transformers import AutoModelForImageTextToText, AutoProcessor, AutoTokenizer
        except ImportError as e:
            raise ImportError(
                "Required libraries not installed. "
                "Install with: pip install torch transformers accelerate"
            ) from e

        # Enable deterministic mode before loading
        _enable_deterministic_mode()

        # Determine torch dtype
        if self._dtype == "float16":
            torch_dtype = torch.float16
        elif self._dtype == "bfloat16":
            torch_dtype = torch.bfloat16
        else:
            torch_dtype = torch.float32

        # Load processor (for multimodal input)
        try:
            self._processor = AutoProcessor.from_pretrained(
                self._model_id,
                trust_remote_code=True,
            )
        except Exception:
            # Fall back to tokenizer only if processor not available
            self._processor = None

        # Load tokenizer
        self._tokenizer = AutoTokenizer.from_pretrained(
            self._model_id,
            trust_remote_code=True,
        )

        # Load model (ImageTextToText for multimodal MedGemma/Gemma3)
        self._model = AutoModelForImageTextToText.from_pretrained(
            self._model_id,
            torch_dtype=torch_dtype,
            device_map="auto",  # Use auto for proper device placement
            trust_remote_code=True,
        )

        # Set model to evaluation mode (disables dropout)
        self._model.eval()

        self._is_loaded = True

    def generate(
        self,
        prompt: str,
        *,
        seed: int,
        image: "Image.Image | None" = None,
    ) -> MedGemmaResult:
        """Generate text from the model.

        Args:
            prompt: The input prompt.
            seed: Seed for reproducibility (REQUIRED).
            image: Optional input image for multimodal inference.

        Returns:
            MedGemmaResult with generated text and metadata.

        Raises:
            RuntimeError: If generation fails.
        """
        import torch

        # Load model if not already loaded
        self._load_model()

        # Set deterministic seed
        _set_deterministic_seed(seed)

        # Prepare inputs
        if image is not None and self._processor is not None:
            # Multimodal input - MedGemma/Gemma3 requires <start_of_image> token in prompt
            # The processor looks for boi_token to know where to insert image features
            boi_token = getattr(self._processor, "boi_token", "<start_of_image>")
            
            # Insert boi_token at the beginning if not already present
            if boi_token not in prompt:
                formatted_prompt = f"{boi_token}{prompt}"
            else:
                formatted_prompt = prompt
            
            inputs = self._processor(
                text=formatted_prompt,
                images=image,
                return_tensors="pt",
            ).to(self._device)
        else:
            # Text-only input
            inputs = self._tokenizer(
                prompt,
                return_tensors="pt",
            ).to(self._device)

        # Generate with deterministic settings
        with torch.no_grad():
            outputs = self._model.generate(
                **inputs,
                max_new_tokens=MAX_NEW_TOKENS,
                temperature=TEMPERATURE,
                top_p=TOP_P,
                do_sample=DO_SAMPLE,
                pad_token_id=self._tokenizer.eos_token_id,
            )

        # Decode output
        generated_text = self._tokenizer.decode(
            outputs[0],
            skip_special_tokens=True,
        )

        # Remove input prompt from output if present
        if generated_text.startswith(prompt):
            generated_text = generated_text[len(prompt):].strip()

        # Compute result hash
        bundle_sha = _compute_result_hash(generated_text, self._model_id, seed)

        # Gather metadata
        metadata = {
            "device": self._device,
            "dtype": self._dtype,
            "max_new_tokens": MAX_NEW_TOKENS,
            "temperature": TEMPERATURE,
            "top_p": TOP_P,
            "do_sample": DO_SAMPLE,
            "torch_version": torch.__version__,
        }

        try:
            import transformers
            metadata["transformers_version"] = transformers.__version__
        except Exception:
            pass

        return MedGemmaResult(
            text=generated_text,
            model_id=self._model_id,
            seed=seed,
            bundle_sha=bundle_sha,
            metadata=metadata,
        )

    def generate_rich(
        self,
        prompt: str,
        *,
        seed: int,
        image: "Image.Image | None" = None,
    ) -> RichGenerationResult:
        """Generate text with rich inference signals (M14).

        This method extends generate() to also extract:
        - Per-token log probabilities
        - Mean log probability (confidence)
        - Output entropy
        - Optional full logits hash (if CLARITY_RICH_LOGITS_HASH=true)

        Requires BOTH CLARITY_REAL_MODEL=true AND CLARITY_RICH_MODE=true.

        Args:
            prompt: The input prompt.
            seed: Seed for reproducibility (REQUIRED).
            image: Optional input image for multimodal inference.

        Returns:
            RichGenerationResult with generated text, metadata, and rich signals.

        Raises:
            RuntimeError: If rich mode is not enabled or generation fails.
        """
        import torch

        if not is_rich_mode_enabled():
            raise RuntimeError(
                "Rich mode is disabled. Set CLARITY_RICH_MODE=true to enable."
            )

        # Load model if not already loaded
        self._load_model()

        # Set deterministic seed
        _set_deterministic_seed(seed)

        # Prepare inputs
        if image is not None and self._processor is not None:
            # Multimodal input - MedGemma/Gemma3 requires <start_of_image> token
            boi_token = getattr(self._processor, "boi_token", "<start_of_image>")

            if boi_token not in prompt:
                formatted_prompt = f"{boi_token}{prompt}"
            else:
                formatted_prompt = prompt

            inputs = self._processor(
                text=formatted_prompt,
                images=image,
                return_tensors="pt",
            ).to(self._device)
        else:
            # Text-only input
            inputs = self._tokenizer(
                prompt,
                return_tensors="pt",
            ).to(self._device)

        # Generate with deterministic settings AND return logits
        with torch.no_grad():
            outputs = self._model.generate(
                **inputs,
                max_new_tokens=MAX_NEW_TOKENS,
                temperature=TEMPERATURE,
                top_p=TOP_P,
                do_sample=DO_SAMPLE,
                pad_token_id=self._tokenizer.eos_token_id,
                return_dict_in_generate=True,
                output_scores=True,  # Return logits for each position
            )

        # Extract generated token IDs (excluding input)
        input_length = inputs["input_ids"].shape[1]
        generated_ids = outputs.sequences[0, input_length:]

        # Decode output
        generated_text = self._tokenizer.decode(
            generated_ids,
            skip_special_tokens=True,
        )

        # Compute result hash (same as basic generate)
        bundle_sha = _compute_result_hash(generated_text, self._model_id, seed)

        # Extract per-token log probabilities from scores
        token_logprobs = self._extract_token_logprobs(outputs.scores, generated_ids)

        # Compute mean entropy across positions (average uncertainty)
        output_probs = self._compute_output_entropy_probs(outputs.scores)

        # Create rich summary
        rich_summary = create_rich_metrics_summary(
            token_logprobs=token_logprobs,
            output_probs=output_probs,
        )

        # Optionally compute full logits hash (streaming, no storage)
        logits_hash = None
        if is_rich_logits_hash_enabled():
            logits_hash = self._compute_logits_hash(outputs.scores)

        # Gather metadata
        metadata = {
            "device": self._device,
            "dtype": self._dtype,
            "max_new_tokens": MAX_NEW_TOKENS,
            "temperature": TEMPERATURE,
            "top_p": TOP_P,
            "do_sample": DO_SAMPLE,
            "torch_version": torch.__version__,
            "rich_mode": True,
        }

        try:
            import transformers
            metadata["transformers_version"] = transformers.__version__
        except Exception:
            pass

        return RichGenerationResult(
            text=generated_text,
            model_id=self._model_id,
            seed=seed,
            bundle_sha=bundle_sha,
            metadata=metadata,
            token_logprobs=tuple(token_logprobs) if token_logprobs else None,
            rich_summary=rich_summary,
            logits_hash=logits_hash,
        )

    def _extract_token_logprobs(
        self,
        scores: tuple[Any, ...],
        generated_ids: Any,
    ) -> list[float]:
        """Extract per-token log probabilities from generation scores.

        Args:
            scores: Tuple of logit tensors, one per generated position.
            generated_ids: The generated token IDs.

        Returns:
            List of log probabilities for each generated token.
        """
        import torch

        token_logprobs = []

        for i, (score, token_id) in enumerate(zip(scores, generated_ids)):
            # score shape: [1, vocab_size]
            # Apply log_softmax to get log probabilities
            log_probs = torch.log_softmax(score[0], dim=-1)

            # Get log prob of the actual generated token
            token_logprob = log_probs[token_id].item()
            token_logprobs.append(round(token_logprob, 8))

        return token_logprobs

    def _compute_output_entropy_probs(
        self,
        scores: tuple[Any, ...],
    ) -> list[float]:
        """Compute mean probability distribution for entropy calculation.

        We compute the mean softmax distribution across all positions,
        then use this for entropy calculation.

        Args:
            scores: Tuple of logit tensors, one per generated position.

        Returns:
            Mean probability distribution across all positions.
        """
        import torch

        if not scores:
            return []

        # Stack all scores and compute mean softmax
        # Shape: [num_positions, vocab_size]
        all_scores = torch.stack([s[0] for s in scores], dim=0)

        # Compute softmax for each position
        all_probs = torch.softmax(all_scores, dim=-1)

        # Mean across positions
        mean_probs = all_probs.mean(dim=0)

        # Convert to list
        return [round(p, 8) for p in mean_probs.tolist()]

    def _compute_logits_hash(self, scores: tuple[Any, ...]) -> str:
        """Compute hash of all logits (streaming, no storage).

        Args:
            scores: Tuple of logit tensors.

        Returns:
            SHA256 hex digest of all logits.
        """
        def logits_iterator():
            for score in scores:
                # score shape: [1, vocab_size]
                for value in score[0].flatten().tolist():
                    yield value

        return compute_logits_hash_streaming(logits_iterator())

    def get_vram_usage(self) -> dict[str, float]:
        """Get current VRAM usage statistics.

        Returns:
            Dictionary with VRAM usage in GB.
        """
        import torch

        if not torch.cuda.is_available():
            return {"allocated_gb": 0.0, "reserved_gb": 0.0, "max_allocated_gb": 0.0}

        allocated = torch.cuda.memory_allocated() / (1024**3)
        reserved = torch.cuda.memory_reserved() / (1024**3)
        max_allocated = torch.cuda.max_memory_allocated() / (1024**3)

        return {
            "allocated_gb": round(allocated, 2),
            "max_allocated_gb": round(max_allocated, 2),
            "reserved_gb": round(reserved, 2),
        }


# Convenience function for protocol compatibility
def create_medgemma_runner_result(
    text: str,
    model_id: str,
    seed: int,
) -> MedGemmaResult:
    """Create a MedGemmaResult for testing or mocking.

    Args:
        text: Generated text.
        model_id: Model identifier.
        seed: Seed used.

    Returns:
        MedGemmaResult instance.
    """
    bundle_sha = _compute_result_hash(text, model_id, seed)
    return MedGemmaResult(
        text=text,
        model_id=model_id,
        seed=seed,
        bundle_sha=bundle_sha,
        metadata={},
    )

