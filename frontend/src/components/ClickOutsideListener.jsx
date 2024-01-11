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

import { createRef, PureComponent } from "react";

export default class ClickOutsideListener extends PureComponent {
  constructor(props) {
    super(props);
    this.containerRef = createRef();
    this.handleClickOutside = this.handleClickOutside.bind(this);
    this.handleClickOutsideListener =
      this.handleClickOutsideListener.bind(this);
  }

  componentDidMount() {
    this.handleClickOutsideListener(this.props.enabled);
  }

  componentDidUpdate(prevProps) {
    if (prevProps.enabled !== this.props.enabled) {
      this.handleClickOutsideListener(this.props.enabled);
    }
  }

  componentWillUnmount() {
    this.handleClickOutsideListener(false);
  }

  handleClickOutside(e) {
    if (!this.containerRef?.current?.contains(e.target)) {
      this.props.onClickOutside(e);
    }
  }

  handleClickOutsideListener(listen) {
    const body = document.querySelector("body");
    if (!body) return;

    if (listen) {
      body.addEventListener("mousedown", this.handleClickOutside);
    } else {
      body.removeEventListener("mousedown", this.handleClickOutside);
    }
  }

  render() {
    return (
      <div ref={this.containerRef} className={this.props.className ?? ""}>
        {this.props.children}
      </div>
    );
  }
}
