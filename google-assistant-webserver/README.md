# Marcelveldt's Hassio Add-ons: Google Assistant Webserver

## About

Webservice for the Google Assistant SDK - mofified version of the original by @AndBobsYourUncle with customizable broadcast command
For my own personal use but maybe some other non-English hassio users can benefit from this too.


## Installation

The installation of this add-on is pretty straightforward and not different in
comparison to installing any other Hass.io add-on.

1. [Add my Hass.io add-ons repository][repository] to your Hass.io instance.
1. Install the "Google Assistant Webserver" add-on.
1. Start the "Google Assistant Webserver" add-on.
1. Check the logs of the add-on to see if everything went well.
1. At the first start, you will need to authenticate with Google, use the "Open Web UI" button for that.
1. Ready to go!

Note: Once authenticated through the Web UI, it's normal that you'll get an error message, ignore that.


## Configuration

**Note**: _Remember to restart the add-on when the configuration is changed._

Example add-on configuration:

```json
{
  "broadcast_cmd": "vertel iedereen"
}
```

**Note**: _This is just an example, don't copy and paste it! Create your own!_

### Option: `broadcast_cmd`

The `broadcast_cmd` option allow you to specify a custom phrase for the broadcast command.
By default (in English) it is "broadcast" but in other languages this will be something else, like "vertel iedereen" (in Dutch).


## Usage in HomeAssistant

Once you've set-up the webserver, you can add the component to HomeAssistant as notify component (for the broadcasts) and as script for the custom actions.

### Broadcast component

```yaml
notify:
  - name: Google Assistant
    platform: rest
    resource: http://[HASS_IP]:5000/broadcast_message
```

### Script component

```yaml

# define as rest_command in configuration
rest_command:
  - google_assistant_command:
      url: 'http://[HASS_IP]:5000/command?message={{ command }}'


# example usage in script
script:
  - google_cmd_test:
      service: rest_command.google_assistant_command
      data:
        command: "some command you want to throw at the assistant"
```





[repository]: https://github.com/lbouriez/hassio-addons