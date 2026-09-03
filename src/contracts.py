"""Structured contracts shared by the D1 ReAct runner."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

Decision = Literal["book", "request_information", "escalate"]


@dataclass(frozen=True)
class ToolAction:
    name: str
    arguments: dict[str, Any]


@dataclass(frozen=True)
class FinalOutcome:
    decision: Decision
    reason: str
    evidence: list[str] = field(default_factory=list)
    autonomy: Literal["suggest", "confirm", "act"] = "suggest"
    gate: str = "not reached"


@dataclass(frozen=True)
class ModelTurn:
    actions: tuple[ToolAction, ...] = ()
    final: FinalOutcome | None = None
    input_tokens: int = 0
    output_tokens: int = 0


@dataclass
class TraceEvent:
    turn: int
    action: ToolAction
    observation: dict[str, Any]


@dataclass
class RunResult:
    case_id: str
    outcome: FinalOutcome
    turns: int
    trace: list[TraceEvent]
    input_tokens: int
    output_tokens: int
    estimated_cost_usd: float
    cap_fired: bool
