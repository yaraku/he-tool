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

export async function getAnnotationSystems({ id }) {
  if (id == 1) {
    return [
      {
        id: 1,
        annotationId: 1,
        systemId: 1,
        translation: "我が 名 は ジャコモ ジョバンニ で ある 。",
      },
      {
        id: 2,
        annotationId: 1,
        systemId: 2,
        translation: "私 は ジャコモ ジョバンニ と 申します 。",
      },
    ];
  } else if (id == 2) {
    return [
      {
        id: 3,
        annotationId: 2,
        systemId: 1,
        translation: "我が 名 は ビプル ミシュラ で ある 。",
      },
      {
        id: 4,
        annotationId: 2,
        systemId: 2,
        translation: "私 は ビプル ミシュラ と 申します 。",
      },
    ];
  } else if (id == 3) {
    return [
      {
        id: 5,
        annotationId: 3,
        systemId: 1,
        translation: "我が 名 は フー バー で ある 。",
      },
      {
        id: 6,
        annotationId: 3,
        systemId: 2,
        translation: "私 は フー バー と 申します 。",
      },
    ];
  } else {
    return [];
  }

  const response = await fetch(`/api/annotations/${id}/systems`, {
    method: "GET",
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error(
      `Get systems for annotation ${id} failed: ${response.status}`,
    );
  }

  return await response.json();
}
