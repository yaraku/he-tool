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


class AnnotationSystem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    annotationId = db.Column(db.Integer, db.ForeignKey("annotation.id"), nullable=False)
    systemId = db.Column(db.Integer, db.ForeignKey("system.id"), nullable=False)
    translation = db.Column(db.Text, nullable=True)
    createdAt = db.Column(db.DateTime, nullable=False)
    updatedAt = db.Column(db.DateTime, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "annotationId": self.annotationId,
            "systemId": self.systemId,
            "translation": self.translation.replace("\\n", "\n"),
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }
