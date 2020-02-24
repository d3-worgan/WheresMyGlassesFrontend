#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from hermes_python.hermes import Hermes
from UserInputHandler import UserInputHandler
from BackendResponseHandler import BackendResponseHandler

MQTT_IP_ADDR = "192.168.0.27"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))

intent_threshold = 0.7
slot_threshold = 0.7

validate_object = None

if __name__ == "__main__":

    # Launch the backend handler to communicate between the backend and the user interface
    backend_response_handler = BackendResponseHandler(MQTT_IP_ADDR)

    # Launch the user interface (Snips)
    user_input_handler = UserInputHandler(backend_response_handler.pClient, intent_threshold, slot_threshold)

    with Hermes(MQTT_ADDR) as h:
        # Send incoming intents from Snips to the user input handler
        h.subscribe_intents(user_input_handler.handle_user_input).start()
        print("Subscribed to intents")
        print("Hermes MQTT address: " + MQTT_ADDR)
