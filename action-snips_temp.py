#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
from hermes_python.hermes import Hermes
from hermes_python.ffi.utils import MqttOptions
from hermes_python.ontology import *
import io


CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"

class SnipsConfigParser(configparser.SafeConfigParser):
    def to_dict(self):
        return {section : {option_name : option for option_name, option in self.items(section)} for section in self.sections()}


def read_configuration_file(configuration_file):
    try:
        with io.open(configuration_file, encoding=CONFIGURATION_ENCODING_FORMAT) as f:
            conf_parser = SnipsConfigParser()
            conf_parser.readfp(f)
            return conf_parser.to_dict()
    except (IOError, configparser.Error) as e:
        return dict()

    
def msg_cpu_temp(hermes, intentMessage):
    conf = read_configuration_file(CONFIG_INI)

    f = open("/sys/class/thermal/thermal_zone0/temp", "r")
    t = f.readline (2)

    if len(intentMessage.slots.house_room) > 0:
        house_room = intentMessage.slots.house_room.first().value  # We extract the value from the slot "house_room"
        result_sentence = "Das Licht wird in {} angeschaltet".format(
            str(house_room))  # The response that will be said out loud by the TTS engine.
    else:
        result_sentence = "Die CPU hat "+t+" Grad"

    current_session_id = intentMessage.session_id
    hermes.publish_end_session(current_session_id, result_sentence)

if __name__ == "__main__":
    mqtt_opts = MqttOptions()
    with Hermes(mqtt_options=mqtt_opts) as h:
        h.subscribe_intent("cetax:cpu_temp", msg_cpu_temp)
        h.start()
