FROM python:3.10-slim-bullseye

ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt-get install --no-install-recommends -y bash nano mc
RUN mkdir /src
WORKDIR /src
COPY . /src/

RUN pip install -r requirements.txt
RUN exec python manage.py collectstatic --settings=ancients.settings.docker --noinput
CMD exec gunicorn ancients.wsgi:application --bind 0.0.0.0:8000 --workers 3

# build the image like this:
# docker build -t ancients:latest .

# run the container from 'shared', like this:
# docker run -d --name ancients --mount type=bind,source=$HOME/shared,target=/shared -p 8007:8000 --restart always ancients:latest

# log into the container
# docker exec -it ancients bash