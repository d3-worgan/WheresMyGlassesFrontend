from backend_response import BackendResponse
import json
from connection import MQTTConnection
from message_constructor import MessageConstructor


class ResponseDecoder:
    """
    Listens for responses (processed requests) from the backend system and
    constructs messages for output based on the results.
    """
    def __init__(self, broker, name):
        print("[ResponseDecoder] Loading response decoder...")
        self.connection = MQTTConnection(broker, name, self.handle_message_received)
        self.connection.pClient.subscribe("backend/response")
        print("[ResponseDecoder] Done.")

    def handle_message_received(self, client, userdata, msg):
        """
        Process incoming messages from the backend
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
        Decodes and extracts information from the backend response. Builds an output
        message using the message constructor before sending to the TTS
        :param m_decode:
        :return:
        """
        print("Ballbags")
        print("m_decode: " + m_decode)
        assert m_decode is not None, "handle_backend_response m_decode is None"
        out_msg = ""
        message = json.loads(m_decode)
        print("[ResponseDecoder] Loading message from json")
        assert message is not None, "backend response to json did not work?"
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
            out_msg += MessageConstructor.single_location_current_snapshot(backend_response, self.cam)
        elif backend_response.code_name == '2':
            print("[ResponseDecoder] Received code 2, identified multiple locations in current snapshot")
            out_msg += MessageConstructor.multiple_location_current_snapshot(backend_response, self.cam)
        elif backend_response.code_name == '3':
            print("[ResponseDecoder] Received code 3, identified single location in previous snapshot")
            out_msg += MessageConstructor.single_location_previous_snapshot(backend_response, self.cam)
            print(out_msg)
        elif backend_response.code_name == '4':
            print("[ResponseDecoder] Received code 4, identified multiple locations in previous snapshot")
            out_msg += MessageConstructor.multiple_location_previous_snapshot(backend_response, self.cam)
        elif backend_response.code_name == '5':
            print("[ResponseDecoder] Received code 5, could not locate the object")
            out_msg += MessageConstructor.not_found(backend_response)
        elif backend_response.code_name == '6':
            print("[ResponseDecoder] Received code 6, the system does not recognise that object")
            out_msg += MessageConstructor.unknown_object(backend_response)

        print("[ResponseDecoder] Message for TTS: " + out_msg)
        tts = "{\"siteId\": \"default\", \"text\": \"%s\", \"lang\": \"en-GB\"}" % (out_msg)
        print("[ResponseDecoder] Publishing message to TTS: ", out_msg)
        self.connection.pClient.publish('hermes/tts/say', tts)
