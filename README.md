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

- Python 3.10 or later
- Node.js 18 or later
- PostgreSQL 13 or later
- Poetry (Python package manager)
- npm (Node.js package manager)

## Installation and Setup

### Option 1: Using Docker (Recommended)

1. Build the Docker image:
```sh
docker build -t yaraku/human-evaluation-tool .
```

2. Run the container:
```sh
docker run --rm -it -p 8000:8000 yaraku/human-evaluation-tool
```

### Option 2: Manual Setup

1. Install prerequisites:
   - Python 3.10 or later
   - Node.js 18 or later
   - PostgreSQL 13 or later
   - Poetry (Python package manager)
   - npm (Node.js package manager)

2. Set up PostgreSQL:
```sh
# Start PostgreSQL service
sudo service postgresql start

# Create database and set password
sudo -u postgres createdb he_tool
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'postgres';"
```

3. Set up the backend:
```sh
cd backend

# Install dependencies
poetry install

# Create and configure .env file
cat > .env << EOL
FLASK_APP=main.py
FLASK_ENV=development
DB_HOST=localhost
DB_PORT=5432
DB_NAME=he_tool
DB_USER=postgres
DB_PASSWORD=postgres
JWT_SECRET_KEY=development-secret-key
EOL

# Initialize and run migrations
poetry run flask db init
poetry run flask db migrate
poetry run flask db upgrade

# Start the backend server
poetry run python main.py
```

4. Set up the frontend (in a new terminal):
```sh
cd frontend

# Install dependencies
npm install

# Create and configure .env file
echo "VITE_API_URL=http://localhost:5000" > .env

# Start the development server
npm run dev
```

5. Access the application:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:5000

## Usage

1. Access the application at http://localhost:5173
2. Register a new account or log in
3. Create a new evaluation project
4. Upload documents and system outputs
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
poetry run flask db migrate  # Create new migrations
poetry run flask db upgrade  # Apply migrations
poetry run python main.py  # Run development server
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

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the GPL-3.0 License - see the LICENSE file for details.
