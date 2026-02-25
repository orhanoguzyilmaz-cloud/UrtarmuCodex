"""Minimal YAML reader tailored for simple key-value card definitions."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


class SimpleYAMLError(ValueError):
    """Raised when the YAML content cannot be parsed."""


def _coerce_value(text: str) -> Any:
    stripped = text.strip()
    if stripped in {"''", '""'}:
        return ""
    if stripped.lower() in {"true", "false"}:
        return stripped.lower() == "true"
    for converter in (int, float):
        try:
            return converter(stripped)
        except ValueError:
            pass
    if (stripped.startswith("\"") and stripped.endswith("\"")) or (
        stripped.startswith("'") and stripped.endswith("'")
    ):
        return stripped[1:-1]
    return stripped


def parse_simple_yaml(text: str) -> Dict[str, Any]:
    data: Dict[str, Any] = {}
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" not in stripped:
            raise SimpleYAMLError(f"Line {line_number}: expected 'key: value' pair")
        key, value = stripped.split(":", 1)
        key = key.strip()
        if not key:
            raise SimpleYAMLError(f"Line {line_number}: missing key before colon")
        data[key] = _coerce_value(value)
    return data


def load_yaml_file(path: Path) -> Dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SimpleYAMLError(f"Unable to read file: {exc}") from exc

    try:
        return parse_simple_yaml(text)
    except SimpleYAMLError:
        raise
    except Exception as exc:  # pragma: no cover - defensive against unforeseen errors
        raise SimpleYAMLError(str(exc)) from exc
