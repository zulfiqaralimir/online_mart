FROM python:3.12

LABEL maintainer="mmrhaqyt@gmail"

WORKDIR /code/

# RUN apt-get update && apt-get install -y \
# build-essential \
# libpq-dev \
# protobuf-compiler \
# && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y protobuf-compiler

COPY . /code/

RUN pip install poetry \
&& poetry config virtualenvs.create false \
&& poetry install

EXPOSE 8000

CMD ["poetry","run","uvicorn","product_db.main:app","--host","0.0.0.0","--reload"]