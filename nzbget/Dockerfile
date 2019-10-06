FROM linuxserver/nzbget

# MOFIFY DATA PATH
RUN sed -i "s|/config|/data|g" /etc/services.d/nzbget/run
RUN sed -i "s|/config|/data|g" /etc/cont-init.d/30-config

VOLUME [ "/data" ]