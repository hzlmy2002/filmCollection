FROM ubuntu:22.04

RUN apt update && apt install -y python3 python3-pip mysql-client libmysqlclient-dev
EXPOSE 8000

COPY . /flask


WORKDIR /flask

RUN python3 -m pip install -r requirements.txt

CMD ["python3","app.py"]

