# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster
ENV REPOSITORY_LIST_URL=""

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY dockerfile_scanner.py .

ENTRYPOINT python3 dockerfile_scanner.py "${REPOSITORY_LIST_URL}"