#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from hermes_python.hermes import Hermes
from modules.input_handler import InputHandler
from modules.response_decoder import ResponseDecoder

"""Start point for frontend. Subscribe to input from snips and responses from backend."""

MQTT_IP_ADDR = "192.168.0.27"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))

intents = ["code-pig:LocateObject", "code-pig:GiveAnswer", "code-pig:GiveObject", "code-pig:StopSearch",
           "code-pig:InformObject", "code-pig:TellJoke", "code-pig:SetLights", "code-pig:SetVolume",
           "code-pig:BookTickets"]

# Confidence thresholds
intent_threshold = 0.7
slot_threshold = 0.7

# Describe which camera located the object
cam_info = True


if __name__ == "__main__":

    # ResponseDecoder listens for processed information from the backend, sends output to snips TTS
    response_decoder = ResponseDecoder(MQTT_IP_ADDR, "ResponseDecoder", cam_info)

    # Input handler communicates between Snips and BackendManager
    input_handler = InputHandler(MQTT_IP_ADDR, "InputHandler", intents, intent_threshold, slot_threshold)

    with Hermes(MQTT_ADDR) as h:
        # Send incoming intents from Snips to the user input handler
        print("[FrontendManager] Connecting InputHandler to Snips.")
        h.subscribe_session_ended(input_handler.handle_session_ended) \
         .subscribe_session_started(input_handler.handle_session_started) \
         .subscribe_intent_not_recognized(input_handler.handle_not_recognised) \
         .subscribe_intent(intents[0], input_handler.handle_user_input) \
         .subscribe_intent(intents[1], input_handler.handle_user_input) \
         .subscribe_intent(intents[2], input_handler.handle_user_input) \
         .subscribe_intent(intents[3], input_handler.handle_user_input) \
         .subscribe_intent(intents[4], input_handler.handle_user_input) \
         .subscribe_intent(intents[5], input_handler.handle_user_input) \
         .subscribe_intent(intents[6], input_handler.handle_user_input) \
         .subscribe_intent(intents[7], input_handler.handle_user_input) \
         .subscribe_intent(intents[8], input_handler.handle_user_input) \
         .start()
        print("[FrontendManager] InputHandler subscribed to Snips.")
