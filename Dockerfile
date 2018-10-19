FROM python:3.6.6-alpine3.7

ENV PYTHONUNBUFFERED 1

# install necessary libraries
RUN apk add --no-cache \
    bash \
    ca-certificates \
    python3-dev \
    && rm /bin/sh \
    && ln -s /bin/bash /bin/sh

WORKDIR /bluebell
ADD . /bluebell

# install project
RUN pip install -e .

EXPOSE 8000
