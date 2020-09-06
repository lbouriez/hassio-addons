#!/bin/bash
echo "-------------------------------------------------------"
echo "| Ring Device Integration via MQTT                    |"
echo "| Addon for Hass.io                                   |"
echo "|                                                     |"
echo "| Report issues at:                                   |"
echo "| https://github.com/tsightler/ring-mqtt-hassio-addon |"
echo "-------------------------------------------------------"
echo ring-mqtt.js version $(cat /ring-mqtt/package.json | grep version | cut -f4 -d'"')
echo Node version $(node -v)
echo NPM version $(npm -v)
git --version
cd ring-mqtt
echo "-------------------------------------------------------"
echo "Running \"npm audit fix\" to update packages with any vulnerabilities..."
npm audit fix
echo "-------------------------------------------------------"
echo Running ring-mqtt...
chmod +x ring-mqtt.js
DEBUG=ring-mqtt HASSADDON=true exec /ring-mqtt/ring-mqtt.js
