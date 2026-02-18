from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter

from .config import QuickThinkConfig
from .ollama_client import OllamaClient
from .plan_grammar import is_valid_plan, normalize_plan
from .prompts import make_answer_prompt, make_plan_prompt, make_plan_repair_prompt
from .routing import should_bypass


@dataclass
class QuickThinkResult:
    answer: str
    plan: str | None
    bypassed: bool
    route_score: int
    selected_plan_budget: int
    plan_repaired: bool
    plan_latency_ms: float
    answer_latency_ms: float

    @property
    def total_latency_ms(self) -> float:
        return self.plan_latency_ms + self.answer_latency_ms


class QuickThinkEngine:
    def __init__(self, config: QuickThinkConfig) -> None:
        self.config = config
        self.client = OllamaClient(config.ollama_url)

    def run(self, prompt: str) -> QuickThinkResult:
        bypass, route_score, selected_budget = should_bypass(prompt, self.config)
        if bypass:
            start = perf_counter()
            answer_raw = self.client.generate(
                model=self.config.model,
                prompt=prompt,
                temperature=self.config.temperature,
                top_p=self.config.top_p,
                max_tokens=512,
            )
            answer_ms = (perf_counter() - start) * 1000
            return QuickThinkResult(
                answer=answer_raw.get("response", "").strip(),
                plan=None,
                bypassed=True,
                route_score=route_score,
                selected_plan_budget=selected_budget,
                plan_repaired=False,
                plan_latency_ms=0.0,
                answer_latency_ms=answer_ms,
            )

        plan_prompt = make_plan_prompt(prompt, selected_budget)
        start = perf_counter()
        plan_raw = self.client.generate(
            model=self.config.model,
            prompt=plan_prompt,
            temperature=min(self.config.temperature, 0.3),
            top_p=self.config.top_p,
            max_tokens=selected_budget,
        )
        plan_ms = (perf_counter() - start) * 1000
        plan = normalize_plan(plan_raw.get("response", ""))
        repaired = False

        if not is_valid_plan(plan, selected_budget):
            repaired = True
            repair_prompt = make_plan_repair_prompt(prompt, plan, selected_budget)
            start = perf_counter()
            repair_raw = self.client.generate(
                model=self.config.model,
                prompt=repair_prompt,
                temperature=0.1,
                top_p=self.config.top_p,
                max_tokens=selected_budget + 8,
            )
            plan_ms += (perf_counter() - start) * 1000
            repaired_plan = normalize_plan(repair_raw.get("response", ""))
            if is_valid_plan(repaired_plan, selected_budget):
                plan = repaired_plan
            else:
                plan = f"g:solve;c:constraints;s:direct_reasoning;r:verify_output"

        answer_prompt = make_answer_prompt(prompt, plan)
        start = perf_counter()
        answer_raw = self.client.generate(
            model=self.config.model,
            prompt=answer_prompt,
            temperature=self.config.temperature,
            top_p=self.config.top_p,
            max_tokens=768,
        )
        answer_ms = (perf_counter() - start) * 1000

        return QuickThinkResult(
            answer=answer_raw.get("response", "").strip(),
            plan=plan,
            bypassed=False,
            route_score=route_score,
            selected_plan_budget=selected_budget,
            plan_repaired=repaired,
            plan_latency_ms=plan_ms,
            answer_latency_ms=answer_ms,
        )
