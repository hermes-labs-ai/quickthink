from __future__ import annotations

import re

from .config import QuickThinkConfig

_MULTI_STEP_RE = re.compile(r"\b(plan|design|debug|strategy|step[- ]by[- ]step|architecture)\b", re.IGNORECASE)
_COMPARISON_RE = re.compile(r"\b(compare|versus|vs\.?|tradeoff|pros and cons)\b", re.IGNORECASE)
_STRUCTURED_RE = re.compile(r"\b(json|table|schema|bullet|list|format)\b", re.IGNORECASE)
_AMBIGUITY_RE = re.compile(r"\b(best|optimize|could|should|maybe|might)\b", re.IGNORECASE)
_STRICT_FORMAT_RE = re.compile(
    r"\b(json only|yaml only|csv only|xml|exactly|lowercase only|yes or no only|no punctuation|line 1:|line 2:)\b",
    re.IGNORECASE,
)


def complexity_score(prompt: str) -> int:
    score = 0
    stripped = prompt.strip()

    if len(stripped) > 140:
        score += 1
    if _COMPARISON_RE.search(stripped):
        score += 1
    if _MULTI_STEP_RE.search(stripped):
        score += 1
    if _STRUCTURED_RE.search(stripped):
        score += 1
    if _AMBIGUITY_RE.search(stripped):
        score += 1

    return score


def choose_plan_budget(score: int, config: QuickThinkConfig) -> int:
    if score <= 1:
        return config.min_plan_budget_tokens
    if score <= 3:
        return min(max(12, config.min_plan_budget_tokens), config.max_plan_budget_tokens)
    return config.max_plan_budget_tokens


def should_bypass(prompt: str, config: QuickThinkConfig) -> tuple[bool, int, int]:
    stripped = prompt.strip()
    score = complexity_score(stripped)

    if config.bypass_short_prompts and len(stripped) <= config.bypass_char_threshold:
        return True, score, config.min_plan_budget_tokens

    if config.adaptive_routing and score <= config.route_skip_score_threshold:
        return True, score, config.min_plan_budget_tokens

    if config.adaptive_routing:
        return False, score, choose_plan_budget(score, config)

    return False, score, config.plan_budget_tokens


def infer_task_class(prompt: str) -> str:
    stripped = prompt.strip()
    if _STRICT_FORMAT_RE.search(stripped):
        return "strict_format"
    if _MULTI_STEP_RE.search(stripped) or _COMPARISON_RE.search(stripped):
        return "reasoning"
    return "general"
