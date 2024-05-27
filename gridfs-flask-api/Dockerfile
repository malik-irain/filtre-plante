FROM python:3.9-bullseye
WORKDIR /gridfs-sane-api

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY app.py app.py

CMD ["uwsgi",  "--http-timeout",  "3600",  "--harakiri-verbose",  "--harakiri",  "3600", "--socket-timeout", "3600",  "--http", "0.0.0.0:61210", "--master", "-p", "6", "-w", "app:app"]
