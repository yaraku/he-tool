# Copyright (C) 2023 Yaraku, Inc.
#
# This file is part of Human Evaluation Tool.
#
# Human Evaluation Tool is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# Human Evaluation Tool is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# Human Evaluation Tool. If not, see <https://www.gnu.org/licenses/>.
#
# Written by Giovanni G. De Giacomo <giovanni@yaraku.com>, September 2023

# Stage 1: Compile the frontend
FROM node:18.17.0 AS frontend

# 1. Set working directory and copy files to container 
WORKDIR /root
COPY frontend                       /root/frontend

# 2. Compile the tool's frontend
WORKDIR /root/frontend
RUN npm install
RUN npm run build

# Stage 2: Execute the backend
FROM python:3.10-slim-bullseye

# 1. Install required system packages
ARG DEBIAN_FRONTEND=noninteractive
ENV PIP_DEFAULT_TIMEOUT 500
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PIP_NO_CACHE_DIR 1
RUN apt update                                            \
    && apt install -y build-essential libpq-dev
RUN pip install poetry

# 2. Set working directory and copy files to container
WORKDIR /root
COPY backend                        /root/backend
COPY --from=frontend /root/public   /root/public
WORKDIR /root/backend

# 3. Install Python package
ENV POETRY_VIRTUALENVS_CREATE 0
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONFAULTHANDLER 1
ENV PYTHONHASHSEED random
RUN poetry install --no-dev --no-interaction --no-ansi    \
    && rm -rf ~/.cache

# 4. Expose the required ports
EXPOSE 8000

# 5. Execute the microservice using gunicorn.
ENV WORKERS 1
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:8000 -w $WORKERS human_evaluation_tool:app"]
