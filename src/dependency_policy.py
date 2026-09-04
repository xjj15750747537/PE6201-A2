"""Explicit batching policy for the D2(c) multi-tool ReAct demonstration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .contracts import ToolAction


class DependencyViolation(ValueError):
    """Raised when a proposed parallel tool batch violates the documented policy."""


@dataclass(frozen=True)
class DependencyPolicy:
    """Allow only independent read-only checks to share a model turn."""

    context_tool: str = "get_referral_context"
    appointment_tool: str = "get_existing_appointments"
    slot_tool: str = "find_eligible_slots"
    staging_tool: str = "stage_booking_intent"

    def validate_batch(self, actions: Iterable[ToolAction]) -> None:
        names = tuple(action.name for action in actions)
        if len(names) <= 1:
            return
        if len(set(names)) != len(names):
            raise DependencyViolation("A tool may appear at most once in a batch.")
        if set(names) == {self.appointment_tool, self.slot_tool} and len(names) == 2:
            return
        if self.context_tool in names:
            raise DependencyViolation("get_referral_context establishes state and must run alone.")
        if self.staging_tool in names:
            raise DependencyViolation("stage_booking_intent is gated and must run alone.")
        raise DependencyViolation("Only get_existing_appointments and find_eligible_slots may run in parallel.")
