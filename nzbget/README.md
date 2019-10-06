# Marcelveldt's Hassio Add-ons: Nzbget

## About

Nzbget add-on based on the prebuilt docker image from linuxserver.
Nzbget is a usenet downloader, written in C++ and designed with performance in mind to achieve maximum download speed by using very little system resources.

## Installation

The installation of this add-on is pretty straightforward and not different in
comparison to installing any other Hass.io add-on.

1. [Add my Hass.io add-ons repository][repository] to your Hass.io instance.
1. Install this add-on.
1. Click the `Save` button to store your configuration.
1. Start the add-on.
1. Check the logs of the add-on to see if everything went well.
1. Carefully configure the add-on to your preferences, see the official documentation for for that.



## Configuration

Webui can be found at <your-ip>:6789 and the default login details (change ASAP) are

`login`:nzbget, `password`:tegbzn6789

By default hassio folders backup, share and ssl are available within nzbget.
You can use the share folder to access your media files.

[repository]: https://github.com/lbouriez/hassio-addons