FROM lunik1/tt-rss:latest

# MOFIFY DATA PATH
RUN sed -i "s|/config|/data|g" /etc/services.d/update-feeds/run
RUN sed -i "s|/config|/data|g" /etc/cont-init.d/19-newdefault
RUN sed -i "s|/config/|/data/|g" /etc/cont-init.d/30-config

RUN sed -i "s|/config|/data|g" /defaults/default
RUN sed -i "s|/config|/data|g" /defaults/default.incontainer

VOLUME [ "/data" ]

RUN chmod -R 777 /data /var/www/
