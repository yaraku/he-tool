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
 * Written by Giovanni G. De Giacomo <giovanni@yaraku.com>, September 2023
 */

import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";

import Spinner from "../components/Spinner";
import { useEvaluations } from "../features/evaluations/useEvaluations";
import { getEvaluationResults } from "../services/apiEvaluations";

import "../assets/viewer.css";

export default function ResultsPage() {
  const [evaluationIndex, setEvaluationIndex] = useState(0);

  const { evaluations, isLoading: areEvaluationsLoading } = useEvaluations();
  const evaluationId = evaluations?.[evaluationIndex]?.["id"];

  const { data: evaluationResults, isLoading: areResultsLoading } = useQuery({
    queryKey: ["evaluationResults", evaluationId],
    queryFn: () => getEvaluationResults({ id: evaluationId }),
    enabled: !!evaluationId,
  });

  useEffect(() => {
    if (!areEvaluationsLoading && !areResultsLoading) {
      mqmCreateViewer(document.getElementById("mqm"));
    }
  }, [areEvaluationsLoading, areResultsLoading]);

  useEffect(() => {
    if (!areEvaluationsLoading && !areResultsLoading) {
      mqmSetData(evaluationResults);
    }
  }, [evaluationResults]);

  if (areEvaluationsLoading || areResultsLoading) {
    return <Spinner />;
  }

  return (
    <div className="tw-m-4">
      <div className="tw-flex tw-flex-row">
        <h1 className="tw-text-lg tw-font-bold">Evaluation: </h1>
        <select
          value={evaluationIndex}
          onChange={(e) => setEvaluationIndex(e.target.value)}
        >
          {evaluations.map((evaluation, index) => {
            return <option value={index}>{evaluation["name"]}</option>;
          })}
        </select>
      </div>
      <hr />
      <div id="mqm"></div>
    </div>
  );
}
