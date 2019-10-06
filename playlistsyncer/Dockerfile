FROM python:3-alpine3.9

# install deps
RUN apk --no-cache add taglib-dev gcc g++ flac jq
RUN pip install --upgrade spotipy pytaglib simplejson requests spotipy

# copy files and crontab
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY app /usr/src/app
RUN chmod a+x /usr/src/app/run.sh

VOLUME ["/data"]

CMD ["/usr/src/app/run.sh"]