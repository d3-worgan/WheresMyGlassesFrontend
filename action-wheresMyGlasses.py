#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from hermes_python.hermes import Hermes
import paho.mqtt.client as mqtt
from BackendResponse import BackendResponse
from MessageBuilder import MessageBuilder
import json
import time

MQTT_IP_ADDR = "localhost"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))
broker = "192.168.0.27"

response_received = False
be_response = None
message_builder = MessageBuilder()

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


def on_message(client, userdata, msg):
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

    if topic == "hermes/nlu/intentNotRecognized":
        print("Handle intent not recognised")
        tts = "{\"siteId\": \"default\", \"text\": \"i dont understand that. please ask again\", \"lang\": \"en_GB\"}"
    elif topic == "seeker/processed_requests":
        print("Handle message from backend.")
        message = json.loads(m_decode)
        print("Loaded message from json")
        print(message)
        print("Loading response into response object")
        backend_response = BackendResponse(message['code_name'], message['original_request'], message['location_time'], message['locations_identified'])
        print("Backend response loaded")
        backend_response.print()

        print("Checking message code.")
        if backend_response.code_name == '1':
            print("Received code 1, located single object in current snapshot")
            msg = message_builder.single_location_current_snapshot(backend_response)
        elif backend_response.code_name == '2':
            print("Recieved code 2, identified multiple locations in current snapshot")
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


def intent_received(hermes, intent_message):
    """
    Manages communication from the user
    """
    # Extract intent information
    session_id = intent_message.session_id
    intent_name = intent_message.intent.intent_name
    intent_confidence = intent_message.intent.confidence_score
    slot_value = None
    slot_score = None

    print("Session ID " + str(session_id))
    print("Intent name " + intent_name)
    print("intent confidence " + str(intent_confidence))

    search_object = True

    sentence = ''

    # Validate intent confidence
    if search_object:
        if intent_confidence < 0.80:
            sentence += MessageBuilder.poor_intent()
            search_object = False

    # Validate correct intent
    if search_object:
        if intent_name != 'code-pig:LocateObject':
            sentence += MessageBuilder.bad_intent()

    # Validate an object was given
    if search_object:
        if not intent_message.slots.home_object:
            sentence += MessageBuilder.no_object()
            search_object = False

    # Extract the object name and confidence
    if search_object:
        if intent_message.slots.home_object.first().value is not None:
            slot_value = intent_message.slots.home_object.first().value
            slot_score = 0
            print("Slot value " + slot_value)
            for slot in intent_message.slots.home_object:
                slot_score = slot.confidence_score
            print("Slot score ", str(slot_score))

    # Validate heard the object correctly
    if search_object:
        if slot_score < 0.80:
            sentence += MessageBuilder.poor_object(slot_value)
            search_object = False

    # Handle unknown objects
    if search_object:
        if slot_value == "unknownword":
            sentence += MessageBuilder.bad_object()

    # Send request to backend
    if search_object:
        global pClient
        pClient.publish("voice_assistant/user_requests", slot_value)
        sentence += MessageBuilder.search_object(slot_value)
        hermes.publish_end_session(session_id, sentence)
    else:
        hermes.publish_end_session(session_id, sentence)


def wait_for_response(hermes, session_id):
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

    print("Loading paho client")
    pClient = mqtt.Client("Frontend")
    pClient.on_connect = on_connect
    pClient.on_log = on_log
    pClient.on_disconnect = on_disconnect
    pClient.on_message = on_message
    pClient.connect(broker)
    pClient.loop_start()
    pClient.subscribe("seeker/processed_requests")
    pClient.subscribe("hermes/nlu/intentNotRecognized")
    print("Subscribed to backend")

    print("Loading hermes")
    with Hermes(MQTT_ADDR) as h:
        h.subscribe_intents(intent_received).start()
        print("Subscribed to intents")