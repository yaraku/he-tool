/*
 * Copyright (C) 2023 Yaraku, Inc.
 *
 * This file is part of Human Evaluation Tool.
 *
 * Human Evaluation Tool is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by the
 * Free Software Foundation, either version 3 of the License,
 * or (at your option) any later version.
 *
 * Human Evaluation Tool is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
 * or FITNESS FOR A PARTICULAR PURPOSE.
 * See the GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License along with
 * Human Evaluation Tool. If not, see <https://www.gnu.org/licenses/>.
 *
 * Written by Giovanni G. De Giacomo <giovanni@yaraku.com>, August 2023
 */

import { useEffect, useState } from "react";

import ErrorCategorySelector from "./ErrorCategorySelector";
import ErrorSeveritySelector from "./ErrorSeveritySelector";

export default function MarkingPopup({
  containerRef,
  marking,
  selection,
  disabled,
  mouseX,
  mouseY,
  createMarking,
  deleteMarking,
  updateMarking,
}) {
  const { x: parentX, y: parentY } = containerRef.getBoundingClientRect();
  const [category, setCategory] = useState("000");
  const [severity, setSeverity] = useState("no-error");
  useEffect(() => {
    if (marking) {
      setCategory(marking.errorCategory);
      setSeverity(marking.errorSeverity);
    } else {
      setCategory("000");
      setSeverity("no-error");
    }
  }, [marking, selection]);

  return (
    <div
      className="tw-absolute tw-z-[1002] tw-select-none tw-divide-y tw-divide-solid tw-rounded-md tw-bg-white tw-p-2 tw-shadow-card"
      style={{
        left: `${mouseX - parentX + 160}px`,
        top: `${mouseY - parentY + 10}px`,
      }}
    >
      <div className="tw-inline-flex tw-flex-col tw-gap-y-1.5 tw-text-sm">
        <div className="tw-inline-flex tw-flex-row tw-gap-x-1.5">
          <ErrorCategorySelector
            className="btn btn-outline-dark"
            disabled={marking ? !marking.id || disabled : disabled}
            onChange={(e) => {
              if (marking) {
                updateMarking({
                  marking,
                  category: e.target.value,
                  severity: marking.errorSeverity,
                });
              } else {
                setCategory(e.target.value);
              }
            }}
            value={category}
          />
          <ErrorSeveritySelector
            className="btn btn-outline-dark"
            disabled={marking ? !marking.id || disabled : disabled}
            onChange={(e) => {
              if (marking) {
                updateMarking({
                  marking,
                  category: marking.errorCategory,
                  severity: e.target.value,
                });
              } else {
                setSeverity(e.target.value);
              }
            }}
            value={severity}
          />
          {marking ? (
            <button
              className="btn btn-primary"
              disabled={marking ? !marking.id || disabled : disabled}
              onClick={() => deleteMarking({ marking })}
            >
              -
            </button>
          ) : (
            <button
              className="btn btn-primary"
              onClick={() => {
                let start = parseInt(selection.anchorNode.parentElement.id);
                let end = parseInt(selection.focusNode.parentElement.id);
                if (start > end) {
                  [start, end] = [end, start];
                }

                createMarking({
                  start,
                  end,
                  category,
                  severity,
                });
              }}
            >
              +
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
