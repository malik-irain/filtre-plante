FROM python:3.9-bullseye
WORKDIR /flask-sane-api

# Installing the scanners drivers and sane-utils
COPY epsonscan2_6.7.61.0-1_armhf.deb epsonscan2_6.7.61.0-1_armhf.deb 
COPY epsonscan2-non-free-plugin_1.0.0.6-1_armhf.deb epsonscan2-non-free-plugin_1.0.0.6-1_armhf.deb

RUN apt update
RUN apt install -y sane-utils psmisc
RUN dpkg --install ./epsonscan2_6.7.61.0-1_armhf.deb ./epsonscan2-non-free-plugin_1.0.0.6-1_armhf.deb

# Installing Flask and uwsgi
RUN apt install -y build-essential python3-dev
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY app.py app.py

CMD ["uwsgi",  "--http-timeout",  "3600",  "--harakiri-verbose",  "--harakiri",  "3600", "--socket-timeout", "3600",  "--http", "0.0.0.0:5443", "--master", "-p", "6", "-w", "app:app"]
