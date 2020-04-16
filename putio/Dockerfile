FROM python:slim-buster

RUN pip install --upgrade pip && \
    pip install --no-cache-dir pandas termcolor imdbpy

ADD putio.py /usr/local/sbin/

CMD ["/usr/local/sbin/putio.py"]
ENTRYPOINT ["python"]

ARG BUILD_ARCH
ARG BUILD_DATE
ARG BUILD_REF
ARG BUILD_VERSION

LABEL \
    io.hass.arch="${BUILD_ARCH}" \
    io.hass.type="addon" \
    io.hass.version=${BUILD_VERSION} \
    maintainer="Jerem <jerem.eskenazi@gmail.com>" \
    org.label-schema.description="Put.io movie cleanup" \
    org.label-schema.build-date=${BUILD_DATE} \
    org.label-schema.name="Hass.io put.io add-on for ${BUILD_ARCH}" \
    org.label-schema.schema-version="1.0" \
    org.label-schema.url="https://addons.community" \
    org.label-schema.vcs-ref=${BUILD_REF} \
    org.label-schema.vendor="Jerem Eskenazi' Hass.io Addons"
