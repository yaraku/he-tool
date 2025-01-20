"""
Entry point for the Human Evaluation Tool backend server.

This script starts the Flask development server with the appropriate configuration
for local development. In production, use a WSGI server like Gunicorn instead.

Environment Variables:
    FLASK_APP: Set to 'main.py'
    FLASK_ENV: Set to 'development' for development mode
    DATABASE_URL: PostgreSQL connection string
    JWT_SECRET_KEY: Secret key for JWT token generation
"""

from human_evaluation_tool import app


if __name__ == '__main__':
    app.run(
        host="0.0.0.0",  # Listen on all network interfaces
        port=5000,       # Default development port
        debug=True,      # Enable debug mode for development
        load_dotenv=True # Load environment variables from .env file
    )
