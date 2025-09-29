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

from .. import db


class Evaluation(db.Model):
    """
    Represents an evaluation project in the system.

    Attributes:
        id (int): Primary key for the evaluation
        name (str): Unique name of the evaluation project (max 120 chars)
        type (str): Type of evaluation (e.g., 'error-marking', 'ranking') (max 20 chars)
        isFinished (bool): Whether the evaluation is complete
        createdAt (datetime): When the evaluation was created
        updatedAt (datetime): When the evaluation was last updated
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    type = db.Column(db.String(20), nullable=False)
    isFinished = db.Column(db.Boolean, nullable=False, default=False)
    createdAt = db.Column(db.DateTime, nullable=False)
    updatedAt = db.Column(db.DateTime, nullable=False)

    def to_dict(self):
        """
        Converts the evaluation object to a dictionary for JSON serialization.

        Returns:
            dict: Dictionary representation of the evaluation with all its fields
        """
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "isFinished": self.isFinished,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }
