from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter

from .config import QuickThinkConfig
from .inline_protocol import extract_plan_and_answer
from .ollama_client import OllamaClient
from .plan_grammar import is_valid_plan, normalize_plan
from .prompts import (
    make_answer_prompt,
    make_inline_plan_answer_prompt,
    make_plan_prompt,
    make_plan_repair_prompt,
)
from .routing import infer_task_class, should_bypass


@dataclass
class QuickThinkResult:
    answer: str
    plan: str | None
    mode: str
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
        self.client = OllamaClient(config.ollama_url, timeout_s=config.request_timeout_s)

    def run(self, prompt: str) -> QuickThinkResult:
        if self.config.lane_policy == "strict_safe" and infer_task_class(prompt) == "strict_format":
            return self._run_direct(prompt=prompt, route_score=-1, selected_budget=self.config.min_plan_budget_tokens)

        bypass, route_score, selected_budget = should_bypass(prompt, self.config)
        if bypass:
            return self._run_direct(prompt=prompt, route_score=route_score, selected_budget=selected_budget)

        if self.config.mode == "two_pass":
            return self._run_two_pass(prompt, route_score, selected_budget)
        if self.config.mode == "direct":
            return self._run_direct(prompt=prompt, route_score=route_score, selected_budget=selected_budget)
        return self._run_lite(prompt, route_score, selected_budget)

    def _run_direct(self, prompt: str, route_score: int, selected_budget: int) -> QuickThinkResult:
        start = perf_counter()
        answer_raw = self.client.generate(
            model=self.config.model,
            prompt=prompt,
            temperature=self.config.temperature,
            top_p=self.config.top_p,
            max_tokens=512,
            think=self.config.think,
        )
        answer_ms = (perf_counter() - start) * 1000
        return QuickThinkResult(
            answer=answer_raw.get("response", "").strip(),
            plan=None,
            mode=self.config.mode,
            bypassed=True,
            route_score=route_score,
            selected_plan_budget=selected_budget,
            plan_repaired=False,
            plan_latency_ms=0.0,
            answer_latency_ms=answer_ms,
        )

    def _run_lite(self, prompt: str, route_score: int, selected_budget: int) -> QuickThinkResult:
        inline_prompt = make_inline_plan_answer_prompt(
            prompt,
            selected_budget,
            continuity_hint=self.config.continuity_hint,
            scaffold_rules=self.config.scaffold_rules,
        )
        start = perf_counter()
        raw = self.client.generate(
            model=self.config.model,
            prompt=inline_prompt,
            temperature=self.config.temperature,
            top_p=self.config.top_p,
            max_tokens=768,
            think=self.config.think,
        )
        answer_ms = (perf_counter() - start) * 1000

        raw_text = raw.get("response", "")
        plan, answer = extract_plan_and_answer(raw_text)
        repaired = False

        if plan and not is_valid_plan(plan, selected_budget):
            repaired = True
            plan = f"g:solve;c:constraints;s:direct_reasoning;r:verify_output"
        if plan is None:
            repaired = True

        return QuickThinkResult(
            answer=answer.strip(),
            plan=plan,
            mode="lite",
            bypassed=False,
            route_score=route_score,
            selected_plan_budget=selected_budget,
            plan_repaired=repaired,
            plan_latency_ms=0.0,
            answer_latency_ms=answer_ms,
        )

    def _run_two_pass(self, prompt: str, route_score: int, selected_budget: int) -> QuickThinkResult:
        plan_prompt = make_plan_prompt(prompt, selected_budget)
        start = perf_counter()
        plan_raw = self.client.generate(
            model=self.config.model,
            prompt=plan_prompt,
            temperature=min(self.config.temperature, 0.3),
            top_p=self.config.top_p,
            max_tokens=selected_budget,
            think=self.config.think,
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
                think=self.config.think,
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
            think=self.config.think,
        )
        answer_ms = (perf_counter() - start) * 1000

        return QuickThinkResult(
            answer=answer_raw.get("response", "").strip(),
            plan=plan,
            mode="two_pass",
            bypassed=False,
            route_score=route_score,
            selected_plan_budget=selected_budget,
            plan_repaired=repaired,
            plan_latency_ms=plan_ms,
            answer_latency_ms=answer_ms,
        )
