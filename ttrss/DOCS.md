# Hassio Add-ons: TT-RSS

## About

Tt-rss add-on based on the prebuilt docker image from linuxserver

Tt-rss is an open source web-based news feed (RSS/Atom) reader and aggregator.
It is designed to allow you to read news from any location,
while feeling as close to a real desktop application.

## Installation

The installation of this add-on is pretty straightforward and not different in
comparison to installing any other Hass.io add-on.

1. [Add my Hass.io add-ons repo](https://github.com/lbouriez/hassio-addons)
1. Install the add-on.
1. Click the `Save` button to store your configuration.
1. Start the add-on.
1. Check the logs of the add-on to see if everything went well.
1. Carefully configure the add-on to your preferences

## Configuration

Configure the addon with the parameters. You can use the mariadb addon.

1. Install and set your DB (MariaDB addon)
1. Configure the addon
1. Access to your instance on [http://HASSIO_IP:32790](http://HASSIO_IP:32790)
1. Enjoy

If you encouter an access right issue, access the container using bash and do:
`chmod -R 777 /var/www/`

## Backup

This plugin use Mysql to store the data, make sure to backup your database
