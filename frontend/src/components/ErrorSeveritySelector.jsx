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

export default function ErrorSeveritySelector(props) {
  return (
    <select
      className={props.className}
      disabled={props.disabled}
      onChange={props.onChange}
      value={props.value}
    >
      <option id="critical" value="critical">
        Critical
      </option>
      <option id="major" value="major">
        Major
      </option>
      <option id="minor" value="minor">
        Minor
      </option>
      <option id="not-judgeable" value="not-judgeable">
        Not Judgeable
      </option>
      <option id="no-error" value="no-error">
        None
      </option>
    </select>
  );
}
