from BackendResponse import BackendResponse
import paho.mqtt.client as mqtt
import json
import time
from MessageBuilder import MessageBuilder

class BackendResponseHandler:

    def __init__(self, broker):
        print("Loading paho client")
        print("Action code broker address: " + broker)
        self.pClient = mqtt.Client("Frontend")
        self.pClient.on_connect = self.on_connect
        self.pClient.on_log = self.on_log
        self.pClient.on_disconnect = self.on_disconnect
        self.pClient.on_message = self.handle_message_received
        self.pClient.connect(broker)
        self.pClient.loop_start()
        self.pClient.subscribe("backend/response")
        self.pClient.subscribe("hermes/nlu/intentNotRecognized")
        self.pClient.subscribe("frontend/request")
        print("Subscribed to backend")

        self.cam = True  # Give information about which camera seen each object

        self.waiting = False
        #self.wait_for_response()

    def handle_message_received(self, client, userdata, msg):
        """
        Process incoming messages from the frontend and backend
        """
        topic = msg.topic
        m_decode = str(msg.payload.decode("utf-8", "ignore"))
        print("Topics received ", topic)
        print("Message received: ", m_decode)

        if topic == "hermes/nlu/intentNotRecognized":
            print("Handling intent not recognised...")
        elif topic == "frontend/request":
            self.handle_frontend_request(m_decode)
        elif topic == "backend/response":
            print("Handling backend response...")
            self.handle_backend_response(m_decode)

    def handle_frontend_request(self, m_decode):
        """
        Pass on the frontend's request and start waiting for a response.
        :param m_decode:
        :return:
        """
        print("Handle frontend request")
        self.pClient.publish('backend_handler/frontend_request', m_decode)
        #self.waiting = True
        #self.wait_for_response()

    def wait_for_response(self):
        """
        Wait for the backend to respond with an answer to the frontend request. If no
        answer in 3 seconds, keep the user informed. If no answer in 10 seconds, then
        tell the user there is a problem and stop waiting.
        :return:
        """
        wait = 0
        while True:
            if self.waiting:
                while self.waiting:
                    if wait > 10:
                        print("The location request timed out")
                        msg = "The cameras did not respond. maybe try ask me again"
                        tts = "{\"siteId\": \"default\", \"text\": \"%s\", \"lang\": \"en-GB\"}" % (msg)
                        self.pClient.publish('hermes/tts/say', tts)
                        self.waiting = False
                        break
                    else:
                        print("Waiting for backend response")
                        time.sleep(1)
                        wait += 1

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
            out_msg += MessageBuilder.single_location_current_snapshot(backend_response, self.cam)
        elif backend_response.code_name == '2':
            print("Received code 2, identified multiple locations in current snapshot")
            out_msg += MessageBuilder.multiple_location_current_snapshot(backend_response, self.cam)
        elif backend_response.code_name == '3':
            print("Received code 3, identified single location in previous snapshot")
            out_msg += MessageBuilder.single_location_previous_snapshot(backend_response, self.cam)
            print(out_msg)
        elif backend_response.code_name == '4':
            print("Received code 4, identified multiple locations in previous snapshot")
            out_msg += MessageBuilder.multiple_location_previous_snapshot(backend_response, self.cam)
        elif backend_response.code_name == '5':
            print("Received code 5, could not locate the object")
            out_msg += MessageBuilder.not_found(backend_response)
        elif backend_response.code_name == '6':
            print("Received code 6, the system does not recognise that object")
            out_msg += MessageBuilder.unknown_object(backend_response)
            print(out_msg)

        tts = "{\"siteId\": \"default\", \"text\": \"%s\", \"lang\": \"en-GB\"}" % (out_msg)
        print("Publishing message to TTS: ", out_msg)
        self.pClient.publish('hermes/tts/say', tts)

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
