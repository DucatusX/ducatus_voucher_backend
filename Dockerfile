FROM python:3.7

ENV PYTHONUNBUFFERED=1

RUN mkdir /code
WORKDIR /code

RUN pip install --upgrade pip==20.2.4 && apt-get update && apt-get install -y netcat
COPY requirements.txt /code/requirements.txt
RUN pip install -r requirements.txt

EXPOSE 8000

COPY . /code/