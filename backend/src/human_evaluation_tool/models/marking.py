"""Copyright (C) 2023 Yaraku, Inc.

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

# Marking model.

from __future__ import annotations

from datetime import datetime
from typing import Any, TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .. import Base

if TYPE_CHECKING:  # pragma: no cover
    from .annotation import Annotation
    from .system import System


class Marking(Base):
    __tablename__ = "marking"

    id: Mapped[int] = mapped_column(primary_key=True)
    annotationId: Mapped[int] = mapped_column(ForeignKey("annotation.id"), nullable=False)
    systemId: Mapped[int] = mapped_column(ForeignKey("system.id"), nullable=False)
    errorStart: Mapped[int] = mapped_column(Integer, nullable=False)
    errorEnd: Mapped[int] = mapped_column(Integer, nullable=False)
    errorCategory: Mapped[str] = mapped_column(String(20), nullable=False)
    errorSeverity: Mapped[str] = mapped_column(String(20), nullable=False)
    isSource: Mapped[bool] = mapped_column(Boolean, nullable=False)
    createdAt: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updatedAt: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    annotation: Mapped["Annotation"] = relationship(
        "Annotation", back_populates="markings"
    )
    system: Mapped["System"] = relationship("System", back_populates="markings")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "annotationId": self.annotationId,
            "systemId": self.systemId,
            "errorStart": self.errorStart,
            "errorEnd": self.errorEnd,
            "errorCategory": self.errorCategory,
            "errorSeverity": self.errorSeverity,
            "isSource": self.isSource,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }
