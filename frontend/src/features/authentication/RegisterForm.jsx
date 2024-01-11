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

import { useState } from "react";

import LanguageSelector from "../../components/LanguageSelector";

export default function RegisterForm() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm_password, setConfirmPassword] = useState("");
  const [native_language, setNativeLanguage] = useState("ja");

  function handleSubmit(e) {
    e.preventDefault();
  }

  return (
    <form method="POST" onSubmit={handleSubmit}>
      <fieldset className="form-group">
        <legend className="border-bottom mb-4">Sign Up</legend>
        <div className="form-group tw-my-2">
          <label className="form-control-label" htmlFor="email">
            Email
          </label>
          <input
            className="form-control form-control-lg"
            id="email"
            name="email"
            onChange={(e) => setEmail(e.target.value)}
            required
            type="email"
            value={email}
          />
        </div>
        <div className="form-group tw-my-2">
          <label className="form-control-label" htmlFor="password">
            Password
          </label>
          <input
            className="form-control form-control-lg"
            id="password"
            name="password"
            onChange={(e) => setPassword(e.target.value)}
            required
            type="password"
            value={password}
          />
        </div>
        <div className="form-group tw-my-2">
          <label className="form-control-label" htmlFor="confirm_password">
            Confirm Password
          </label>
          <input
            className="form-control form-control-lg"
            id="confirm_password"
            name="confirm_password"
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
            type="password"
            value={confirm_password}
          />
        </div>
        <div className="form-group tw-my-2">
          <label className="form-control-label" htmlFor="native_language">
            Native Language
          </label>
          <LanguageSelector
            className="form-control form-control-lg"
            id="native_language"
            name="native_language"
            onChange={(e) => setNativeLanguage(e.target.value)}
            required
            value={native_language}
          />
        </div>
      </fieldset>
      <div className="form-group tw-mt-2 tw-text-right">
        <input
          className="btn btn-outline-info"
          id="submit"
          name="submit"
          type="submit"
          value="Register"
        />
      </div>
    </form>
  );
}
