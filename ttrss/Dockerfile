FROM linuxserver/tt-rss

# MOFIFY DATA PATH
RUN sed -i "s|/config|/data|g" /etc/services.d/nginx/run
RUN sed -i "s|/config|/data|g" /etc/cont-init.d/19-newdefault
RUN sed -i "s|/config|/data|g" /etc/cont-init.d/30-config

VOLUME [ "/data" ]