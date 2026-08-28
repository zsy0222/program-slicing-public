"""SWP (Slicing Workflow Paradigm) — structured reasoning prompts for LLM-based program slicing."""

from .templates import (
    SWPTemplate,
    build_slice_prompt,
    SLICE_TYPE_BACKWARD,
    SLICE_TYPE_FORWARD,
    SLICE_TYPE_CHOP,
)

__all__ = [
    "SWPTemplate",
    "build_slice_prompt",
    "SLICE_TYPE_BACKWARD",
    "SLICE_TYPE_FORWARD",
    "SLICE_TYPE_CHOP",
]
