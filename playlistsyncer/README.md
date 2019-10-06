# Marcelveldt's Hassio Add-ons: Playlistsyncer

## About

This addon/docker image will allow you to sync playlists between several streaming services.
I created this as a personal project but this might come in handy for others too.
Supported streaming services: Spotify, Tidal and Qobuz

## Installation

The installation of this add-on is pretty straightforward and not different in
comparison to installing any other Hass.io add-on.

1. [Add my Hass.io add-ons repository][repository] to your Hass.io instance.
1. Install the "Playlistsyncer" add-on.
1. Carefully configure the add-on to your preference with the options (see below)!
1. Click the `Save` button to store your configuration.
1. Start the "Playlistsyncer" add-on.
1. Check the logs of the add-on to see if everything went well.
1. At startup, a first sync id done immediately, once done it will follow the schedule
1. Ready to go!



## Configuration

**Note**: _Remember to restart the add-on when the configuration is changed._

Example add-on configuration:

```json
{
  "log_level": "INFO",
  "log_file": "/share/playlistsyncer.log",
  "force_full_sync": false,
  "matcher_strictness": 0.9,
  "spotify_username": "myspotifyusername",
  "spotify_password": "myspotifypasswd",
  "tidal_username": "mytidalusername",
  "tidal_password": "mytidalpasswd",
  "qobuz_username": "myqobuzusername",
  "qobuz_password": "myqobuzpasswd",
  "local_music_dir": "/share/music",
  "playlists": [
    {
      "source_provider": "SPOTIFY",
      "source_playlist": "Kids",
      "destination_provider": "ROON",
      "destination_playlist": "",
      "two_way": true,
      "add_library": true
    },
    {
      "source_provider": "SPOTIFY",
      "source_playlist": "Nederlandse Top 40",
      "destination_provider": "QOBUZ",
      "destination_playlist": "",
      "two_way": false,
      "add_library": false
    }
  ]
}
```

**Note**: _This is just an example, don't copy and paste it! Create your own!_

### Option: `log_level`

The `log_level` option controls the level of log output by the addon and can
be changed to be more or less verbose, which might be useful when you are
dealing with an unknown issue. Possible values are:

- `DEBUG`: Shows detailed debug information.
- `INFO`: Normal (usually) interesting events. It's the default choice.
- `WARNING`: Exceptional occurrences that are not errors.
- `ERROR`: Something went terribly wrong. Add-on becomes unusable.

**Note**: _The loglevel is only applied to the logfile, not the console output._

### Option: `log_file`

Full path to the logfile. Root folder can be either /backup or /share. The addon does not have access to other hassio folders.

### Option: `schedule`

Schedule when the backup task should run. By default it's set to every night at 04:00.
You can use CRON syntax for this. http://www.nncron.ru/help/EN/working/cron-format.htm

### Option: `force_full_sync`

Force a full sync (ignore cache) for the next run. By default a full sync if forced every 7 runs.

### Option: `matcher_strictness`

This setting sets the strictness level of the matcher in a range from 0.0 tot 1.
Default setting is 0.9 which can solve small typos but will not match 2 entirely different artists/titles.
Only adjust if you're sure what you're doing.

### Option: `spotify_username`

[OPTIONAL]
Your Spotify username if you have a Spotify account and you want to sync Spotify playlists with this addon.

### Option: `spotify_password`

[OPTIONAL]
Your Spotify password if you have a Spotify account and you want to sync Spotify playlists with this addon.

### Option: `tidal_username`

[OPTIONAL]
Your Tidal username if you have a Tidal account and you want to sync Tidal playlists with this addon.

### Option: `tidal_password`

[OPTIONAL]
Your Tidal password if you have a Tidal account and you want to sync Tidal playlists with this addon.

### Option: `qobuz_username`

[OPTIONAL]
Your Qobuz username if you have a Qobuz account and you want to sync Qobuz playlists with this addon.

### Option: `qobuz_password`

[OPTIONAL]
Your Qobuz password if you have a Qobuz account and you want to sync Qobuz playlists with this addon.

### Option: `local_music_dir`

[OPTIONAL]
When syncing, look in the music dir if the song is found on disk
Advanced feature can be ommitted completely.

### Option: `playlists`

A list with all playlists you want to sync, see options below.

`source_provider`: Where to sync the playlist from. Valid options are TIDAL/QOBUZ/SPOTIFY/ROON
`source_playlist`: The name of the playlist (on the source provider) to sync.
`destination_provider`: Where to sync the playlist to. Valid options are TIDAL/QOBUZ/SPOTIFY/ROON.
`destination_playlist`: The name of the playlist (on the destination provider) to sync to. Use * as wildcard to use the source playlist name.
`two_way`: Also sync the other way around, from destination to source. (bool: true/false)
`add_library`: Tracks that are added to the playlist (and their albums) will also be added to the library of the provider. (bool: true/false)


[repository]: https://github.com/lbouriez/hassio-addons