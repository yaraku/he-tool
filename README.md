# Human Evaluation Tool

A web-based tool for conducting human evaluation of machine translation outputs. This tool allows evaluators to assess and compare translations from different systems, mark errors, and provide detailed feedback.

## Features

- User authentication and authorization
- Support for multiple language pairs
- Error marking and categorization
- Severity level assessment
- Side-by-side comparison of translations
- Progress tracking
- Results aggregation and export

## Demo

Below is a quick video showing how the Human Evaluation Tool looks and works:

https://github.com/yaraku/he-tool/assets/5934186/bb1dcf1c-a1e2-464c-af0a-1225e57eef56

## Project Structure

The project consists of three main components:

- `backend/`: Flask-based REST API server
- `frontend/`: React-based web application
- `public/`: Static assets and built files

## Prerequisites

- [Podman](https://podman.io/) (or Docker — commands are identical)
- `podman compose` or `podman-compose` for the multi-container setup

For manual setup you also need Python 3.10+, Node.js 18+, PostgreSQL 16+, and Poetry.

## Installation and Setup

### Option 1: Podman Compose with PostgreSQL (Recommended)

This is the production-ready path. PostgreSQL data is persisted in a named volume.

1. Copy and configure the environment file:
```sh
cp .env.example .env
# Edit .env — set DB_PASSWORD and JWT_SECRET_KEY to real values.
# Generate a secret key with:
#   python3 -c "import secrets; print(secrets.token_hex(32))"
```

2. Start everything:
```sh
podman compose up
```

On first start the app container runs `flask db upgrade` to create the schema, then starts gunicorn. Open http://localhost:8000.

To rebuild after code changes:
```sh
podman compose up --build
```

### Option 2: Single container (SQLite demo)

No PostgreSQL needed. Runs with an in-memory SQLite database pre-seeded with a demo user and sample evaluation.

```sh
podman build -t he-tool .
podman run --rm -p 8000:8000 he-tool
```

> **Note:** The build installs Poetry versions satisfying `>=1.5,<1.7` by default.
> Override with `--build-arg POETRY_VERSION_CONSTRAINT="==1.6.1"` if needed.

### Option 3: Manual Setup

1. Set up PostgreSQL and create a database:
```sh
sudo -u postgres createdb he_tool
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'postgres';"
```

2. Set up the backend:
```sh
cd backend

# Install dependencies
poetry install

# Create .env
cat > .env << EOL
FLASK_APP=human_evaluation_tool:app
DB_HOST=localhost
DB_PORT=5432
DB_NAME=he_tool
DB_USER=postgres
DB_PASSWORD=postgres
JWT_SECRET_KEY=development-secret-key
EOL

# Apply migrations (schema is already defined in backend/migrations/)
poetry run flask db upgrade

# Start the development server
poetry run python main.py
```

3. Set up the frontend (in a new terminal):
```sh
cd frontend
npm install
npm run dev
```

4. Access the application:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:5000

## Usage

When you run the backend without PostgreSQL credentials it falls back to a local SQLite database. That database is pre-populated with a demo user (`yaraku@yaraku.com` / `yaraku`) and a "Sample Evaluation" so you can explore the workflow immediately.

1. Access the application at http://localhost:5173
2. Log in with the demo credentials above or register a new account
3. Open the "Sample Evaluation" to try the annotation UI, or create a new evaluation project
4. Upload documents and system outputs when running your own studies
5. Start evaluating translations

## Development

### Backend Development

The backend is built with Flask and uses:
- SQLAlchemy for database ORM
- Flask-JWT-Extended for authentication
- Flask-Migrate for database migrations

Key commands:
```sh
cd backend
poetry run flask db upgrade              # Apply pending migrations
poetry run flask db migrate -m "desc"   # Generate a new migration after model changes
poetry run python main.py               # Run development server
poetry run gunicorn --bind 0.0.0.0:8000 human_evaluation_tool:app  # Run with Gunicorn
```

### Frontend Development

The frontend is built with React and uses:
- Vite for build tooling
- TailwindCSS for styling
- React Query for data fetching

Key commands:
```sh
cd frontend
npm run dev  # Start development server
npm run build  # Build for production
npm run preview  # Preview production build
```

## Database Schema

The application uses a PostgreSQL database with the following main entities:

- Users: Evaluators and administrators
- Documents: Source texts for evaluation
- Systems: MT systems being evaluated
- Evaluations: Evaluation projects
- Annotations: User annotations and feedback
- Markings: Error markings and categorizations

For a detailed ER diagram, see `backend/README.md`.

## Customizing MQM Error Categories

Error categories are defined in `config/categories.txt` using a simple indented format:

```
000: No Error

Accuracy
  A01: Mistranslation
  A02: Omission
  ...

Fluency
  F01: Grammar
  ...
```

Top-level lines without indentation are group headers; indented lines are `ID: Label` entries. The ID is stored in the database — change it only with a migration. The label is display-only and safe to edit freely.

After editing the file, regenerate the backend constants and frontend selector:

```sh
python3 scripts/gen_categories.py
cd frontend && npm run build   # or podman compose up --build
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. For backend changes, install dependencies with `poetry install --with dev` and run:
   - `poetry run black --check src tests`
   - `poetry run isort --check-only src tests`
   - `poetry run flake8 src tests`
   - `poetry run mypy src tests`
   - `poetry run pytest`
4. Commit your changes
5. Push to the branch
6. Create a Pull Request and ensure the **Backend CI** workflow passes when touching backend code.

## License

This project is licensed under the GPL-3.0 License - see the LICENSE file for details.
