# Marcelveldt's Hassio Add-ons: Spotweb

## About

Spotweb add-on based on erikdevries/spotweb


## Installation

Note: This addon requires a mysql database. Make sure you have the MariaDB addon running with a database set-up with these options:

database: spotweb
username: spotweb
password: spotweb

1. [Add my Hass.io add-ons repository][repository] to your Hass.io instance.
1. Install the add-on.
1. Click the `Save` button to store your configuration.
1. Start the  add-on.
1. Check the logs of the add-on to see if everything went well.
1. Carefully configure the add-on to your preferences, see the official documentation for for that.


## Configuration

Access the webui at <your-ip>:81

- Spotweb is configured as an open system after running docker-compose up, so everyone who can access can register an account (keep this in mind)
- If you want to use the Spotweb API, create a new user and use the API key associated with that user
- If you would like to save nzb files to disk for (e.g.) SABnzbd to be picked up, the hassio /share folder is mounted in the addon.



[repository]: https://github.com/lbouriez/hassio-addons