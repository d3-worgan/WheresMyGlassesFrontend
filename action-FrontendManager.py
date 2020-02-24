#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from hermes_python.hermes import Hermes
from input_handler import InputHandler
from response_decoder import ResponseDecoder

MQTT_IP_ADDR = "192.168.0.27"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))

intent_threshold = 0.7
slot_threshold = 0.7

validate_object = None

if __name__ == "__main__":

    # Launch the backend handler to communicate between the backend and the user interface
    response_decoder = ResponseDecoder(MQTT_IP_ADDR, "ResponseDecoder")

    # Launch the user interface (Snips)
    input_handler = InputHandler(MQTT_IP_ADDR, "InputHandler", intent_threshold, slot_threshold)

    with Hermes(MQTT_ADDR) as h:
        # Send incoming intents from Snips to the user input handler
        h.subscribe_intents(input_handler.handle_user_input).start()
        print("[FrontendManager] Subscribed to intents")
        print("[FrontendManager] Hermes MQTT address: " + MQTT_ADDR)
