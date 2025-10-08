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

# Bitext model.

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .. import Base


if TYPE_CHECKING:  # pragma: no cover
    from .annotation import Annotation
    from .document import Document


class Bitext(Base):
    __tablename__ = "bitext"

    id: Mapped[int] = mapped_column(primary_key=True)
    documentId: Mapped[int] = mapped_column(ForeignKey("document.id"), nullable=False)
    source: Mapped[str] = mapped_column(Text, nullable=False)
    target: Mapped[str | None] = mapped_column(Text)
    createdAt: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updatedAt: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    document: Mapped["Document"] = relationship("Document", back_populates="bitexts")
    annotations: Mapped[list["Annotation"]] = relationship(
        "Annotation", back_populates="bitext", cascade="all, delete-orphan"
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "documentId": self.documentId,
            "source": self.source,
            "target": self.target,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }
