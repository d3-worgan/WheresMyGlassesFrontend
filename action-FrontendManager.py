#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from hermes_python.hermes import Hermes
from MessageBuilder import MessageBuilder
from UserInputHandler import UserInputHandler
from BackendResponseHandler import BackendResponseHandler

MQTT_IP_ADDR = "192.168.0.27"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))
broker = "192.168.0.27"

response_received = False
sent_request = False
be_response = None
message_builder = MessageBuilder()
intent_threshold = 0.7
slot_threshold = 0.7

validate_object = None

if __name__ == "__main__":
    backend_response_handler = BackendResponseHandler(broker)
    user_input_handler = UserInputHandler(backend_response_handler.pClient)

    with Hermes(MQTT_ADDR) as h:
        h.subscribe_intents(user_input_handler.handle_user_input).start()
        print("Subscribed to intents")
        print("Hermes mqtt address: " + MQTT_ADDR)
