# Human Evaluation Tool Backend

The backend is a Flask + SQLAlchemy application that powers the Human Evaluation Tool. It exposes a REST API for managing evaluations, documents, bitext pairs, annotations, systems, markings, and authentication.

## Quick start

```bash
cd backend
poetry install --with dev
poetry run python main.py
```

The development entry point automatically falls back to a SQLite database (`sqlite:///development.db`) and a deterministic JWT secret when the corresponding environment variables are absent. Override them via the environment before launching the server in order to point at PostgreSQL or to use a production-grade secret. When the SQLite fallback is used the database is automatically seeded with:

- A demo user: email `yaraku@yaraku.com`, password `yaraku`
- A "Sample Evaluation" containing two sentences from the "Sample Machine Translation QA" document and machine translations produced by the "Test MT System"

This makes it possible to log in immediately and try the annotation workflow without any manual setup.

You can also use the standard Flask CLI:

```bash
poetry run flask --app human_evaluation_tool:app run --debug
```

## Configuration

`create_app` layers configuration from three sources, in order of precedence:

1. `flask.config.json` (JWT cookie defaults)
2. Environment overrides passed to `create_app` (e.g. from `main.py` or tests)
3. The runtime environment variables

When a concrete `SQLALCHEMY_DATABASE_URI` is not provided, the factory falls back to assembling a PostgreSQL URL from:

- `DB_HOST`
- `DB_NAME`
- `DB_PASSWORD`
- `DB_PORT`
- `DB_USER`

At minimum you must define `JWT_SECRET_KEY` (unless you rely on the development defaults) and either the database URI or the five database components above.

## Project layout

```text
backend/
├── flask.config.json        # JWT cookie defaults
├── main.py                  # Development runner that calls create_app()
├── pyproject.toml           # Poetry + tooling configuration
├── src/
│   └── human_evaluation_tool/
│       ├── __init__.py      # App factory and extension wiring
│       ├── auth.py          # Authentication blueprint
│       ├── models/          # SQLAlchemy 2.0 typed ORM models
│       ├── resources/       # REST resources registered as blueprints
│       └── utils.py         # Shared category/severity lookups
└── tests/                   # Pytest suite with fixtures and API coverage
```

## Architecture highlights

- **Application factory** – `create_app` wires Flask extensions (SQLAlchemy, JWT, bcrypt, migration), loads configuration, and registers the authentication and resource blueprints. The module exports a ready-to-serve `app` for WSGI usage as well as the shared extensions for imports.
- **Blueprint modularity** – Each resource (`annotations`, `bitexts`, `documents`, `evaluations`, `markings`, `systems`, `users`) lives in its own blueprint with typed request handlers and explicit validation.
- **Typed ORM models** – Models use SQLAlchemy 2.0 style `Mapped[...]` annotations backed by the shared declarative `Base`. Relationships between users, evaluations, annotations, systems, and markings mirror the evaluation workflow.
- **Static asset bridge** – The factory serves files from the repository-level `public/` directory so the backend can host the SPA build output in production.

See `docs/backend/architecture.md` for a component diagram and deeper discussion.

## Data model

The persistent entities cover the evaluation workflow:

- `User` – annotators and admins
- `System` – machine translation systems under evaluation
- `Document`/`Bitext` – source documents and aligned source/target segments
- `Evaluation` – collections of annotations for a given study
- `Annotation` – annotator work tied to a bitext in an evaluation
- `AnnotationSystem` – translation outputs per annotation/system pair
- `Marking` – individual error markings with category/severity metadata

`docs/backend/domain-model.md` includes an ER diagram and class relationships.

## Quality gates

All automated quality tooling is configured via Poetry:

```bash
poetry run pytest                 # Run the full test suite
poetry run coverage run -m pytest # Collect coverage
poetry run coverage report        # Display coverage summary (targets 100 %)
poetry run mypy src tests         # Strict static type checking
```

The pytest suite boots an application instance with an in-memory SQLite database, seeds fixtures for every model, and exercises success/error paths for each API endpoint (including auth flows and evaluation exports). Mypy runs in `strict` mode with targeted overrides for the test package.

## Further reading

The `docs/backend` knowledge base expands on architecture, domain design, API flows, and the testing/type-checking toolkit:

- [`docs/backend/architecture.md`](../docs/backend/architecture.md)
- [`docs/backend/domain-model.md`](../docs/backend/domain-model.md)
- [`docs/backend/api-flows.md`](../docs/backend/api-flows.md)
- [`docs/backend/testing-and-quality.md`](../docs/backend/testing-and-quality.md)
