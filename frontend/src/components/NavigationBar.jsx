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

import { useAuth } from "../features/authentication/useAuth";
import { useLogout } from "../features/authentication/useLogout";

export default function NavigationBar() {
  const { isAuthenticated, isLoading: isAuthenticationLoading } = useAuth();
  const { logout, isLoading: isLogoutLoading } = useLogout();

  return (
    <header className="site-header">
      <nav className="navbar navbar-expand-md navbar-dark bg-dark">
        <div className="container">
          <Link className="navbar-brand mr-4" to="/">
            Human Evaluation Tool
          </Link>
          <button
            className="navbar-toggler"
            type="button"
            data-toggle="collapse"
            data-target="#navbarToggle"
            aria-controls="navbarToggle"
            aria-expanded="false"
            aria-label="Toggle navigation"
          >
            <span className="navbar-toggler-icon"></span>
          </button>
          <div className="collapse navbar-collapse" id="navbarToggle">
            {!isAuthenticationLoading ? (
              !isAuthenticated ? (
                <>
                  <div className="navbar-nav mr-auto">
                    <Link className="nav-item nav-link" to="/about">
                      About
                    </Link>
                  </div>
                  <div className="navbar-nav">
                    <Link className="nav-item nav-link" to="/login">
                      Login
                    </Link>
                  </div>
                </>
              ) : (
                <>
                  <div className="navbar-nav mr-auto">
                    <Link className="nav-item nav-link" to="/about">
                      About
                    </Link>
                  </div>
                  <div className="navbar-nav">
                    <Link className="nav-item nav-link" to="/evaluations">
                      Evaluations
                    </Link>
                  </div>
                  <div className="navbar-nav">
                    <Link className="nav-item nav-link" to="/annotate">
                      Annotate
                    </Link>
                  </div>
                  <div className="navbar-nav">
                    <button
                      className="nav-item nav-link"
                      disabled={isLogoutLoading}
                      onClick={logout}
                    >
                      Logout
                    </button>
                  </div>
                </>
              )
            ) : null}
          </div>
        </div>
      </nav>
    </header>
  );
}
