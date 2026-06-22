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
CONF_WITH_SWING = "with_swing"
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

# This codes and commands specially the test ones are obtained from:


MEDIA_PLAYER_COMMANDS = {
    TV_TYPE: {
        "basic": {
            "turn_on": {"action": "turnOn", "customize": False},
            "turn_off": {"action": "turnOff", "customize": False},
            "volume_up": {"action": "volumeAdd", "customize": False},
            "volume_down": {"action": "volumeSub", "customize": False},
            "channel_up": {"action": "channelAdd", "customize": False},
            "channel_down": {"action": "channelSub", "customize": False},
            "set_channel": {"action": "SetChannel", "customize": False},
            "mute": {"action": "13", "customize": True, "icon": "mdi:volume-mute"},

        },
        "extra": {
            "menu": {"action": "5", "customize": True, "icon": "mdi:menu"},
            "back": {"action": "39", "customize": True, "icon": "mdi:arrow-left"},
            "select": {"action": "41", "customize": True, "icon": "mdi:check"},
            "cursor_up": {"action": "43", "customize": True, "icon": "mdi:arrow-up"},
            "cursor_down": {"action": "49", "customize": True, "icon": "mdi:arrow-down"},
            "cursor_left": {"action": "45", "customize": True, "icon": "mdi:arrow-left"},
            "cursor_right": {"action": "47", "customize": True, "icon": "mdi:arrow-right"},
            "digit_1": {"action": "15", "customize": True, "icon": "mdi:numeric-1-box"},
            "digit_2": {"action": "17", "customize": True, "icon": "mdi:numeric-2-box"},
            "digit_3": {"action": "19", "customize": True, "icon": "mdi:numeric-3-box"},
            "digit_4": {"action": "21", "customize": True, "icon": "mdi:numeric-4-box"},
            "digit_5": {"action": "23", "customize": True, "icon": "mdi:numeric-5-box"},
            "digit_6": {"action": "25", "customize": True, "icon": "mdi:numeric-6-box"},
            "digit_7": {"action": "27", "customize": True, "icon": "mdi:numeric-7-box"},
            "digit_8": {"action": "29", "customize": True, "icon": "mdi:numeric-8-box"},
            "digit_9": {"action": "31", "customize": True, "icon": "mdi:numeric-9-box"},
            "digit_0": {"action": "35", "customize": True, "icon": "mdi:numeric-0-box"},
            "source_av_tv": {"action": "37", "customize": True, "icon": "mdi:television-classic"},
            "reset": {"action": "33", "customize": True, "icon": "mdi:restart"},
        }
    },
    IPTV_TYPE: {
        "basic": {
            "turn_on": {"action": "turnOn", "customize": False},
            "turn_off": {"action": "turnOff", "customize": False},
            "volume_up": {"action": "volumeAdd", "customize": False},
            "volume_down": {"action": "volumeSub", "customize": False},
            "channel_up": {"action": "channelAdd", "customize": False},
            "channel_down": {"action": "channelSub", "customize": False},
            "set_channel": {"action": "SetChannel", "customize": False},
            "play": {"action": "23", "customize": True},
            "mute": {"action": "3", "customize": True, "icon": "mdi:volume-mute"},

        },
        "extra": {
            "cursor_up": {"action": "13", "customize": True, "icon": "mdi:arrow-up"},
            "cursor_left": {"action": "15", "customize": True, "icon": "mdi:arrow-left"},
            "select": {"action": "17", "customize": True, "icon": "mdi:check"},
            "cursor_right": {"action": "19", "customize": True, "icon": "mdi:arrow-right"},
            "cursor_down": {"action": "21", "customize": True, "icon": "mdi:arrow-down"},
            "back": {"action": "45", "customize": True, "icon": "mdi:arrow-left"},
            "digit_1": {"action": "25", "customize": True, "icon": "mdi:numeric-1-box"},
            "digit_2": {"action": "27", "customize": True, "icon": "mdi:numeric-2-box"},
            "digit_3": {"action": "29", "customize": True, "icon": "mdi:numeric-3-box"},
            "digit_4": {"action": "31", "customize": True, "icon": "mdi:numeric-4-box"},
            "digit_5": {"action": "33", "customize": True, "icon": "mdi:numeric-5-box"},
            "digit_6": {"action": "35", "customize": True, "icon": "mdi:numeric-6-box"},
            "digit_7": {"action": "37", "customize": True, "icon": "mdi:numeric-7-box"},
            "digit_8": {"action": "39", "customize": True, "icon": "mdi:numeric-8-box"},
            "digit_9": {"action": "41", "customize": True, "icon": "mdi:numeric-9-box"},
            "digit_0": {"action": "43", "customize": True, "icon": "mdi:numeric-0-box"},
        }
    },
    SET_TOP_BOX_TYPE: {
        "basic": {
            "turn_on": {"action": "turnOn", "customize": False},
            "turn_off": {"action": "turnOff", "customize": False},
            "volume_up": {"action": "volumeAdd", "customize": False},
            "volume_down": {"action": "volumeSub", "customize": False},
            "channel_up": {"action": "channelAdd", "customize": False},
            "channel_down": {"action": "channelSub", "customize": False},
            "set_channel": {"action": "SetChannel", "customize": False},
        },
        "extra": {
            "standby": {"action": "1", "customize": True, "icon": "mdi:power-standby"},
            "menu": {"action": "45", "customize": True, "icon": "mdi:menu"},
            "back": {"action": "25", "customize": True, "icon": "mdi:arrow-left"},
            "select": {"action": "31", "customize": True, "icon": "mdi:check"},
            "cursor_up": {"action": "27", "customize": True, "icon": "mdi:arrow-up"},
            "cursor_left": {"action": "29", "customize": True, "icon": "mdi:arrow-left"},
            "cursor_right": {"action": "33", "customize": True, "icon": "mdi:arrow-right"},
            "cursor_down": {"action": "35", "customize": True, "icon": "mdi:arrow-down"},
            "guide": {"action": "21", "customize": True, "icon": "mdi:television-guide"},
            "digit_1": {"action": "3", "customize": True, "icon": "mdi:numeric-1-box"},
            "digit_2": {"action": "5", "customize": True, "icon": "mdi:numeric-2-box"},
            "digit_3": {"action": "7", "customize": True, "icon": "mdi:numeric-3-box"},
            "digit_4": {"action": "9", "customize": True, "icon": "mdi:numeric-4-box"},
            "digit_5": {"action": "11", "customize": True, "icon": "mdi:numeric-5-box"},
            "digit_6": {"action": "13", "customize": True, "icon": "mdi:numeric-6-box"},
            "digit_7": {"action": "15", "customize": True, "icon": "mdi:numeric-7-box"},
            "digit_8": {"action": "17", "customize": True, "icon": "mdi:numeric-8-box"},
            "digit_9": {"action": "19", "customize": True, "icon": "mdi:numeric-9-box"},
            "digit_0": {"action": "23", "customize": True, "icon": "mdi:numeric-0-box"},
        }
    },
    DVD_TYPE: {
        "basic": {
            "turn_on": {"action": "turnOn", "customize": False},
            "turn_off": {"action": "turnOff", "customize": False},
            "play": {"action": "Play", "customize": False},
            "pause": {"action": "Pause", "customize": False},
            "stop": {"action": "Stop", "customize": False},
            "next_track": {"action": "Next", "customize": False},
            "previous_track": {"action": "Previous", "customize": False},
            "mute": {"action": "setMute", "customize": False, "icon": "mdi:volume-mute"},

        },
        "extra": {
            "fast_forward": {"action": "FastForward", "customize": False, "icon": "mdi:fast-forward"},
            "rewind": {"action": "Rewind", "customize": False, "icon": "mdi:rewind"},
            "menu": {"action": "35", "customize": True, "icon": "mdi:menu"},
            "back": {"action": "37", "customize": True, "icon": "mdi:arrow-left"},
            "select": {"action": "5", "customize": True, "icon": "mdi:check"},
            "cursor_up": {"action": "3", "customize": True, "icon": "mdi:arrow-up"},
            "cursor_left": {"action": "1", "customize": True, "icon": "mdi:arrow-left"},
            "cursor_right": {"action": "9", "customize": True, "icon": "mdi:arrow-right"},
            "cursor_down": {"action": "7", "customize": True, "icon": "mdi:arrow-down"},
            "title": {"action": "31", "customize": True, "icon": "mdi:format-title"},
            "skip": {"action": "33", "customize": True, "icon": "mdi:skip-forward"},
            "format": {"action": "27", "customize": True, "icon": "mdi:format-align-center"},
        }
    },
    SPEAKER_TYPE: {
        "basic": {
            "turn_on": {"action": "turnOn", "customize": False},
            "turn_off": {"action": "turnOff", "customize": False},
            "play": {"action": "Play", "customize": False},
            "pause": {"action": "Pause", "customize": False},
            "stop": {"action": "Stop", "customize": False},
            "next_track": {"action": "Next", "customize": False},
            "previous_track": {"action": "Previous", "customize": False},
            "volume_up": {"action": "volumeAdd", "customize": False},
            "volume_down": {"action": "volumeSub", "customize": False},
            "mute": {"action": "setMute", "customize": False, "icon": "mdi:volume-mute"},

        },
        "extra": {
            "select": {"action": "5", "customize": True, "icon": "mdi:check"},
            "cursor_up": {"action": "3", "customize": True, "icon": "mdi:arrow-up"},
            "cursor_left": {"action": "1", "customize": True, "icon": "mdi:arrow-left"},
            "cursor_right": {"action": "9", "customize": True, "icon": "mdi:arrow-right"},
            "cursor_down": {"action": "7", "customize": True, "icon": "mdi:arrow-down"},
            "AudioP": {"action": "13", "customize": True, "icon": "mdi:format-title"},
            "AudioM": {"action": "17", "customize": True, "icon": "mdi:format-title"},
            "fast_forward": {"action": "FastForward", "customize": False, "icon": "mdi:fast-forward"},
            "rewind": {"action": "Rewind", "customize": False, "icon": "mdi:rewind"},
            "menu": {"action": "33", "customize": True, "icon": "mdi:menu"},
            "back": {"action": "35", "customize": True, "icon": "mdi:arrow-left"},
        }
    },
    PROJECTOR_TYPE: {
        "basic": {
            "turn_on": {"action": "turnOn", "customize": False},
            "turn_off": {"action": "turnOff", "customize": False},
            "play": {"action": "21", "customize": True},  # Assuming Select as play/pause toggle
            "pause": {"action": "21", "customize": True},
            "volume_up": {"action": "33", "customize": True},
            "volume_down": {"action": "35", "customize": True},
            "mute": {"action": "37", "customize": True, "icon": "mdi:volume-mute"},

        },
        "extra": {
            "source_computer": {"action": "5", "customize": True, "icon": "mdi:laptop"}, # Not working on test device
            "source_video": {"action": "7", "customize": True, "icon": "mdi:video"}, # Not working on test device
            "source_signal": {"action": "9", "customize": True, "icon": "mdi:signal"}, # Not working on test device
            "menu": {"action": "19", "customize": True, "icon": "mdi:menu"},
            "select": {"action": "21", "customize": True, "icon": "mdi:check"},
            "cursor_up": {"action": "23", "customize": True, "icon": "mdi:arrow-up"},
            "cursor_left": {"action": "25", "customize": True, "icon": "mdi:arrow-left"},
            "cursor_right": {"action": "27", "customize": True, "icon": "mdi:arrow-right"},
            "cursor_down": {"action": "29", "customize": True, "icon": "mdi:arrow-down"},
            "exit": {"action": "31", "customize": True, "icon": "mdi:exit-to-app"},
            "auto": {"action": "39", "customize": True, "icon": "mdi:auto-fix"}, # Not working on test device
            "focus_in": {"action": "11", "customize": True, "icon": "mdi:magnify-plus"}, # Not working on test device
            "focus_out": {"action": "13", "customize": True, "icon": "mdi:magnify-minus"}, # Not working on test device
            "picture_up": {"action": "15", "customize": True, "icon": "mdi:image-plus"}, # Not working on test device
            "picture_down": {"action": "17", "customize": True, "icon": "mdi:image-minus"}, # Not working on test device
            "mode": {"action": "43", "customize": True, "icon": "mdi:projector-screen"}, # Not working on test device
            # pause": {"action": "41", "customize": True},Assuming PJT_Pause as play/pause toggle # Not working on test device
        }
    }
}