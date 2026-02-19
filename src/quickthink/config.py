from __future__ import annotations

from dataclasses import dataclass


SUPPORTED_MODELS = ("qwen2.5:1.5b", "mistral:7b", "gemma3:27b")

MODEL_PROFILES = {
    "qwen2.5:1.5b": {
        "plan_budget_tokens": 8,
        "min_plan_budget_tokens": 6,
        "max_plan_budget_tokens": 12,
        "temperature": 0.3,
        "top_p": 0.9,
    },
    "mistral:7b": {
        "plan_budget_tokens": 10,
        "min_plan_budget_tokens": 8,
        "max_plan_budget_tokens": 16,
        "temperature": 0.25,
        "top_p": 0.9,
    },
    "gemma3:27b": {
        "plan_budget_tokens": 8,
        "min_plan_budget_tokens": 6,
        "max_plan_budget_tokens": 14,
        "temperature": 0.2,
        "top_p": 0.85,
    },
}

PRESET_PROFILES = {
    "fast": {
        "min_plan_budget_tokens": 4,
        "max_plan_budget_tokens": 8,
        "route_skip_score_threshold": 2,
        "bypass_char_threshold": 180,
        "temperature": 0.2,
        "top_p": 0.85,
    },
    "balanced": {
        "min_plan_budget_tokens": 6,
        "max_plan_budget_tokens": 12,
        "route_skip_score_threshold": 1,
        "bypass_char_threshold": 120,
        "temperature": 0.3,
        "top_p": 0.9,
    },
    "strict": {
        "min_plan_budget_tokens": 8,
        "max_plan_budget_tokens": 16,
        "route_skip_score_threshold": 0,
        "bypass_char_threshold": 80,
        "temperature": 0.15,
        "top_p": 0.8,
    },
}


@dataclass
class QuickThinkConfig:
    model: str = "qwen2.5:1.5b"
    ollama_url: str = "http://localhost:11434"
    plan_budget_tokens: int = 8
    min_plan_budget_tokens: int = 6
    max_plan_budget_tokens: int = 12
    temperature: float = 0.3
    top_p: float = 0.9
    bypass_short_prompts: bool = True
    bypass_char_threshold: int = 120
    adaptive_routing: bool = True
    route_skip_score_threshold: int = 1
    mode: str = "lite"
    continuity_hint: str | None = None
    preset: str = "balanced"
    request_timeout_s: float = 180.0
    think: bool | str | None = None
    scaffold_rules: str | None = None

    @classmethod
    def with_model_profile(cls, model: str, ollama_url: str = "http://localhost:11434") -> "QuickThinkConfig":
        profile = MODEL_PROFILES.get(model, {})
        return cls(
            model=model,
            ollama_url=ollama_url,
            plan_budget_tokens=profile.get("plan_budget_tokens", 8),
            min_plan_budget_tokens=profile.get("min_plan_budget_tokens", 6),
            max_plan_budget_tokens=profile.get("max_plan_budget_tokens", 12),
            temperature=profile.get("temperature", 0.3),
            top_p=profile.get("top_p", 0.9),
        )

    def apply_preset(self, preset: str) -> None:
        profile = PRESET_PROFILES.get(preset)
        if not profile:
            raise ValueError(f"Unknown preset '{preset}'")
        self.preset = preset
        self.min_plan_budget_tokens = int(profile["min_plan_budget_tokens"])
        self.max_plan_budget_tokens = int(profile["max_plan_budget_tokens"])
        self.route_skip_score_threshold = int(profile["route_skip_score_threshold"])
        self.bypass_char_threshold = int(profile["bypass_char_threshold"])
        self.temperature = float(profile["temperature"])
        self.top_p = float(profile["top_p"])
