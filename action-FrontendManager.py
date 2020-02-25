#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from hermes_python.hermes import Hermes
from input_handler import InputHandler
from response_decoder import ResponseDecoder

"""Start point for frontend. Subscribe to input from snips and responses from backend."""

MQTT_IP_ADDR = "192.168.0.27"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))

# Confidence thresholds
intent_threshold = 0.7
slot_threshold = 0.7

# Describe which camera located the object
cam_info = False

if __name__ == "__main__":

    # Input handler communicates between Snips and BackendManager
    input_handler = InputHandler(MQTT_IP_ADDR, "InputHandler", intent_threshold, slot_threshold)

    with Hermes(MQTT_ADDR) as h:
        # Send incoming intents from Snips to the user input handler
        print("[FrontendManager] Connecting InputHandler to Snips.")
        h.subscribe_session_ended(input_handler.handle_session_ended) \
         .subscribe_intent_not_recognized(input_handler.handle_not_recognised) \
         .subscribe_intent("code-pig:LocateObject", input_handler.handle_user_input) \
         .subscribe_intent("code-pig:GiveAnswer", input_handler.handle_user_input) \
         .subscribe_intent("code-pig:GiveObject", input_handler.handle_user_input) \
         .subscribe_intent("code-pig:StopSearch", input_handler.handle_user_input) \
         .subscribe_intent("code-pig:InformObject", input_handler.handle_user_input) \
         .subscribe_intent("code-pig:TellJoke", input_handler.handle_user_input) \
         .subscribe_intent("code-pig:SetLights", input_handler.handle_user_input) \
         .subscribe_intent("code-pig:SetVolume", input_handler.handle_user_input) \
         .subscribe_intent("code-pig:BookTickets", input_handler.handle_user_input) \
         .start()
        print("[FrontendManager] InputHandler subscribed to Snips.")

    # ResponseDecoder listens for processed information from the backend, sends output to snips TTS
    response_decoder = ResponseDecoder(MQTT_IP_ADDR, "ResponseDecoder", cam_info)
