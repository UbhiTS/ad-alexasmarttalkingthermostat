# Alexa (& Sonos) Smart Talking Thermostat

Alexa becomes an announcer for your thermostat. Set Temp Limits, Enforce Fan Modes, Daily Shut Off, makes your thermostat Smart ! Please :star: if you like the app :)

Please ⭐ this repo if you like my work and also check out my other repos like
- [Home Assistant 'STEROIDS' Configuration](https://github.com/UbhiTS/ha-config-ataraxis)
- [Alexa (& Sonos) Talking Clock](https://github.com/UbhiTS/ad-alexatalkingclock)
- [Alexa (& Sonos) Doorbell](https://github.com/UbhiTS/ad-alexadoorbell)
- [Alexa (& Sonos) Door/Window Announce](https://github.com/UbhiTS/ad-alexadoorwindowannounce)
- [Alexa (& Sonos) Smart Talking Thermostat](https://github.com/UbhiTS/ad-alexasmarttalkingthermostat)

Also, if you want to see a walkthrough of my Home Assistant configuration, I have my video walkthrough on youtube below
- [Home Automation on 'STEROIDS' : Video Walkthrough](https://youtu.be/qqktLE9_45A)

## Installation
**NEEDS THE [Alexa Media Player](https://github.com/custom-components/alexa_media_player) HACS Integration from Keaton Taylor and Alan Tse**

Use [HACS](https://github.com/custom-components/hacs) or [download](https://github.com/UbhiTS/ad-alexatalkingclock) the `alexa_doorbell` directory from inside the `apps` directory to your local `apps` directory, then add the configuration to enable the `alexa_doorbell` module.

## App Configuration (config/appdaemon/apps/apps.yaml)
```yaml
hvac_master_bedroom:
  module: alexa_smart_talking_thermostat
  class: AlexaSmartTalkingThermostat
  thermostat: climate.thermostat_master_bedroom_mode
  alexa: media_player.master_bedroom_alexa
  hvac_limits:
    cooling_min: 67
    heating_max: 72
    daily_shutoff: "08:00:00"
    enforce_fan_auto_mode: True
  air_recirculation:
    hour: true
    half_hour: true
    quarter_hour: false
    minute_offset: 0
    duration: 1
  doors_windows:
    - binary_sensor.master_bedroom_door
    - binary_sensor.master_bedroom_window
```

key | optional | type | default | description
-- | -- | -- | -- | --
`module` | **False** | string | alexa_door_window_announce | The module name of the app.
`class` | **False** | string | AlexaDoorWindowAnnounce | The name of the Class.
`alexas` | **False** | list |  | The Alexa device(s) to target for the door/window announcements.
`door_windows` | **False** | cover\|binary_sensor |  | The doors/windows to monitor.
`announcements\|start_time` | True | time | 00:00:00 | The time to enable the service. (24h format)
`announcements\|end_time` | True | time | 23:59:59 | The time to disable the service. (24h format)

## Thank you!
This app wouldn't be possible without the amazing work done by the developers and community at **[Home Assistant](https://www.home-assistant.io/)**, and of Keaton Taylor and Alan Tse on their **Alexa Media Player integration** for Home Assistant. *https://github.com/custom-components/alexa_media_player*

Ever since we've set this up in our home, we don't think we can do without it now. Your home suddenly gets a voice, something like Jarvis ... awesome ! 

If you like my work and feel gracious, you can buy me a beer below ;)

<a href="https://www.buymeacoffee.com/ubhits" target="_blank">
<img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png"
     alt="Buy Me A Beer" 
     style="height:41px !important; width:174px !important;" />
</a>

# License
[Apache-2.0](LICENSE). By providing a contribution, you agree the contribution is licensed under Apache-2.0. This is required for Home Assistant contributions.
