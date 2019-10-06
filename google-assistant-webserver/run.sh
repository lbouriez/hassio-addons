#!/bin/bash
set -e

CONFIG_PATH=/data/options.json
CLIENT_JSON=/client_secrets.json
CRED_JSON=/data/cred.json
BROADCAST_CMD=$(jq --raw-output '.broadcast_cmd' $CONFIG_PATH)

if [ ! -f "$CRED_JSON" ] && [ -f "$CLIENT_JSON" ]; then
    echo "[Info] Start WebUI for handling oauth2"
    python3 /hassio_oauth.py "$CLIENT_JSON" "$CRED_JSON"
elif [ ! -f "$CRED_JSON" ]; then
    echo "[Error] You need initialize GoogleAssistant with a client secret json!"
    exit 1
fi

exec python3 /hassio_gassistant.py "$CRED_JSON" "$BROADCAST_CMD" > /proc/1/fd/1 2>/proc/1/fd/2