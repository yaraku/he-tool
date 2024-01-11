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

import { useMutation, useQuery } from "@tanstack/react-query";

import {
  createAnnotationMarking as createAnnotationMarkingApi,
  deleteAnnotationMarking as deleteAnnotationMarkingApi,
  getAnnotationMarkings as getAnnotationMarkingsApi,
  updateAnnotationMarking as updateAnnotationMarkingApi,
} from "../../services/apiMarkings";

export function useAnnotationMarkings({ id }) {
  const {
    data: annotationMarkings,
    error,
    isLoading,
  } = useQuery({
    queryKey: ["annotationMarkings", id],
    queryFn: () => getAnnotationMarkingsApi({ id }),
  });

  return { annotationMarkings, error, isLoading };
}

export function useCreateAnnotationMarking() {
  const { mutate: createAnnotationMarking, isLoading } = useMutation({
    mutationFn: (data) => createAnnotationMarkingApi(data),
    onSuccess: (data, { onSuccess }) => onSuccess(data),
    onError: (error, { onError }) => onError(error),
    onSettled: (data, error, { onSettled }) => onSettled(data, error),
  });

  return { createAnnotationMarking, isLoading };
}

export function useDeleteAnnotationMarking() {
  const { mutate: deleteAnnotationMarking, isLoading } = useMutation({
    mutationFn: (data) => deleteAnnotationMarkingApi(data),
    onSuccess: (data, { onSuccess }) => onSuccess(data),
    onError: (error, { onError }) => onError(error),
    onSettled: (data, error, { onSettled }) => onSettled(data, error),
  });

  return { deleteAnnotationMarking, isLoading };
}

export function useUpdateAnnotationMarking() {
  const { mutate: updateAnnotationMarking, isLoading } = useMutation({
    mutationFn: (data) => updateAnnotationMarkingApi(data),
    onSuccess: (data, { onSuccess }) => onSuccess(data),
    onError: (error, { onError }) => onError(error),
    onSettled: (data, error, { onSettled }) => onSettled(data, error),
  });

  return { updateAnnotationMarking, isLoading };
}
