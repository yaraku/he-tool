Proposed by: **ChatGPT**
  
Proposed on: **2025-10-01**

# Overview

This RFC proposes a comprehensive quality initiative for the Human Evaluation Tool backend. The workstream covers (1) deep reverse-engineering of the current Flask/SQLAlchemy API surface, (2) creation of authoritative documentation—including rich Mermaid diagrams—that explains the domain model and request flow, (3) introduction of exhaustive automated tests with near-100 % coverage using pytest and coverage.py, and (4) adoption of mypy in strict mode (with a focused configuration) alongside any type hinting or refactors required to obtain a clean static-typing bill of health.

# Background

The backend currently exposes a sizable REST API layer across eight resource modules plus authentication, driven by SQLAlchemy ORM models. However:

* There is minimal documentation: `backend/README.md` is skeletal and `docs/backend/` is empty.
* There are no automated tests, leaving behaviour (especially the numerous error paths in the resources) unverified.
* Static typing is absent, and mypy is not part of the toolchain.
* The Flask application is instantiated at import time with a hard-coded PostgreSQL connection string assembled from environment variables, which makes automated verification complicated.

Improving maintainability requires authoritative docs, regression coverage, and type safety.

# The What

The initiative is broken down into the following deliverables:

1. **Documentation**
   * Populate `backend/README.md` with an in-depth explanation of the application architecture, configuration, dependency graph, and development workflows.
   * Create a new `docs/backend/` knowledge base with:
     * An overview document describing runtime architecture, configuration layers, deployment assumptions, and local development instructions.
     * Domain documentation with Mermaid-based ER diagram for the SQLAlchemy models and relationship multiplicities.
     * API lifecycle documentation with Mermaid sequence diagrams for critical flows (login/auth cookie refresh, CRUD for a resource such as annotations, evaluation results generation).
     * If helpful, a class diagram summarising model relationships (Mermaid classDiagram) and a component diagram showing module structure.
     * Pointers to testing/type-checking workflows (pytest, coverage, mypy).

2. **Testing & Coverage**
   * Adopt `pytest` as the orchestrator and add `coverage[toml]` for measurement.
   * Introduce a testing harness that spins up the Flask app with an in-memory SQLite database (using SQLAlchemy’s `create_all` / `drop_all`) so that the ORM layer can be exercised without external dependencies.
   * Build fixtures for:
     * Application/test client (with JWT manager configured for tests).
     * Database session and factory helpers for Users, Systems, Documents, Bitexts, Evaluations, Annotations, AnnotationSystems, and Markings.
   * Write tests for every endpoint and helper covering:
     * `human_evaluation_tool.__init__`: index route and JWT refresh hook behaviour.
     * `auth` routes: login success/failure, logout, validate, refresh logic (forcing near-expiration tokens).
     * CRUD operations for each resource module (users, systems, documents, bitexts, annotations, annotation systems, markings, evaluations) covering success paths, validation errors (missing fields, conflicts, invalid IDs), authorisation enforcement, and not-found branches.
     * Utility constants usage via evaluation results route, ensuring category/severity mappings behave as expected.
     * Edge cases like deletion responses, 204 empty JSON bodies, and error rollbacks.
   * Target line coverage ≥99 % (100 % where feasible) as reported by `coverage`.

3. **Static Typing**
   * Add `mypy` as a dev dependency and configure it in `pyproject.toml` under a `[tool.mypy]` section with the provided options, plus `strict = true`.
   * Gradually type-annotate modules to satisfy strict typing:
     * Provide return types for Flask route functions (`tuple[Response, int]`/`ResponseReturnValue` etc.), using `flask.typing.ResponseReturnValue` for compatibility.
     * Annotate helper functions (`to_dict`) and constants (`dict[str, str]`).
     * Use `typing.cast` for SQLAlchemy query results where necessary, and guard query `.get` results with explicit `Optional` handling.
     * Where SQLAlchemy dynamic attributes confuse mypy, introduce `typing.TYPE_CHECKING` blocks with declarative attribute definitions, or leverage SQLAlchemy 2.0 style `Mapped[]` annotations if the refactor is manageable without altering runtime behaviour.
     * Add minimal helper abstractions (e.g., `get_object_or_404` wrappers) if they simplify both typing and reuse.
   * Ensure `mypy --strict` passes against the backend package and tests (if practical) without suppressions beyond targeted `# type: ignore[... ]` justified in comments.

4. **Project Tooling Updates**
   * Update `pyproject.toml` to register new dev dependencies (`pytest`, `coverage`, `pytest-cov` if used, `mypy`) and configure pytest/coverage (e.g., `[tool.pytest.ini_options]`, `[tool.coverage.run]` sections).
   * Update `backend/poetry.lock` to remain consistent.
   * Provide `Makefile`/task runner snippets if existing workflows need augmentation (only if necessary to simplify commands).

# The How

Implementation will proceed in stages:

1. **Codebase Recon & App Factory Extraction**
   * Refactor `human_evaluation_tool.__init__` into an application factory pattern (`create_app(config_override: Optional[dict[str, Any]] = None)`) to decouple environment-specific configuration from import side effects. Maintain backward compatibility by instantiating a default app for production usage. Ensure CLI entry points (`backend/main.py`) still work by importing the default app.
   * Add configurability for SQLAlchemy URI and testing mode (e.g., accept `SQLALCHEMY_DATABASE_URI` from environment or override) so tests can use SQLite.

2. **Testing Infrastructure**
   * Create `tests/backend/conftest.py` with fixtures for application, client, and database setup/teardown (ensuring tables are dropped between tests to avoid leakage).
   * Use `flask_jwt_extended` utilities within fixtures to issue tokens and attach cookies for authenticated requests.
   * Implement data factory helpers (simple functions instead of extra libraries unless growth demands `factory_boy`).
   * Write parameterised tests verifying positive and negative paths for each endpoint and method; use `pytest.mark.parametrize` to cover multiple invalid inputs per handler.
   * Run `coverage run -m pytest` to iterate towards full coverage; plug holes by identifying unexecuted lines and augmenting tests accordingly.

3. **Static Typing Pass**
   * After tests stabilise, layer in annotations module-by-module, running `mypy --strict` to detect issues. Address them via:
     * Explicit type hints (`dict[str, typing.Any]`) on `to_dict` results.
     * Narrowing query returns with early `if obj is None` checks.
     * Introducing dataclasses or TypedDicts for JSON payloads if beneficial.
   * Update imports to bring in typing utilities; avoid try/except around imports per style guideline.

4. **Documentation Authoring**
   * Compose `backend/README.md` describing environment setup, configuration injection, development/test/type-check commands, architecture summary, and diagram references.
   * Under `docs/backend/`, add:
     * `architecture.md` (component view + Mermaid diagrams).
     * `domain-model.md` (ER + class diagrams; explanation of relationships and invariants).
     * `api-flows.md` (sequence diagrams for login, annotation CRUD, evaluation results export).
     * `testing-and-quality.md` (instructions for pytest/coverage/mypy usage and expected coverage gate).
     * Additional files if clarity demands (e.g., `configuration.md`).
   * Ensure docs reference real commands and include instructions for running tests with SQLite test DB, migrating Postgres for prod, etc.

5. **Verification & Tooling**
   * Run `pytest`, `coverage report`, and `mypy --strict` in CI/local to confirm green status.
   * Optionally capture coverage XML/HTML outputs if repository conventions expect them (will confirm before adding extra artefacts).

6. **Final Polish**
   * Ensure new docs/fixtures adhere to repository style (no `try/except` around imports, black-compatible formatting).
   * Update `.gitignore` if coverage/mypy caches introduce new artefacts (e.g., `.coverage`, `.mypy_cache`).

# The Why

* **Reliability**: Regression tests and strict typing dramatically reduce the risk of silent breakages in a critical evaluation workflow.
* **Onboarding**: Rich documentation (with diagrams) makes it far easier for new contributors to understand the data model and API flows.
* **Maintainability**: App factory refactor + typed code fosters cleaner dependency injection, enabling future features (e.g., new storage backends) without friction.
* **Quality Gates**: Institutionalising pytest/coverage/mypy establishes quality bars for future contributions.

# The Benefits

* Drastically improved test coverage and confidence in CRUD/auth flows.
* Clear, navigable documentation for engineers, QA, and stakeholders.
* Enforced static typing prevents classes of runtime errors and clarifies API contracts.
* More flexible configuration enabling hermetic tests and easier local setup.

# The Concerns

* **Refactor Risk**: Extracting an app factory touches core initialisation logic; requires careful regression testing to avoid disrupting production.
* **Time Investment**: Achieving ~100 % coverage across numerous endpoints is labour-intensive; may require iterative cycles to close gaps.
* **SQLAlchemy Typing**: Aligning the ORM models with mypy strict mode can be challenging; may necessitate adopting SQLAlchemy 2.0 typing conventions or selective `type: ignore` pragmas.
* **JWT Testing Complexity**: Simulating near-expiry tokens for the refresh hook demands precise control over token timestamps.

# Additional notes, links

* Mermaid docs: <https://mermaid.js.org/> (for ER, sequence, and class diagrams).
* Flask testing patterns: <https://flask.palletsprojects.com/en/latest/testing/>.
* SQLAlchemy typing guide: <https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html#using-typing-annotations>.
* `flask-jwt-extended` testing helpers: <https://flask-jwt-extended.readthedocs.io/en/stable/testing/>.
* Will ensure compatibility with existing tooling (Poetry) and align dependency versions accordingly.
