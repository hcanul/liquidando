# Dockerfile
FROM python:3.6-stretch

RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt-get install -y python-pip python-dev build-essential
WORKDIR /app
COPY . /app
RUN pip --no-cache install -r requirements.txt
RUN chmod 644 app.py
CMD [ "python3", "app.py" ]