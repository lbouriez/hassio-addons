# Hassio Add-ons: TT-RSS

## About

Tt-rss add-on based on the prebuilt docker image from linuxserver

Tt-rss is an open source web-based news feed (RSS/Atom) reader and aggregator, designed to allow you to read news from any location, while feeling as close to a real desktop application as possible.

## Installation

The installation of this add-on is pretty straightforward and not different in
comparison to installing any other Hass.io add-on.

1. [Add my Hass.io add-ons repository](https://github.com/lbouriez/hassio-addons) to your Hass.io instance.
2. Install the add-on.
3. Click the `Save` button to store your configuration.
4. Start the  add-on.
5. Check the logs of the add-on to see if everything went well.
6. Carefully configure the add-on to your preferences, see the official documentation for for that.

## Configuration
Configure the addon with the parameters. You can use the mariadb addon.

1. Install and set your DB (MariaDB addon)
2. Configure the addon
3. Access to your instance on http://HASSIO_IP:32790
4. Enjoy

If you encouter an access right issue, bash into the container and do: `chmod -R 777 /data /var/www/`