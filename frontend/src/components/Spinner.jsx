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

export default function Spinner() {
  return (
    <div className="tw-absolute tw-bottom-1/2 tw-right-1/2 tw-translate-x-1/2 tw-translate-y-1/2 tw-transform">
      <div className="tw-h-24 tw-w-24 tw-animate-spin tw-rounded-full tw-border-8 tw-border-solid tw-border-gray-600 tw-border-t-transparent" />
    </div>
  );
}
