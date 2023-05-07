FROM nginx/unit:1.29.1-python3.11

COPY ./src/core/config.json /docker-entrypoint.d/config.json

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt update && apt install -y python3-pip
RUN pip install --upgrade pip

COPY requirements.txt .
RUN pip install -r requirements.txt

CMD bash -c 'while !</dev/tcp/db/5432; \
 do sleep 1; done; mkdir /usr/local/storage; \
 gunicorn src.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
   --bind 0.0.0.0:8000'