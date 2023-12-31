"""Constants for the SwitchBot Remote IR integration."""
from enum import IntFlag, StrEnum

DOMAIN = "switchbotremote"

CONF_POWER_SENSOR = "power_sensor"
CONF_TEMPERATURE_SENSOR = "temperature_sensor"
CONF_HUMIDITY_SENSOR = "humidity_sensor"
CONF_TEMP_MIN = "temp_min"
CONF_TEMP_MAX = "temp_max"
CONF_TEMP_STEP = "temp_step"
CONF_HVAC_MODES = "hvac_modes"
CONF_CUSTOMIZE_COMMANDS = "customize_commands"
CONF_WITH_SPEED = "with_speed"
CONF_WITH_ION = "with_ion"
CONF_WITH_TIMER = "with_timer"
CONF_WITH_BRIGHTNESS = "with_brightness"
CONF_WITH_TEMPERATURE = "with_temperature"
CONF_ON_COMMAND = "on_command"
CONF_OFF_COMMAND = "off_command"
CONF_OVERRIDE_OFF_COMMAND = "override_off_command"

"""Supported Devices"""
DIY_AIR_CONDITIONER_TYPE = "DIY Air Conditioner"
AIR_CONDITIONER_TYPE = "Air Conditioner"

DIY_FAN_TYPE = "DIY Fan"
FAN_TYPE = "Fan"
DIY_AIR_PURIFIER_TYPE = "DIY Air Purifier"
AIR_PURIFIER_TYPE = "Air Purifier"

DIY_LIGHT_TYPE = "DIY Light"
LIGHT_TYPE = "Light"

DIY_TV_TYPE = "DIY TV"
TV_TYPE = "TV"
DIY_IPTV_TYPE = "DIY IPTV"
IPTV_TYPE = "IPTV"
DIY_DVD_TYPE = "DIY DVD"
DVD_TYPE = "DVD"
DIY_SPEAKER_TYPE = "DIY Speaker"
SPEAKER_TYPE = "Speaker"
DIY_SET_TOP_BOX_TYPE = "DIY Set Top Box"
SET_TOP_BOX_TYPE = "Set Top Box"
DIY_PROJECTOR_TYPE = "DIY Projector"
PROJECTOR_TYPE = "Projector"

DIY_CAMERA_TYPE = "DIY Camera"
CAMERA_TYPE = "Camera"

DIY_VACUUM_CLEANER_TYPE = "DIY Vacuum Cleaner"
VACUUM_CLEANER_TYPE = "Vacuum Cleaner"

DIY_WATER_HEATER_TYPE = "DIY Water Heater"
WATER_HEATER_TYPE = "Water Heater"

OTHERS_TYPE = "Others"

"""IR Classes"""
AIR_CONDITIONER_CLASS = "Air Conditioner"
FAN_CLASS = "Fan"
LIGHT_CLASS = "Light"
MEDIA_CLASS = "Media"
CAMERA_CLASS = "Camera"
VACUUM_CLASS = "Vacuum"
WATER_HEATER_CLASS = "Water Heater"
OTHERS_CLASS = "Others"

"""Class by device type"""
CLASS_BY_TYPE = {
    DIY_AIR_CONDITIONER_TYPE: AIR_CONDITIONER_CLASS,
    AIR_CONDITIONER_TYPE: AIR_CONDITIONER_CLASS,

    DIY_FAN_TYPE: FAN_CLASS,
    FAN_TYPE: FAN_CLASS,
    DIY_AIR_PURIFIER_TYPE: FAN_CLASS,
    AIR_PURIFIER_TYPE: FAN_CLASS,

    DIY_LIGHT_TYPE: LIGHT_CLASS,
    LIGHT_TYPE: LIGHT_CLASS,

    DIY_TV_TYPE: MEDIA_CLASS,
    TV_TYPE: MEDIA_CLASS,
    DIY_IPTV_TYPE: MEDIA_CLASS,
    IPTV_TYPE: MEDIA_CLASS,
    DIY_DVD_TYPE: MEDIA_CLASS,
    DVD_TYPE: MEDIA_CLASS,
    DIY_SPEAKER_TYPE: MEDIA_CLASS,
    SPEAKER_TYPE: MEDIA_CLASS,
    DIY_SET_TOP_BOX_TYPE: MEDIA_CLASS,
    SET_TOP_BOX_TYPE: MEDIA_CLASS,
    DIY_PROJECTOR_TYPE: MEDIA_CLASS,
    PROJECTOR_TYPE: MEDIA_CLASS,

    DIY_CAMERA_TYPE: CAMERA_CLASS,
    CAMERA_TYPE: CAMERA_CLASS,

    DIY_VACUUM_CLEANER_TYPE: VACUUM_CLASS,
    VACUUM_CLEANER_TYPE: VACUUM_CLASS,

    DIY_WATER_HEATER_TYPE: WATER_HEATER_CLASS,
    WATER_HEATER_TYPE: WATER_HEATER_CLASS,

    OTHERS_TYPE: OTHERS_CLASS,
}

"""Climate Types"""
IR_CLIMATE_TYPES = [
    DIY_AIR_CONDITIONER_TYPE,
    AIR_CONDITIONER_TYPE,
]

"""Fan Types"""
IR_FAN_TYPES = [
    DIY_FAN_TYPE,
    FAN_TYPE,
    DIY_AIR_PURIFIER_TYPE,
    AIR_PURIFIER_TYPE,
]

"""Light Types"""
IR_LIGHT_TYPES = [
    DIY_LIGHT_TYPE,
    LIGHT_TYPE,
]

"""Media Types"""
IR_MEDIA_TYPES = [
    DIY_TV_TYPE,
    TV_TYPE,
    DIY_IPTV_TYPE,
    IPTV_TYPE,
    DIY_DVD_TYPE,
    DVD_TYPE,
    DIY_SPEAKER_TYPE,
    SPEAKER_TYPE,
    DIY_SET_TOP_BOX_TYPE,
    SET_TOP_BOX_TYPE,
    DIY_PROJECTOR_TYPE,
    PROJECTOR_TYPE,
]

"""Camera Types"""
IR_CAMERA_TYPES = [
    DIY_CAMERA_TYPE,
    CAMERA_TYPE,
]

"""Vacuum Types"""
IR_VACUUM_TYPES = [
    DIY_VACUUM_CLEANER_TYPE,
    VACUUM_CLEANER_TYPE,
]

"""Water Heater Types"""
IR_WATER_HEATER_TYPES = [
    DIY_WATER_HEATER_TYPE,
    WATER_HEATER_TYPE,
]
