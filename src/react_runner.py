"""A small, instrumented single-agent ReAct loop for D1."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Protocol

from .contracts import FinalOutcome, ModelTurn, RunResult, ToolAction, TraceEvent


class Backend(Protocol):
    def next_turn(self, transcript: list[dict[str, object]]) -> ModelTurn: ...


ToolExecutor = Callable[[ToolAction], dict[str, Any]]


@dataclass(frozen=True)
class RunnerConfig:
    step_cap: int = 8
    input_price_per_million: float = 0.10
    output_price_per_million: float = 0.40


class ReActRunner:
    """Runs one model-controlled loop and records every observation."""

    def __init__(
        self,
        backend: Backend,
        execute_tool: ToolExecutor,
        config: RunnerConfig | None = None,
    ) -> None:
        self.backend = backend
        self.execute_tool = execute_tool
        self.config = config or RunnerConfig()

    def run(self, case_id: str) -> RunResult:
        transcript: list[dict[str, object]] = [{"role": "user", "case_id": case_id}]
        trace: list[TraceEvent] = []
        input_tokens = 0
        output_tokens = 0

        for turn_number in range(1, self.config.step_cap + 1):
            model_turn = self.backend.next_turn(transcript)
            input_tokens += model_turn.input_tokens
            output_tokens += model_turn.output_tokens

            for action in model_turn.actions:
                observation = self.execute_tool(action)
                trace.append(TraceEvent(turn_number, action, observation))
                transcript.append(
                    {
                        "role": "tool",
                        "turn": turn_number,
                        "tool": action.name,
                        "observation": observation,
                    }
                )

            if model_turn.final is not None:
                return self._result(
                    case_id,
                    model_turn.final,
                    turn_number,
                    trace,
                    input_tokens,
                    output_tokens,
                    cap_fired=False,
                )

        capped_outcome = FinalOutcome(
            decision="escalate",
            reason="Step cap reached before a supported final outcome.",
            evidence=[event.action.name for event in trace],
            autonomy="suggest",
            gate="not reached: step cap fired",
        )
        return self._result(
            case_id,
            capped_outcome,
            self.config.step_cap,
            trace,
            input_tokens,
            output_tokens,
            cap_fired=True,
        )

    def _result(
        self,
        case_id: str,
        outcome: FinalOutcome,
        turns: int,
        trace: list[TraceEvent],
        input_tokens: int,
        output_tokens: int,
        cap_fired: bool,
    ) -> RunResult:
        estimated_cost_usd = (
            input_tokens * self.config.input_price_per_million
            + output_tokens * self.config.output_price_per_million
        ) / 1_000_000
        return RunResult(
            case_id=case_id,
            outcome=outcome,
            turns=turns,
            trace=trace,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            estimated_cost_usd=estimated_cost_usd,
            cap_fired=cap_fired,
        )
