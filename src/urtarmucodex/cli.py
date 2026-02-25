from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List

from .yaml_loader import SimpleYAMLError, load_yaml_file

REQUIRED_FIELDS = ("id", "name", "rarity", "type", "description")


@dataclass
class ValidationResult:
    path: Path
    missing_fields: List[str]
    errors: List[str]

    @property
    def ok(self) -> bool:
        return not self.missing_fields and not self.errors


def find_card_files(root: Path) -> List[Path]:
    cards_dir = root / "data" / "cards"
    return sorted(cards_dir.glob("*.yaml")) if cards_dir.exists() else []


def validate_card(path: Path, required_fields: Iterable[str]) -> ValidationResult:
    missing_fields: List[str] = []
    errors: List[str] = []

    try:
        data = load_yaml_file(path)
    except SimpleYAMLError as exc:
        errors.append(f"YAML error: {exc}")
        return ValidationResult(path=path, missing_fields=missing_fields, errors=errors)

    if not isinstance(data, dict):
        errors.append(f"Expected mapping at document root, found {type(data).__name__}")
        return ValidationResult(path=path, missing_fields=missing_fields, errors=errors)

    for field in required_fields:
        value = data.get(field)
        if value is None:
            missing_fields.append(field)
        elif isinstance(value, str) and not value.strip():
            missing_fields.append(field)

    return ValidationResult(path=path, missing_fields=missing_fields, errors=errors)


def build_report(
    results: List[ValidationResult],
    report_path: Path,
    root: Path,
    general_notes: List[str],
) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)

    total = len(results)
    passed = sum(1 for r in results if r.ok)
    failed = total - passed

    lines: List[str] = [
        "# Validation Report",
        "",
        f"Generated at: {datetime.now(tz=timezone.utc).isoformat()}",
        f"Project root: {root}",
        "",
        "## Summary",
        "",
        f"- Total files: {total}",
        f"- Passed: {passed}",
        f"- Failed: {failed}",
    ]

    if general_notes:
        lines.extend(["", "## Notes", ""])
        lines.extend(f"- {note}" for note in general_notes)

    if results:
        lines.extend(["", "## File Results", "", "| File | Status | Details |", "| --- | --- | --- |"])
        for result in results:
            status = "✅ Passed" if result.ok else "❌ Failed"
            details: List[str] = []
            if result.errors:
                details.extend(f"Error: {error}" for error in result.errors)
            if result.missing_fields:
                details.append(
                    "Missing fields: " + ", ".join(sorted(result.missing_fields))
                )
            detail_text = "<br />".join(details) if details else ""
            relative_path = result.path.relative_to(root)
            lines.append(f"| `{relative_path}` | {status} | {detail_text} |")
    else:
        lines.extend(["", "## File Results", "", "No card files were found."])

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_validate(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    report_path = Path(args.output).resolve() if args.output else root / "reports" / "validate_report.md"

    general_notes: List[str] = []
    card_files = find_card_files(root)
    if not card_files:
        general_notes.append("No card files were found in data/cards.")

    results = [validate_card(path, REQUIRED_FIELDS) for path in card_files]

    build_report(results=results, report_path=report_path, root=root, general_notes=general_notes)

    success = bool(card_files) and all(result.ok for result in results)
    if success:
        print(f"Validation succeeded. Report written to {report_path}")
        return 0

    print(f"Validation failed. See report at {report_path}")
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Urtarmu Codex utility CLI.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate card YAML files and write a report.",
    )
    validate_parser.add_argument(
        "--root",
        default=Path.cwd(),
        type=Path,
        help="Project root containing data/cards and reports directories.",
    )
    validate_parser.add_argument(
        "--output",
        type=Path,
        help="Optional custom path for the validation report.",
    )
    validate_parser.set_defaults(func=run_validate)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
