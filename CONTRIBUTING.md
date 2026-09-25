# Contributing

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements-dev.txt
```

## Before a pull request

```bash
ruff check .
pytest
```

Keep changes focused, add tests for behavior changes, and do not commit local databases, uploads, secrets, or editor metadata.
