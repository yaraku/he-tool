# Testing and Quality Tooling

The backend ships with a comprehensive pytest suite, coverage reporting, and strict static typing via mypy. This document describes how to run the tooling, how the fixtures work, and what quality gates the project enforces.

## Pytest configuration

- `pytest.ini` options live in `backend/pyproject.toml` under `[tool.pytest.ini_options]` and set `pythonpath=src`, `testpaths=tests`, and `-ra` for extra failure info.
- `tests/conftest.py` initialises a Flask application with:
  - `TESTING=True`
  - An in-memory SQLite database (`sqlite://`) using `StaticPool` and `check_same_thread=False`
  - `JWT_COOKIE_CSRF_PROTECT=False` to simplify cookie handling in tests
- The autouse fixture drops/creates all tables before every test, ensuring isolation. Factory fixtures build `User`, `System`, `Document`, `Bitext`, `Evaluation`, `Annotation`, `AnnotationSystem`, and `Marking` objects with deterministic timestamps.
- `auth_client` authenticates a user once per test by hitting `/api/auth/login` and returning a cookie-enabled client.

Run the suite with:

```bash
poetry run pytest
```

## Coverage expectations

Coverage is measured with `coverage[toml]` (configured in `pyproject.toml`).

```bash
poetry run coverage run -m pytest
poetry run coverage report
```

The goal is ≥99 % line coverage (the current suite hits 100 %). Branch coverage is enabled to surface unexecuted conditional logic.

## Static typing with mypy

The project requires `mypy --strict` to pass. Configuration highlights:

```toml
[tool.mypy]
python_version = "3.10"
strict = true
allow_redefinition = true
disallow_untyped_calls = false
follow_imports = "silent"
ignore_missing_imports = true
implicit_reexport = true
```

- Application code is fully typed, including route functions returning `ResponseReturnValue` and SQLAlchemy models using the 2.0-style `Mapped[...]` annotations.
- A typed wrapper around `jwt_required` in `auth.py` keeps authentication endpoints type-safe.

Run mypy with:

```bash
poetry run mypy src tests
```

## Linting and formatting

While not part of this task, Poetry declares `black` and `flake8` as dev dependencies. They can be run via:

```bash
poetry run black src tests
poetry run flake8 src tests
```

## Developer workflow checklist

1. Implement feature/fix with tests.
2. Run `poetry run pytest`.
3. Run `poetry run coverage report` and ensure coverage has not regressed below 99 %.
4. Run `poetry run mypy src tests` to confirm strict typing.
5. Update documentation when behaviour or APIs change.
