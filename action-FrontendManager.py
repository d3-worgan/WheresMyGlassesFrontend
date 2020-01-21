#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from hermes_python.hermes import Hermes
import paho.mqtt.client as mqtt
from BackendResponse import BackendResponse
from MessageBuilder import MessageBuilder
import json
import time

MQTT_IP_ADDR = "192.168.1.2"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))
broker = "192.168.0.27"

response_received = False
sent_request = False
be_response = None
message_builder = MessageBuilder()

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


def handle_user_input(hermes, intent_message):

    # Extract intent information
    session_id = intent_message.session_id
    intent_name = intent_message.intent.intent_name
    intent_confidence = intent_message.intent.confidence_score

    print("Session ID " + str(session_id))
    print("Intent name " + intent_name)
    print("intent confidence " + str(intent_confidence))

    if intent_confidence < 0.80:
        handle_poor_intent(hermes, intent_message, session_id)
    elif intent_name == "code-pig:LocateObject":
        handle_locate_object(hermes, intent_message, session_id)
    elif intent_name == "code-pig:ConfirmObject":
        handle_confirm_object(hermes, intent_message, session_id)
    elif intent_name == "code-pig:GiveObject":
        handle_give_object(hermes, intent_message, session_id)
    else:
        handle_bad_intent(hermes, intent_message, session_id)


def handle_locate_object(hermes, intent_message, session_id):

    # Extract the object name and confidence
    slot_value, slot_score = extract_slot_info(intent_message.slots.home_object)

    # Validate the slot info
    if not slot_value:
        handle_no_object(hermes, session_id)
    elif slot_score < 0.80:
        handle_poor_object(hermes, session_id, slot_value)
    elif slot_value == "unknownword":
        handle_bad_object(hermes, session_id)
    else:
        send_frontend_request(hermes, session_id, slot_value)


def handle_confirm_object(hermes, intent_message, session_id):
    # Extract the object name and confidence
    slot_value, slot_score = extract_slot_info(intent_message.slots.yesno)

    if not slot_value:
        handle_bad_intent(hermes, intent_message, session_id)
    elif slot_value == "yes":
        send_frontend_request(hermes, intent_message, validate_object)
    elif slot_value == "no":
        handle_negative_confirmation(hermes, session_id)


def handle_give_object(hermes, intent_message, session_id):
    # Extract the object name and confidence
    slot_value, slot_score = extract_slot_info(intent_message.slots.item)

    print("Extracted slot")

    if not slot_value:
        handle_bad_intent(hermes, intent_message, session_id)
    elif slot_score < 0.80:
        handle_poor_object(hermes, session_id, slot_value)
    elif slot_value == "unknownword":
        handle_bad_object(hermes, session_id)
    else:
        send_frontend_request(hermes, session_id, slot_value)


def extract_slot_info(slot):
    # Extract the object name and confidence
    if slot:
        print("Extracting slot info")
        slot_value = slot.first().value
        slot_score = 0
        print("Slot value " + slot_value)
        for slots in slot:
            slot_score = slots.confidence_score
        print("Slot score ", str(slot_score))
        return slot_value, slot_score
    else:
        print("No slot to extract")
        return None, None


def send_frontend_request(hermes, session_id, object_name):
    # Send request to backend
    if object_name:
        global pClient
        pClient.publish("voice_assistant/user_requests", object_name)
        message = MessageBuilder.search_object(object_name)
        hermes.publish_end_session(session_id, message)
    else:
        hermes.publish_end_session(session_id, "Error")


def handle_poor_intent(hermes, intent_message, session_id):
    sentence = MessageBuilder.poor_intent()
    hermes.publish_end_session(session_id, sentence)


def handle_bad_intent(hermes, intent_message, session_id):
    message = MessageBuilder.bad_intent()
    hermes.publish_end_session(session_id, message)


def handle_no_object(hermes, session_id):
    sentence = MessageBuilder.no_object()
    hermes.publish_end_session(session_id, sentence, ["code-pig:GiveObject"])


def handle_poor_object(hermes, session_id, object_name):
    sentence = MessageBuilder.poor_object(object_name)
    hermes.publish_continue_session(session_id, sentence, ["code-pig:ConfirmObject"])


def handle_bad_object(hermes, session_id):
    sentence = MessageBuilder.bad_object()
    hermes.publish_end_session(session_id, sentence)


def handle_negative_confirmation(hermes, session_id):
    sentence = MessageBuilder.what_object()
    hermes.publish_continue_session(session_id, sentence, ["code-pig:GiveObject"])


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
    print("Action code broker address: " + broker)
    pClient = mqtt.Client("Frontend")
    pClient.on_connect = on_connect
    pClient.on_log = on_log
    pClient.on_disconnect = on_disconnect
    pClient.on_message = handle_backend_response
    pClient.connect(broker)
    pClient.loop_start()
    pClient.subscribe("seeker/processed_requests")
    pClient.subscribe("hermes/nlu/intentNotRecognized")
    print("Subscribed to backend")

    print("Loading hermes")
    with Hermes(MQTT_ADDR) as h:
        h.subscribe_intents(handle_user_input).start()
        print("Subscribed to intents")
        print("Hermes mqtt address: " + MQTT_ADDR)
