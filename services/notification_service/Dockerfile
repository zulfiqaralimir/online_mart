FROM python:3.12

WORKDIR /code/

RUN apt-get update && apt-get install -y \
build-essential \
libpq-dev \
protobuf-compiler \
&& rm -rf /var/lib/apt/lists/*

COPY . /code/

RUN pip install poetry \
&& poetry config virtualenvs.create false \
&& poetry install

EXPOSE 8034

CMD ["poetry","run","uvicorn","notification_service.main:app","--host","0.0.0.0","--port","8034","--reload"]