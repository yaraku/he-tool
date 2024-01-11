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

import { Link } from "react-router-dom";

export default function NotFoundPage() {
  return (
    <div className="col-xs-1 text-center">
      <h1 className="tw-text-7xl tw-text-blue-700">404</h1>
      <p className="tw-mb-2 tw-text-xl tw-text-gray-700">
        Something's missing.
      </p>
      <p className="tw-mb-2">
        Sorry, we can't find that page. You'll find lots to explore on the home
        page.
      </p>
      <Link
        className="tw-font-semibold tw-text-blue-500 hover:tw-text-blue-600 hover:tw-underline"
        to="/"
      >
        Back to Homepage
      </Link>
    </div>
  );
}
