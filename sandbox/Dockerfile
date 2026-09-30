FROM python:3.12-slim

RUN pip install --no-cache-dir pytest

RUN useradd -u 10001 -m codelens

USER codelens

WORKDIR /home/codelens