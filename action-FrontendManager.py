#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from hermes_python.hermes import Hermes
import paho.mqtt.client as mqtt
from BackendResponse import BackendResponse
from MessageBuilder import MessageBuilder
import json
import time
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



def on_log(client, userdata, level, buf):
    """
    Use for debugging paho client
    """
    print("log: " + buf)


def on_connect(client, userdata, flags, rc):
    """
    Use for debugging the paho client
    """
    if rc == 0:
        print("Connected OK")
    else:
        print("Bad connection, returned code ", rc)


def on_disconnect(client, userdata, flags, rc=0):
    """
    Use for debugging the paho client
    """
    print("Disconnected result code " + str(rc))


def handle_backend_response(client, userdata, msg):
    """
    Paho client (pClient) main callback function, Handles messages from the backend 
    using the paho mqtt client. Listen for messages on the seeker/processed_requests topics
    and use the information to provide an output to the user
    :return: Publish a message to the text to speech engine for the user
    """
    global pClient
    topic = msg.topic
    m_decode = str(msg.payload.decode("utf-8", "ignore"))
    print("Topics recieved ", topic)
    print("Message recieved: ", m_decode)

    global message_builder
    msg = ""

    if topic == "hermes/dialogueManager/sessionEnded":
        print("Handle intent not recognised")
        tts = "{\"siteId\": \"default\", \"text\": \"i dont understand that. please ask again\", \"lang\": \"en_GB\"}"
    if topic == "hermes/dialogueManager/endSession":
        print("Handle topic session ended")
        print(m_decode)
    elif topic == "seeker/processed_requests":
        print("Handle message from backend.")
        message = json.loads(m_decode)
        print("Loaded message from json")
        print(message)
        print("Loading response into response object")
        backend_response = BackendResponse(message['code_name'],
                                           message['original_request'],
                                           message['location_time'],
                                           message['minutes_passed'],
                                           message['locations_identified'])
        print("Backend response loaded")
        backend_response.print()

        print("Checking message code.")
        if backend_response.code_name == '1':
            print("Received code 1, located single object in current snapshot")
            msg = message_builder.single_location_current_snapshot(backend_response)
        elif backend_response.code_name == '2':
            print("Received code 2, identified multiple locations in current snapshot")
            msg = message_builder.multiple_location_current_snapshot(backend_response)
        elif backend_response.code_name == '3':
            print("Received code 3, identified single location in previous snapshot")
            msg = message_builder.single_location_previous_snapshot(backend_response)
        elif backend_response.code_name == '4':
            print("Received code 4, identified multiple locations in previous snapshot")
            msg = message_builder.multiple_location_previous_snapshot(backend_response)
        elif backend_response.code_name == '5':
            print("Received code 5, could not locate the object")
            msg = message_builder.not_found(backend_response)
        elif backend_response.code_name == '6':
            print("Received code 6, the system does not recognise that object")
            msg = message_builder.unknown_object(backend_response)

    tts = "{\"siteId\": \"default\", \"text\": \"%s\", \"lang\": \"en-GB\"}" % (msg)
    pClient.publish('hermes/tts/say', tts)

    def wait_for_response(self, session_id):
        global response_received
        wait = 0
        while not response_received:
            if wait > 10:
                print("The location request timed out")
                msg = "The system is not working, try again later"
                tts = "{\"siteId\": \"default\", \"text\": \"%s\", \"lang\": \"en-GB\"}" % (msg)
                pClient.publish('hermes/tts/say', tts)
                break
            else:
                print("Waiting for backend response")
                time.sleep(1)
                wait += 1


if __name__ == "__main__":

    # print("Loading paho client")
    # print("Action code broker address: " + broker)
    # pClient = mqtt.Client("Frontend")
    # pClient.on_connect = on_connect
    # pClient.on_log = on_log
    # pClient.on_disconnect = on_disconnect
    # pClient.on_message = handle_backend_response
    # pClient.connect(broker)
    # pClient.loop_start()
    # pClient.subscribe("seeker/processed_requests")
    # pClient.subscribe("hermes/nlu/intentNotRecognized")
    # print("Subscribed to backend")

    backend_response_handler = BackendResponseHandler(broker)
    user_input_handler = UserInputHandler(pClient)

    with Hermes(MQTT_ADDR) as h:
        h.subscribe_intents(user_input_handler.handle_user_input).start()
        print("Subscribed to intents")
        print("Hermes mqtt address: " + MQTT_ADDR)
