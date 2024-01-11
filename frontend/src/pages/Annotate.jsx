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

import { useEffect, useRef, useState } from "react";

import Spinner from "../components/Spinner";
import AnnotateInstance from "../features/annotations/AnnotateInstance";
import { useAnnotations } from "../features/annotations/useAnnotations";
import { clamp } from "../services/utils";

export default function AnnotatePage() {
  const containerRef = useRef(null);
  const [currentAnnotation, setCurrentAnnotation] = useState(0);
  const { status, annotations, isLoading } = useAnnotations();

  function getUnannotatedLength() {
    return annotations.filter((a) => !a["isAnnotated"]).length;
  }

  useEffect(() => {
    if (status === "success") {
      setCurrentAnnotation(
        clamp(currentAnnotation, 0, getUnannotatedLength() - 1),
      );
    }
  }, [status, annotations]);

  // If currently loading annotations, show a spinner
  if (isLoading) {
    return <Spinner />;
  }

  // If there are no annotations, show a message
  if (annotations.filter((a) => !a["isAnnotated"]).length === 0) {
    return (
      <div className="container">
        <div className="row">
          <div className="col-12">
            <div className="row">
              <div className="tw-mb-4 tw-flex tw-justify-between">
                <div />
                <div />
              </div>
              <div className="tw-flex tw-flex-col tw-items-center">
                <h1 className="tw-mb-4 tw-text-3xl tw-font-bold">
                  You're all done!
                </h1>
                <p className="tw-mb-4 tw-text-lg">
                  Thank you for your contribution. You can now close this page.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container" ref={containerRef}>
      <div className="row">
        <div className="col-12">
          <div id="annotation" className="row">
            <div className="tw-mb-4 tw-flex tw-justify-between">
              {currentAnnotation > 0 ? (
                <button
                  className="tw-text-blue-500 hover:tw-text-blue-600 hover:tw-underline"
                  onClick={() =>
                    setCurrentAnnotation(
                      clamp(
                        currentAnnotation - 1,
                        0,
                        getUnannotatedLength() - 1,
                      ),
                    )
                  }
                >
                  &larr; Previous
                </button>
              ) : (
                <div />
              )}
              {currentAnnotation < getUnannotatedLength() - 1 ? (
                <button
                  className="tw-text-blue-500 hover:tw-text-blue-600 hover:tw-underline"
                  onClick={() =>
                    setCurrentAnnotation(
                      clamp(
                        currentAnnotation + 1,
                        0,
                        getUnannotatedLength() - 1,
                      ),
                    )
                  }
                >
                  Next &rarr;
                </button>
              ) : (
                <div />
              )}
            </div>
            <AnnotateInstance
              containerRef={containerRef}
              annotation={
                annotations
                  .sort((a, b) => a["id"] - b["id"])
                  .filter((a) => !a["isAnnotated"])[
                  clamp(currentAnnotation, 0, getUnannotatedLength() - 1)
                ]
              }
              done={annotations.filter((a) => a["isAnnotated"]).length}
              total={annotations.length}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
