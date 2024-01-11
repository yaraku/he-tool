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

export async function getAnnotations() {
  return [
    {
      id: 1,
      evaluation: { name: "ChatGPT Test Evaluation" },
      bitext: {
        id: 1,
        documentId: 1,
        source: "My name is Giovanni Giacomo .",
        target: "私 の 名前 は ジャコモ ジョバンニ です 。",
      },
      isAnnotated: false,
    },
    {
      id: 2,
      evaluation: { name: "ChatGPT Test Evaluation" },
      bitext: {
        id: 2,
        documentId: 1,
        source: "My name is Vipul Mishra .",
        target: "私 の 名前 は ビプル ミシュラ です 。",
      },
      isAnnotated: true,
    },
    {
      id: 3,
      evaluation: { name: "ChatGPT Test Evaluation" },
      bitext: {
        id: 3,
        documentId: 1,
        source: "My name is Foo Bar .",
        target: "私 の 名前 は フー バー です 。",
      },
      isAnnotated: false,
    },
  ];

  const response = await fetch("/api/annotations", {
    method: "GET",
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error(`Get annotations failed: ${response.status}`);
  }

  return await response.json();
}

export async function updateAnnotation({
  id,
  userId,
  evaluationId,
  bitextId,
  isAnnotated,
  comment,
}) {
  const response = await fetch(`/api/annotations/${id}`, {
    method: "PUT",
    credentials: "same-origin",
    headers: {
      "Content-Type": "application/json",
      "X-CSRF-TOKEN": getCookie("csrf_access_token"),
    },
    body: JSON.stringify({
      userId,
      evaluationId,
      bitextId,
      isAnnotated,
      comment,
    }),
  });

  if (!response.ok) {
    throw new Error(`Update annotation ${id} failed: ${response.status}`);
  }

  return await response.json();
}
