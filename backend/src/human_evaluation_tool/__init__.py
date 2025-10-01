"""
Copyright (C) 2023 Yaraku, Inc.

This file is part of Human Evaluation Tool.

Human Evaluation Tool is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License,
or (at your option) any later version.

Human Evaluation Tool is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
Human Evaluation Tool. If not, see <https://www.gnu.org/licenses/>.

Written by Giovanni G. De Giacomo <giovanni@yaraku.com>, August 2023
"""

import os
import json

from dotenv import load_dotenv
from flask import Flask, send_from_directory
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote_plus


# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__, static_folder="../../../public")
app.config.from_file("../../flask.config.json", load=json.load)
app.config["JWT_SECRET_KEY"] = os.environ["JWT_SECRET_KEY"]
app.json.sort_keys = False

# Set the database URI from the environment variables
if "SQLALCHEMY_DATABASE_URI" in os.environ:
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["SQLALCHEMY_DATABASE_URI"]
else:
    required_variables = ["DB_HOST", "DB_NAME", "DB_PASSWORD", "DB_PORT", "DB_USER"]
    if any(field not in os.environ for field in required_variables):
        raise RuntimeError("Missing required database environment variables")
    app.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = f"postgresql://{os.environ['DB_USER']}:{quote_plus(os.environ['DB_PASSWORD'])}@{os.environ['DB_HOST']}:{os.environ['DB_PORT']}/{os.environ['DB_NAME']}"

# Initialize Flask extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt_manager = JWTManager(app)
migrate = Migrate(app, db)


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def index(path):
    if path != "" and os.path.exists(app.static_folder + "/" + path):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, "index.html")


from . import auth  # noqa
from . import resources  # noqa
