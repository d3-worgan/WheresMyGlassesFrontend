from backend_response import BackendResponse
import paho.mqtt.client as mqtt
import json
import time
from message_constructor import MessageContructor


class ResponseDecoder:

    def __init__(self, broker):
        print("[ResponseDecoder] Loading paho client")
        print("[ResponseDecoder] Action code broker address: " + broker)
        self.pClient = mqtt.Client("Frontend")
        self.pClient.on_connect = self.on_connect
        self.pClient.on_log = self.on_log
        self.pClient.on_disconnect = self.on_disconnect
        self.pClient.on_message = self.handle_message_received
        self.pClient.connect(broker)
        self.pClient.loop_start()
        self.pClient.subscribe("backend/response")
        print("[ResponseDecoder] Subscribed to backend")

    def handle_message_received(self, client, userdata, msg):
        """
        Process incoming messages from the frontend and backend
        """
        topic = msg.topic
        m_decode = str(msg.payload.decode("utf-8", "ignore"))
        print("[ResponseDecoder] Topics received ", topic)
        print("[ResponseDecoder] Message received: ", m_decode)

        if topic == "backend/response":
            print("[ResponseDecoder] Handling backend response...")
            self.handle_backend_response(m_decode)

    def handle_backend_response(self, m_decode):
        """
        Decode the backend response and extract the information. Rebuild the response
        and send the corresponding output message to the frontend TTS engine.
        :param m_decode:
        :return:
        """
        #self.waiting = False
        out_msg = ""
        message = json.loads(m_decode)
        print("[ResponseDecoder] " + message)
        print("[ResponseDecoder] Loaded message from json")
        print("[ResponseDecoder] " + message)
        print("[ResponseDecoder] Loading response into response object")
        backend_response = BackendResponse(message['code_name'],
                                           message['original_request'],
                                           message['location_time'],
                                           message['minutes_passed'],
                                           message['locations_identified'])
        print("[ResponseDecoder] Backend response loaded")
        backend_response.print()

        print("[ResponseDecoder] Checking message code.")
        if backend_response.code_name == '1':
            print("[ResponseDecoder] Received code 1, located single object in current snapshot")
            out_msg += MessageContructor.single_location_current_snapshot(backend_response, self.cam)
        elif backend_response.code_name == '2':
            print("[ResponseDecoder] Received code 2, identified multiple locations in current snapshot")
            out_msg += MessageContructor.multiple_location_current_snapshot(backend_response, self.cam)
        elif backend_response.code_name == '3':
            print("[ResponseDecoder] Received code 3, identified single location in previous snapshot")
            out_msg += MessageContructor.single_location_previous_snapshot(backend_response, self.cam)
            print(out_msg)
        elif backend_response.code_name == '4':
            print("[ResponseDecoder] Received code 4, identified multiple locations in previous snapshot")
            out_msg += MessageContructor.multiple_location_previous_snapshot(backend_response, self.cam)
        elif backend_response.code_name == '5':
            print("[ResponseDecoder] Received code 5, could not locate the object")
            out_msg += MessageContructor.not_found(backend_response)
        elif backend_response.code_name == '6':
            print("[ResponseDecoder] Received code 6, the system does not recognise that object")
            out_msg += MessageContructor.unknown_object(backend_response)

        print("[ResponseDecoder] Message for TTS: " + out_msg)
        tts = "{\"siteId\": \"default\", \"text\": \"%s\", \"lang\": \"en-GB\"}" % (out_msg)
        print("[ResponseDecoder] Publishing message to TTS: ", out_msg)
        self.pClient.publish('hermes/tts/say', tts)

    def on_log(client, userdata, level, buf):
        """
        Use for debugging paho client
        """
        print("[ResponseDecoder] log: " + buf)

    def on_connect(client, userdata, flags, rc):
        """
        Use for debugging the paho client
        """
        if rc == 0:
            print("[ResponseDecoder] Connected OK")
        else:
            print("[ResponseDecoder] Bad connection, returned code ", rc)

    def on_disconnect(client, userdata, flags, rc=0):
        """
        Use for debugging the paho client
        """
        print("[ResponseDecoder] Disconnected result code " + str(rc))
