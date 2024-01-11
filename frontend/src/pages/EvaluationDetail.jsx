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
import { useParams } from "react-router-dom";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";

import Spinner from "../components/Spinner";
import { updateAnnotation as updateAnnotationApi } from "../services/apiAnnotations";
import { useDocuments } from "../features/evaluations/useDocuments";
import { useEvaluationAnnotations } from "../features/evaluations/useEvaluationAnnotations";

export default function EvaluationDetailPage() {
  const { id } = useParams();
  const queryClient = useQueryClient();
  const {
    status: annotationStatus,
    evaluationAnnotations,
    isLoading: areAnnotationsLoading,
  } = useEvaluationAnnotations({ id });
  const {
    status: documentStatus,
    documents,
    isLoading: areDocumentsLoading,
  } = useDocuments();
  const [documentsToAnnotations, setDocumentsToAnnotations] = useState([]);
  const { mutate: updateAnnotation, isLoading: isAnnotationUpdating } =
    useMutation({
      mutationFn: (data) => updateAnnotationApi(data),
      onSuccess: (data) => {
        queryClient.setQueryData(["evaluationAnnotations", id], (annotations) =>
          annotations.map((a) => {
            if (a.id === data.id) {
              return {
                ...a,
                isAnnotated: data["isAnnotated"],
              };
            }

            return a;
          }),
        );
      },
      onError: (error) => {
        toast.error(
          `Failed to update annotation: ${error}. Please check your connection and try again.`,
        );
      },
      onSettled: () => {
        queryClient.invalidateQueries({
          queryKey: ["evaluationAnnotations", id],
        });
      },
    });

  useEffect(() => {
    if (annotationStatus === "success" && documentStatus === "success") {
      let newDocuments = new Map();
      evaluationAnnotations.forEach((annotation) => {
        const document = documents.find(
          (d) => d["id"] === annotation["bitext"]["documentId"],
        );
        if (document) {
          const documentName = document["name"];
          if (!newDocuments.has(documentName)) {
            newDocuments.set(documentName, []);
          }

          newDocuments.get(documentName).push(annotation);
        }
      });

      setDocumentsToAnnotations([...newDocuments.entries()]);
    }
  }, [annotationStatus, evaluationAnnotations, documentStatus, documents]);

  if (areAnnotationsLoading || areDocumentsLoading) {
    return <Spinner />;
  }

  return (
    <div className="row">
      <div className="col-12">
        <div className="row justify-content-center">
          {documentsToAnnotations.map(([documentName, document]) => {
            return (
              <div className="row tw-mb-8">
                <h3 className="tw-mb-4 tw-text-2xl tw-text-gray-700">
                  {documentName}
                </h3>
                <div className="tw-relative tw-overflow-x-auto tw-shadow-md sm:tw-rounded-lg">
                  <table className="tw-w-full tw-text-left tw-text-sm tw-text-gray-500">
                    <thead className="tw-bg-gray-50 tw-text-xs tw-uppercase tw-text-gray-700">
                      <tr>
                        <th scope="col" className="tw-px-6 tw-py-3">
                          Source
                        </th>
                        <th scope="col" className="tw-px-6 tw-py-3">
                          Reference
                        </th>
                        <th scope="col" className="tw-px-6 tw-py-3">
                          Finished?
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {document
                        .sort((a, b) => a["id"] - b["id"])
                        .map((annotation) => {
                          return (
                            <tr className="tw-border-b tw-bg-white">
                              <td className="tw-px-6 tw-py-4">
                                <span>{annotation["bitext"]["source"]}</span>
                              </td>
                              <td className="tw-px-6 tw-py-4">
                                <span>{annotation["bitext"]["target"]}</span>
                              </td>
                              <td className="tw-px-6 tw-py-4">
                                <input
                                  type="checkbox"
                                  disabled={isAnnotationUpdating}
                                  checked={annotation["isAnnotated"]}
                                  onChange={() => {
                                    updateAnnotation({
                                      id: annotation["id"],
                                      userId: annotation["userId"],
                                      evaluationId:
                                        annotation["evaluation"]["id"],
                                      bitextId: annotation["bitext"]["id"],
                                      isAnnotated: !annotation["isAnnotated"],
                                      comment: annotation["comment"],
                                    });
                                  }}
                                />
                              </td>
                            </tr>
                          );
                        })}
                    </tbody>
                  </table>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
