FROM ubuntu:22.04

RUN apt update && apt install -y python3 python3-pip mysql-client libmysqlclient-dev
EXPOSE 5000

COPY . /flask

WORKDIR /flask

RUN python3 -m pip install -r requirements.txt

CMD ["gunicorn","-w 4","-b 0.0.0.0:5000","app:create_app()"]

