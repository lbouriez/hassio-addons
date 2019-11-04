FROM linuxserver/tt-rss

# MOFIFY DATA PATH
RUN sed -i "s|/config|/data|g" /etc/services.d/nginx/run
RUN sed -i "s|/config|/data|g" /config/nginx/nginx.conf

VOLUME [ "/data" ]