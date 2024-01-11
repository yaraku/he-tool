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

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";

import { useAnnotationMarkings } from "./useAnnotationMarkings";
import { useAnnotationSystems } from "./useAnnotationSystems";
import { useDocumentBitexts } from "./useDocumentBitexts";
import { updateAnnotation as updateAnnotationApi } from "../../services/apiAnnotations";
import Marking from "../../components/Marking";
import Spinner from "../../components/Spinner";
import SpinnerMini from "../../components/SpinnerMini";

export default function AnnotateInstance({
  containerRef,
  annotation,
  done,
  total,
}) {
  const { annotationMarkings, isLoading: areMarkingsLoading } =
    useAnnotationMarkings({
      id: annotation["id"],
    });
  const { annotationSystems, isLoading: areSystemsLoading } =
    useAnnotationSystems({
      id: annotation["id"],
    });
  const { documentBitexts, isLoading: areBitextsLoading } = useDocumentBitexts({
    id: annotation["bitext"]["documentId"],
  });
  const queryClient = useQueryClient();

  const { mutate: updateAnnotation, isLoading: isAnnotationUpdating } =
    useMutation({
      mutationFn: (data) => updateAnnotationApi(data),
      onSuccess: (data) => {
        queryClient.setQueryData(["annotations"], (annotations) => {
          annotations.map((a) => {
            if (a["id"] === data["id"]) {
              return {
                ...a,
                isAnnotated: data["isAnnotated"],
                comment: data["comment"],
              };
            }

            return a;
          });
        });
      },
      onError: (error) => {
        toast.error(
          `Failed to update annotation: ${error}. Please check your connection and try again.`,
        );
      },
      onSettled: () => {
        queryClient.invalidateQueries({
          queryKey: ["annotations"],
        });
      },
    });

  function handleFinish(e) {
    e.preventDefault();
    updateAnnotation({
      id: annotation["id"],
      userId: annotation["userId"],
      evaluationId: annotation["evaluation"]["id"],
      bitextId: annotation["bitext"]["id"],
      isAnnotated: true,
      comment: "",
    });
  }

  if (areBitextsLoading || areMarkingsLoading || areSystemsLoading) {
    return (
      <div>
        <Spinner />
      </div>
    );
  }

  return (
    <div className="container">
      <div className="tw-mb-6 tw-flex tw-justify-between">
        <div>
          <b>Evaluation Name:</b>&nbsp;
          {annotation["evaluation"]["name"]}
        </div>
        <div className="tw-justify-between tw-space-x-8">
          <b>Done:</b>&nbsp;{done}
          <b>Total:</b>&nbsp;{total}
        </div>
      </div>
      <div className="row">
        <div className="col alert alert-warning text-center">
          <h5>
            Please select and right-click to highlight incorrect spans in the
            translated sentences below.
          </h5>
        </div>
      </div>
      <div className="row">
        <div className="col align-middle">
          <div className="row text-left content-row d-flex justify-content-center">
            {annotationSystems.map((system, systemIndex) => {
              return (
                <div className="tw-select-none">
                  <Marking
                    containerRef={containerRef}
                    annotationId={annotation["id"]}
                    systemId={system["systemId"]}
                    systemIndex={systemIndex}
                    annotationMarkings={annotationMarkings.filter(
                      (m) => m["systemId"] === system["systemId"],
                    )}
                    source={annotation["bitext"]["source"]}
                    target={system["translation"]}
                  />
                  <div className="border-top pt-3" />
                </div>
              );
            })}
            <button
              className="btn btn-primary tw-mb-4 tw-w-full"
              disabled={isAnnotationUpdating}
              onClick={handleFinish}
            >
              {isAnnotationUpdating ? (
                <div className="tw-flex tw-justify-center">
                  <SpinnerMini />
                </div>
              ) : (
                "Finish"
              )}
            </button>
            <div className="card tw-mb-4">
              <div className="card-header">Reference</div>
              <div className="card-body">
                <p>{annotation["bitext"]["target"]}</p>
              </div>
            </div>
            {documentBitexts.length > 1 ? (
              <div className="card">
                <div className="card-header">Document Context</div>
                <div className="card-body">
                  <table className="table">
                    <tr>
                      <th>Source</th>
                      <th>Target</th>
                    </tr>
                    {documentBitexts.map((bitext) => {
                      if (bitext["id"] === annotation["bitext"]["id"]) {
                        return (
                          <tr className="tw-border-b tw-border-t tw-border-solid tw-bg-green-100">
                            <td className="tw-py-4">{bitext["source"]}</td>
                            <td className="tw-py-4">{bitext["target"]}</td>
                          </tr>
                        );
                      }

                      return (
                        <tr className="tw-border-b tw-border-t tw-border-solid">
                          <td className="tw-py-4">{bitext["source"]}</td>
                          <td className="tw-py-4">{bitext["target"]}</td>
                        </tr>
                      );
                    })}
                  </table>
                </div>
              </div>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  );
}
