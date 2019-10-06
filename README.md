# hassio-addons
Repository of custom addons for hass.io


## [Inadyn][addon-inadyn]

### About

Inadyn is a small and simple Dynamic DNS, DDNS, client with HTTPS support. Commonly available in many GNU/Linux distributions, used in off the shelf routers and Internet gateways to automate the task of keeping your Internet name in sync with your public IP address.

### This Hass.io Addon

The objective is to provide a client to do dynamic dns updates on behalf of your hass.io server. The configuration of this addon allows you to setup your provider to dynamically update whenever a change of your public IP address occurs.

### Configuration

The available configuration options are as follows (this is filled in with some example data):

```
{
  "verify_address": false,
  "fake_address": false,
  "allow_ipv6": true,
  "iface": "eth0",
  "iterations": 0,
  "period": 300,
  "forced_update": false,
  "secure_ssl": true,
  "providers": [
    {
      "provider": "providerslug",
      "custom_provider": false,
      "username": "yourusername",
      "password": "yourpassword_or_token",
      "ssl": true,
      "hostname": "dynamic-subdomain.example.com",
      "checkip_ssl": false,
      "checkip_server": "api.example.com",
      "checkip_command": "/sbin/ifconfig eth0 | grep 'inet6 addr'",
      "checkip_path": "/",
      "user_agent": "Mozilla/5.0",
      "ddns_server": "ddns.example.com",
      "ddns_path": "",
      "append_myip": false
    }
  ]
}
```

You should not fill in all of these, only use what is necessary. A typical example would look like:

```
{
    {
      "provider": "duckdns",
      "username": "your-token",
      "hostname": "sub.duckdns.org"
    }
  ]
}
```

or:

```
{
  "providers": [
    {
      "provider": "someprovider",
      "username": "username",
      "password": "password",
      "hostname": "your.domain.com"
    }
  ]
}
```

for a custom provider that is not supported by inadyn you can do:
```
{
  "providers": [
    {
      "provider": "arbitraryname",
      "username": "username",
      "password": "password",
      "hostname": "your.domain.com",
      "ddns_server": "api.cp.easydns.com",
      "ddns_path": "/somescript.php?hostname=%h&myip=%i",
      "custom_provider": true
    }
  ]
}
```

the tokens in ddns_path are outlined in the `inadyn.conf(5)` man page.


---




## [Google Assistant Webserver][addon-google-assistant-webserver]

Webservice for the Google Assistant SDK - mofified version of the original by @AndBobsYourUncle with customizable broadcast command For my own personal use but maybe some other non-English hassio users can benefit from this too.


## [NZBget][addon-nzbget]

Nzbget is a usenet downloader, written in C++ and designed with performance in mind to achieve maximum download speed by using very little system resources.


## [Playlistsyncer][addon-playlistsyncer]

This addon/docker image will allow you to sync playlists between several streaming services. I created this as a personal project but this might come in handy for others too. Supported streaming services: Spotify, Tidal and Qobuz Special: Also supports Roon (www.roonlabs.com) media software for syncing playlists.


## [Radarr][addon-radarr]

A fork of Sonarr to work with movies à la Couchpotato.


## [Sonarr][addon-sonarr]

Sonarr (formerly NZBdrone) is a PVR for usenet and bittorrent users. It can monitor multiple RSS feeds for new episodes of your favorite shows and will grab, sort and rename them. It can also be configured to automatically upgrade the quality of files already downloaded when a better quality format becomes available.


## [Roon][addon-roon]

Roon Core Server (www.roonlabs.com) - The core manages your music collection from many sources, and builds an interconnected digital library using enhanced information from Roon.


## [Spotweb][addon-spotweb]

Spotweb add-on based on the docker image erikdevries/spotweb
