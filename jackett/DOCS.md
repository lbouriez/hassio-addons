# ~~Home Assistant Community Add-on~~ Sonarr

## Installation

The installation of this add-on is pretty straightforward and not different in
comparison to installing any other Home Assistant add-on.

1. Search for the “Sonarr” add-on in the Hass.io 166 add-on store
   and install it.
1. Save the add-on configuration.
1. Start the "Sonarr" add-on.
1. Check the logs of the "Plex Media Server" to see if everything went well.
1. Login to the Sonarr admin interface and complete the setup process.

## Configuration

**Note**: _Remember to restart the add-on when the configuration is changed._

Example add-on configuration:

```yaml
log_level: info
networkdisks:
  - //serverip/share
cifsusername: hassio
cifspassword: password
cifsversion: "3.0"
```

**Note**: _This is just an example, don't copy and paste it! Create your own!_

### Option: `log_level`

The `log_level` option controls the level of log output by the addon and can
be changed to be more or less verbose, which might be useful when you are
dealing with an unknown issue. Possible values are:

- `trace`: Show every detail, like all called internal functions.
- `debug`: Shows detailed debug information.
- `info`: Normal (usually) interesting events.
- `warning`: Exceptional occurrences that are not errors.
- `error`: Runtime errors that do not require immediate action.
- `fatal`: Something went terribly wrong. Add-on becomes unusable.

Please note that each level automatically includes log messages from a
more severe level, e.g., `debug` also shows `info` messages. By default,
the `log_level` is set to `info`, which is the recommended setting unless
you are troubleshooting.

### Option: `networkdisks` 🔴 PROTECTION MODE NEED TO DISABLED TO WORK

Is the list of networks share to mount at boot.
The mounted driver is on `/<SERVER>/<SHARE>` directory.

#### Option: `cifsusername`

The username to use to mount the network shares

#### Option: `cifspassword`

The password used to mount the networks shares

#### Option: `cifsversion`

The version of cifs to use. Default `3.0`.
Valid values are `3.0`, `2.1`, `2.0`, `1.0`.
