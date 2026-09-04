"""A small, instrumented ReAct-style execution loop."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Callable, Literal, Protocol

from .contracts import FinalOutcome, ModelTurn, RunResult, ToolAction, TraceEvent


class Backend(Protocol):
    def next_turn(self, transcript: list[dict[str, object]]) -> ModelTurn:
        """Return the next scripted or model-generated turn."""


ToolExecutor = Callable[[ToolAction], dict[str, object]]
BatchValidator = Callable[[tuple[ToolAction, ...]], None]


@dataclass(frozen=True)
class RunnerConfig:
    step_cap: int = 8
    input_price_per_million: float = 3.0
    output_price_per_million: float = 15.0
    execution_mode: Literal["sequential", "parallel"] = "sequential"
    max_parallel_workers: int = 4


class ReActRunner:
    """Execute tool turns and retain a compact, inspectable trace."""

    def __init__(self, backend: Backend, tool_executor: ToolExecutor,
                 config: RunnerConfig | None = None,
                 batch_validator: BatchValidator | None = None) -> None:
        self.backend = backend
        self.tool_executor = tool_executor
        self.config = config or RunnerConfig()
        self.batch_validator = batch_validator

    def _execute_actions(self, actions: tuple[ToolAction, ...]) -> list[tuple[ToolAction, dict[str, object]]]:
        if self.batch_validator is not None:
            self.batch_validator(actions)
        if self.config.execution_mode == "parallel" and len(actions) > 1:
            with ThreadPoolExecutor(max_workers=min(self.config.max_parallel_workers, len(actions))) as executor:
                observations = list(executor.map(self.tool_executor, actions))
            return list(zip(actions, observations, strict=True))
        return [(action, self.tool_executor(action)) for action in actions]

    def run(self, case_id: str, initial_context: dict[str, object] | None = None) -> RunResult:
        transcript: list[dict[str, object]] = [{"role": "user", "content": initial_context or {}}]
        trace: list[TraceEvent] = []
        total_input_tokens = total_output_tokens = 0
        for turn_number in range(1, self.config.step_cap + 1):
            model_turn = self.backend.next_turn(transcript)
            total_input_tokens += model_turn.input_tokens
            total_output_tokens += model_turn.output_tokens
            for action, observation in self._execute_actions(model_turn.actions):
                trace.append(TraceEvent(turn=turn_number, action=action, observation=observation))
                transcript.append({"role": "tool", "name": action.name, "content": observation})
            if model_turn.final is not None:
                return self._result(case_id, model_turn.final, turn_number, trace, total_input_tokens, total_output_tokens, False)
        cap_outcome = FinalOutcome(decision="escalate", reason="Step cap reached before a safe final decision.", evidence=(), autonomy="review_required", gate="step_cap")
        return self._result(case_id, cap_outcome, self.config.step_cap, trace, total_input_tokens, total_output_tokens, True)

    def _result(self, case_id: str, outcome: FinalOutcome, turns: int, trace: list[TraceEvent], input_tokens: int, output_tokens: int, cap_fired: bool) -> RunResult:
        cost = input_tokens / 1_000_000 * self.config.input_price_per_million + output_tokens / 1_000_000 * self.config.output_price_per_million
        return RunResult(case_id=case_id, outcome=outcome, turns=turns, trace=tuple(trace), input_tokens=input_tokens, output_tokens=output_tokens, estimated_cost_usd=cost, cap_fired=cap_fired)
