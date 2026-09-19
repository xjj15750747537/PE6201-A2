"""Portable entry point for the D3(b) ten-case guardrail checklist."""

import runpy
from pathlib import Path


if __name__ == "__main__":
    runpy.run_path(
        str(Path(__file__).with_name("d3(b)_guardrail_checklist.py")),
        run_name="__main__",
    )
