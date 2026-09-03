"""Offline deterministic model backends for D1."""

from __future__ import annotations

from dataclasses import dataclass

from .contracts import ModelTurn


@dataclass
class ScriptedBackend:
    """Returns canned model turns in order, with no network or API key."""

    turns: list[ModelTurn]
    _cursor: int = 0

    def next_turn(self, transcript: list[dict[str, object]]) -> ModelTurn:
        del transcript  # The scenario, not a live model, controls this backend.
        if self._cursor >= len(self.turns):
            raise RuntimeError("Scripted backend exhausted before a final outcome.")
        turn = self.turns[self._cursor]
        self._cursor += 1
        return turn
