FROM andbobsyouruncle/amd64-google-assistant-webserver:0.0.4

# overwite python files
COPY *.py /
COPY client_secrets.json /
COPY run.sh /
RUN chmod a+x /run.sh
ENTRYPOINT [ "/run.sh" ]
