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

import MarkingItem from "./MarkingItem";

export default function Marking({
  containerRef,
  annotationId,
  systemId,
  systemIndex,
  annotationMarkings,
  source,
  target,
}) {
  return (
    <div id="markingParent" className="container-fluid" tabIndex="0">
      <div className="row">
        <div className="col-sm-2 markingHead">Source</div>
        <MarkingItem
          containerRef={containerRef}
          annotationId={annotationId}
          systemId={systemId}
          annotationMarkings={annotationMarkings.filter((m) => m["isSource"])}
          isSource={true}
          text={source}
        />
      </div>
      <div className="row">
        <div className="col-sm-2 markingHead">System {systemIndex + 1}</div>
        <MarkingItem
          containerRef={containerRef}
          annotationId={annotationId}
          systemId={systemId}
          annotationMarkings={annotationMarkings.filter((m) => !m["isSource"])}
          isSource={false}
          text={target}
        />
      </div>
    </div>
  );
}
