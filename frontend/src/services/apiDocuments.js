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

export async function getDocuments() {
  return [
    {
      id: 1,
      name: "Sample Document",
    },
  ];

  const response = await fetch("/api/documents", {
    method: "GET",
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error(`Get documents failed: ${response.status}`);
  }

  return await response.json();
}

export async function getDocumentBitexts({ id }) {
  return [
    {
      id: 1,
      documentId: 1,
      source: "My name is Giovanni Giacomo .",
      target: "私 の 名前 は ジャコモ ジョバンニ です 。",
    },
    {
      id: 2,
      documentId: 1,
      source: "My name is Vipul Mishra .",
      target: "私 の 名前 は ビプル ミシュラ です 。",
    },
    {
      id: 3,
      documentId: 1,
      source: "My name is Foo Bar .",
      target: "私 の 名前 は フー バー です 。",
    },
  ];

  const response = await fetch(`/api/documents/${id}/bitexts`, {
    method: "GET",
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error(
      `Get bitexts for document ${id} failed: ${response.status}`,
    );
  }

  return await response.json();
}
