from __future__ import annotations

from dataclasses import dataclass


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
