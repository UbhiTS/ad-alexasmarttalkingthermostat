import appdaemon.plugins.hass.hassapi as hass
import datetime
#
# Alexa Smart Talking Thermostat App
#
# Args:
#hvac_master_bedroom:
#  module: alexa_smart_talking_thermostat
#  class: AlexaSmartTalkingThermostat
#  thermostat: climate.thermostat_master_bedroom_mode
#  alexa: media_player.master_bedroom_alexa
#  hvac_limits:
#    cooling_min: 67
#    heating_max: 72
#    daily_shutoff: "08:00:00"
#    enforce_fan_auto_mode: True
#  air_recirculation:
#    hour: true
#    half_hour: true
#    quarter_hour: false
#    minute_offset: 0
#    duration: 1
#  doors_windows:
#    - binary_sensor.master_bedroom_door
#    - binary_sensor.master_bedroom_window

class AlexaSmartTalkingThermostat(hass.Hass):

  def initialize(self):
    
    self.thermostat = self.args["thermostat"]
    self.alexa = self.args["alexa"]
    
    self.cooling_min = 45
    self.heating_max = 95
    self.enforce_fan_auto = False
    
    self.recirc_hour = False
    self.recirc_half_hour = False
    self.recirc_quarter_hour = False
    self.recirc_minute_offset = 0
    self.recirc_duration = 0
    self.recirc_frequency = Frequency()
    self.recirc_next_start = None
    self.recirc_in_progress = False
    
    init_log = []
    
    if "hvac_limits" in self.args:
      self.cooling_min = int(self.args["hvac_limits"]["cooling_min"]) if "cooling_min" in self.args["hvac_limits"] else self.cooling_min
      self.heating_max = int(self.args["hvac_limits"]["heating_max"]) if "heating_max" in self.args["hvac_limits"] else self.heating_max
      self.listen_state(self.enforce_temp_limits, self.thermostat, attribute = "temperature")
      self.listen_state(self.enforce_temp_limits, self.thermostat, attribute = "target_temp_high")
      self.listen_state(self.enforce_temp_limits, self.thermostat, attribute = "target_temp_low")
      
      init_log += [f"  TEMP {self.cooling_min}/{self.heating_max}\n"]
      
      if "daily_shutoff" in self.args["hvac_limits"]:
        daily_shut_off = datetime.datetime.strptime(self.args["hvac_limits"]["daily_shutoff"], '%H:%M:%S').time()
        self.run_daily(self.hvac_daily_shut_off, daily_shut_off)
        init_log += [f"  DAILY SHUT OFF {daily_shut_off}\n"]
      
      if "enforce_fan_auto_mode" in self.args["hvac_limits"]:
        self.enforce_fan_auto = bool(self.args["hvac_limits"]["enforce_fan_auto_mode"])
        if self.enforce_fan_auto:
          self.listen_state(self.enforce_fan_auto_mode, self.thermostat, attribute = "fan_mode")
          init_log += [f"  ENFORC FAN AUTO {self.enforce_fan_auto}\n"]

    if "air_recirculation" in self.args:
      self.recirc_hour = bool(self.args["air_recirculation"]["hour"]) if "hour" in self.args["air_recirculation"] else self.recirc_hour
      self.recirc_half_hour = bool(self.args["air_recirculation"]["half_hour"]) if "half_hour" in self.args["air_recirculation"] else self.recirc_half_hour
      self.recirc_quarter_hour = bool(self.args["air_recirculation"]["quarter_hour"]) if "quarter_hour" in self.args["air_recirculation"] else self.recirc_quarter_hour
      self.recirc_minute_offset = int(self.args["air_recirculation"]["minute_offset"]) if "minute_offset" in self.args["air_recirculation"] else self.recirc_minute_offset
      self.recirc_duration = int(self.args["air_recirculation"]["duration"]) if "duration" in self.args["air_recirculation"] else self.recirc_duration
      
      if self.recirc_hour or self.recirc_half_hour or self.recirc_quarter_hour:
        self.recirc_frequency = self.get_frequency()
        self.recirc_next_start = self.get_next_start(self.recirc_frequency) + datetime.timedelta(minutes=self.recirc_minute_offset)
        self.run_every(self.air_cycle, self.recirc_next_start, (60 * self.recirc_frequency.interval))
        init_log += [f"  AIR RECIRCULATE {self.recirc_next_start.strftime('%H:%M')} ({self.recirc_frequency.interval} min)\n"]
         
    doors_windows = 0
    if "doors_windows" in self.args:
      for door_window_sensor in self.args["doors_windows"]:
        self.listen_state(self.open_door_window_hvac_shut_off, door_window_sensor, old = "off", new = "on", duration = 60)
        doors_windows = doors_windows + 1
      init_log += [f"  DOORS/WINDOWS {doors_windows}\n"]
    
    #self.run_daily(self.decrease_heating_temp_after_midnight, datetime.time(2, 0, 0))
    #self.run_daily(self.decrease_heating_temp_after_midnight, datetime.time(3, 0, 0))
    #self.run_daily(self.increase_heating_temp_before_morning, datetime.time(4, 0, 0))
    #self.run_daily(self.increase_heating_temp_before_morning, datetime.time(5, 0, 0))
    
    self.log("\nINIT - ALEXA TALKING THERMOSTAT\n" + "".join(init_log))


  def hvac_daily_shut_off(self, kwargs):
    self.call_service("climate/turn_off", entity_id = self.thermostat)
    self.log("HVAC DAILY SHUT OFF")


  def enforce_fan_auto_mode(self, entity, attribute, old, new, kwargs):
    if new != 'Auto Low' and self.recirc_in_progress == False:
      self.call_service("climate/set_fan_mode", entity_id = self.thermostat, fan_mode = 'Auto Low')
      self.call_service("notify/alexa_media", data = {"type":"tts", "method":"all"}, target = self.alexa, message = "Your attention please. AC fan mode has been set to auto.")
      self.log("ENFORCE FAN MODE AUTO")


  def enforce_temp_limits(self, entity, attribute, old, new, kwargs):
    
    hvac_mode = self.get_state(self.thermostat)
    
    if hvac_mode is None:
      return
    
    if hvac_mode == 'heat':
      temp = self.get_state(self.thermostat, attribute = "temperature")
      if self.heating_max < temp:
        self.call_service("climate/set_temperature", entity_id = self.thermostat, temperature = self.heating_max)
        self.call_service("notify/alexa_media", data = {"type":"tts", "method":"all"}, target = self.alexa, message = f"Your attention please, the maximum heating temperature limit in this room is {str(self.heating_max)}")
        self.log(f"ENFORCED MAX HEATING TEMP LIMIT {str(self.heating_max)}")
        
    if hvac_mode == 'cool':
      temp = self.get_state(self.thermostat, attribute = "temperature")
      if temp < self.cooling_min:
        self.call_service("climate/set_temperature", entity_id = self.thermostat, temperature = self.cooling_min)
        self.call_service("notify/alexa_media", data = {"type":"tts", "method":"all"}, target = self.alexa, message = f"Your attention please, the minimum cooling temperature limit in this room is {str(self.cooling_min)}")
        self.log(f"ENFORCED MIN COOL TEMP LIMIT {str(self.cooling_min)}")
        
    if hvac_mode == 'heat_cool':
      target_temp_high = self.get_state(self.thermostat, attribute = "target_temp_high")
      target_temp_low = self.get_state(self.thermostat, attribute = "target_temp_low")
      
      if target_temp_low < self.cooling_min or self.heating_max < target_temp_high:
        self.call_service("climate/set_temperature", entity_id = self.thermostat, target_temp_low = self.cooling_min, target_temp_high = self.heating_max)
        self.call_service("notify/alexa_media", data = {"type":"tts", "method":"all"}, target = self.alexa, message = f"Your attention please, the temperature range limit in this room is {str(self.cooling_min)} to {str(self.heating_max)}")
        self.log(f"ENFORCED AUTO TEMP LIMIT {str(self.cooling_min)}/{str(self.heating_max)}")


  def open_door_window_hvac_shut_off(self, entity, attribute, old, new, kwargs):
    operation_mode = self.get_state(self.thermostat)
    if operation_mode != 'off':
      self.call_service("climate/turn_off", entity_id = self.thermostat)
      self.call_service("notify/alexa_media", data = {"type":"tts", "method":"all"}, target = self.alexa, message = f"Your attention please, this room's door or window has been open since the past 60 seconds. I've turned off the air conditioning.")
      self.log("DOOR WINDOW SHUT OFF")


  def air_cycle(self, kwargs):
    self.recirc_in_progress = True
    self.call_service("climate/set_fan_mode", entity_id = self.thermostat, fan_mode = 'On Low')
    self.run_in(self.air_cycle_off, (60 * int(self.recirc_duration)) + 5)
    self.log("AIR RECIRCULATE ON")


  def air_cycle_off(self, kwargs):
    self.call_service("climate/set_fan_mode", entity_id = self.thermostat, fan_mode = 'Auto Low')
    self.recirc_in_progress = False
    self.log("AIR RECIRCULATE OFF")


#  def decrease_heating_temp_after_midnight(self, kwargs):
#    temp = self.get_state(self.thermostat_heating, attribute = "temperature")
#    new_temp = temp - 1
#    self.call_service("climate/set_temperature", entity_id = self.thermostat_heating, temperature = new_temp)
#    self.log("AUTO_DECREASE_TEMP") 
  
  
#  def increase_heating_temp_before_morning(self, kwargs):
#    temp = self.get_state(self.thermostat_heating, attribute = "temperature")
#    new_temp = temp + 1
#    self.call_service("climate/set_temperature", entity_id = self.thermostat_heating, temperature = new_temp)
#    self.log("AUTO_INCREASE_TEMP")


  def get_frequency(self):
    
    frequency = Frequency()
    
    if (self.recirc_hour):
      frequency.interval = 60
      frequency.times.append(0)
    
    if (self.recirc_half_hour):
      frequency.interval = 30
      frequency.times.append(0)
      frequency.times.append(30)
      
    if (self.recirc_quarter_hour):
      frequency.interval = 15
      frequency.times.append(0)
      frequency.times.append(15)
      frequency.times.append(30)
      frequency.times.append(45)
    
    frequency.times = set(frequency.times)
    frequency.times = sorted(frequency.times)
    
    return frequency


  def get_next_start(self, frequency):
    
    now = datetime.datetime.now()
    next_start_min = None
    
    for min in frequency.times:
      if now.minute < min:
        next_start_min = min
        break
    
    if next_start_min is None:
      next = now.replace(minute = 0, second = 0) + datetime.timedelta(hours=1)
    else:
      next = now.replace(minute = next_start_min, second = 0)
    
    return next


class Frequency:
  
    def __init__(self):
      
        self.times = []
        self.interval = None
