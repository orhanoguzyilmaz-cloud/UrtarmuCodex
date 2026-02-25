# UrtarmuCodex

The Tale of Two Wings - Urtarmu Codex

## Installation

Install the package in editable mode so the `urtarmucodex` command becomes available:

```bash
python -m pip install -e .
```

If your environment restricts build isolation or external downloads, use:

```bash
python -m pip install --no-build-isolation -e .
```

When installation is not possible, you can still run the CLI directly from the repository with `PYTHONPATH=src python -m urtarmucodex.cli ...`.

## Validation command

Validate all card definitions under `data/cards/*.yaml` and produce a Markdown report:

```bash
urtarmucodex validate --root .
```

- Report location: `reports/validate_report.md` by default (customize with `--output <path>`).
- Required fields in each card file: `id`, `name`, `rarity`, `type`, and `description`.
- Exit codes: `0` when all cards pass validation, `1` if any required field is missing or a file cannot be read/parsed.

A sample card is provided in `data/cards/dawnfeather_guardian.yaml` as a reference format.
