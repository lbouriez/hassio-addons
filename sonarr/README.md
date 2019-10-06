# Marcelveldt's Hassio Add-ons: Sonarr

## About

Sonarr add-on based on the prebuilt docker image from linuxserver

Sonarr (formerly NZBdrone) is a PVR for usenet and bittorrent users. It can monitor multiple RSS feeds for new episodes of your favorite shows and will grab, sort and rename them. It can also be configured to automatically upgrade the quality of files already downloaded when a better quality format becomes available.

## Installation

The installation of this add-on is pretty straightforward and not different in
comparison to installing any other Hass.io add-on.

1. [Add my Hass.io add-ons repository][repository] to your Hass.io instance.
1. Install the add-on.
1. Click the `Save` button to store your configuration.
1. Start the  add-on.
1. Check the logs of the add-on to see if everything went well.
1. Carefully configure the add-on to your preferences, see the official documentation for for that.


## Configuration

Access the webui at <your-ip>:8989, for more information check out https://sonarr.tv/

By default hassio folders backup, share and ssl are available within the addon.
You can use the share folder to access/store your media files.



[repository]: https://github.com/lbouriez/hassio-addons