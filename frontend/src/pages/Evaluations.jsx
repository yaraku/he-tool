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

import { Link } from "react-router-dom";

import Spinner from "../components/Spinner";
import { useEvaluations } from "../features/evaluations/useEvaluations";

export default function EvaluationsPage() {
  const { evaluations, isLoading } = useEvaluations();

  if (isLoading) {
    return <Spinner />;
  }

  // If there are no evaluations, show a message
  if (evaluations.filter((e) => !e["isFinished"]).length === 0) {
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
                  There are currently no ongoing evaluations. You can now close
                  this page.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="content">
      <div className="row"></div>
      <h3 className="tw-mb-4 tw-text-2xl tw-text-gray-700">
        Ongoing Evaluations
      </h3>
      <ul className="tw-ml-10 tw-list-item tw-list-disc">
        {evaluations
          .filter((e) => !e["isFinished"])
          .map((evaluation) => {
            return (
              <li className="tw-mb-2">
                <Link
                  className="tw-text-blue-500 hover:tw-text-blue-600 hover:tw-underline"
                  to={`/evaluations/${evaluation["id"]}`}
                >
                  {evaluation["name"]}
                </Link>
              </li>
            );
          })}
      </ul>
    </div>
  );
}
