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

import { getCookie } from "./utils";

export async function getAnnotationMarkings({ id }) {
  const response = await fetch(`/api/annotations/${id}/markings`, {
    method: "GET",
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error(
      `Get markings for annotation ${id} failed: ${response.status}`,
    );
  }

  return await response.json();
}

export async function createAnnotationMarking({
  annotationId,
  systemId,
  start,
  end,
  category,
  severity,
  isSource,
}) {
  const response = await fetch(
    `/api/annotations/${annotationId}/systems/${systemId}/markings`,
    {
      method: "POST",
      credentials: "same-origin",
      headers: {
        "Content-Type": "application/json",
        "X-CSRF-TOKEN": getCookie("csrf_access_token"),
      },
      body: JSON.stringify({
        errorStart: start,
        errorEnd: end,
        errorCategory: category,
        errorSeverity: severity,
        isSource,
      }),
    },
  );

  if (!response.ok) {
    throw new Error(
      `Create marking for annotation ${annotationId} and system ${systemId} failed: ${response.status}`,
    );
  }

  return await response.json();
}

export async function updateAnnotationMarking({
  annotationId,
  systemId,
  markingId,
  start,
  end,
  category,
  severity,
  isSource,
}) {
  const response = await fetch(
    `/api/annotations/${annotationId}/systems/${systemId}/markings/${markingId}`,
    {
      method: "PUT",
      credentials: "same-origin",
      headers: {
        "Content-Type": "application/json",
        "X-CSRF-TOKEN": getCookie("csrf_access_token"),
      },
      body: JSON.stringify({
        errorStart: start,
        errorEnd: end,
        errorCategory: category,
        errorSeverity: severity,
        isSource,
      }),
    },
  );

  if (!response.ok) {
    throw new Error(
      `Update marking ${markingId} for annotation ${annotationId} and system ${systemId} failed: ${response.status}`,
    );
  }

  return await response.json();
}

export async function deleteAnnotationMarking({
  annotationId,
  systemId,
  markingId,
}) {
  const response = await fetch(
    `/api/annotations/${annotationId}/systems/${systemId}/markings/${markingId}`,
    {
      method: "DELETE",
      credentials: "same-origin",
      headers: {
        "X-CSRF-TOKEN": getCookie("csrf_access_token"),
      },
    },
  );

  if (!response.ok) {
    throw new Error(
      `Delete marking ${markingId} for annotation ${annotationId} and system ${systemId} failed: ${response.status}`,
    );
  }
}
