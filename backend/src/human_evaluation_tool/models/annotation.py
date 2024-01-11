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

from .bitext import Bitext
from .evaluation import Evaluation


class Annotation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    evaluationId = db.Column(db.Integer, db.ForeignKey("evaluation.id"), nullable=False)
    bitextId = db.Column(db.Integer, db.ForeignKey("bitext.id"), nullable=False)
    isAnnotated = db.Column(db.Boolean, nullable=False, default=False)
    comment = db.Column(db.Text, nullable=True)
    createdAt = db.Column(db.DateTime, nullable=False)
    updatedAt = db.Column(db.DateTime, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "userId": self.userId,
            "evaluation": Evaluation.query.get(self.evaluationId).to_dict(),
            "bitext": Bitext.query.get(self.bitextId).to_dict(),
            "isAnnotated": self.isAnnotated,
            "comment": self.comment,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }
