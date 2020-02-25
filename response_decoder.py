from backend_response import BackendResponse
import json
from connection import MQTTConnection
from message_constructor import MessageConstructor
from datetime import datetime


class ResponseDecoder:
    """
    Listens for responses (processed requests) from the backend system and
    constructs messages for output based on the results.
    """
    def __init__(self, broker, name, cam_info):
        print("[ResponseDecoder] Loading response decoder...")
        self.connection = MQTTConnection(broker, name, self.handle_message_received)
        self.connection.con.subscribe("backend/response")
        self.cam_info = cam_info
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
        print("m_decode: " + m_decode)
        assert m_decode is not None, "handle_backend_response m_decode is None"
        out_msg = ""
        message = json.loads(m_decode)
        print("[ResponseDecoder] Loading message from json")
        assert message is not None, "backend response to json did not work?"
        assert message['code_name'].isdigit(), "Response code should be integer"
        assert 0 < int(message['code_name']) <= 6, "Response code should be between 1 and 6"
        print("[ResponseDecoder] Loading response into response object")
        try:
            backend_response = BackendResponse(message['code_name'],
                                               message['original_request'],
                                               message['location_time'],
                                               message['minutes_passed'],
                                               message['locations_identified'])
        except (AttributeError, TypeError):
            raise AssertionError("Backend response busted")

        assert backend_response is not None, "Failed to load BackendResponse object"
        print("[ResponseDecoder] Backend response loaded")
        backend_response.print()

        print("[ResponseDecoder] Checking message code.")
        if backend_response.code_name == '1':
            print("[ResponseDecoder] Received code 1, located single object in current snapshot")
            out_msg += MessageConstructor.single_location_current_snapshot(backend_response, self.cam_info)
        elif backend_response.code_name == '2':
            print("[ResponseDecoder] Received code 2, identified multiple locations in current snapshot")
            out_msg += MessageConstructor.multiple_location_current_snapshot(backend_response, self.cam_info)
        elif backend_response.code_name == '3':
            print("[ResponseDecoder] Received code 3, identified single location in previous snapshot")
            out_msg += MessageConstructor.single_location_previous_snapshot(backend_response, self.cam_info)
        elif backend_response.code_name == '4':
            print("[ResponseDecoder] Received code 4, identified multiple locations in previous snapshot")
            out_msg += MessageConstructor.multiple_location_previous_snapshot(backend_response, self.cam_info)
        elif backend_response.code_name == '5':
            print("[ResponseDecoder] Received code 5, could not locate the object")
            out_msg += MessageConstructor.not_found(backend_response)
        elif backend_response.code_name == '6':
            print("[ResponseDecoder] Received code 6, the system does not recognise that object")
            out_msg += MessageConstructor.unknown_object(backend_response)
        print(out_msg)
        tts = "{\"siteId\": \"default\", \"text\": \"%s\", \"lang\": \"en-GB\"}" % (out_msg)
        print("[ResponseDecoder] Publishing message to TTS: ", out_msg)
        self.connection.con.publish('hermes/tts/say', tts)


if __name__ == "__main__":

    """Unit tests"""

    # rd = ResponseDecoder("192.168.0.27", "rd", True)


    #backend_response = "{\"code_name\": \"1\", \"original_request\": \"bottle\", \"location_time\": \"2020-02-24 19:36:40.357148\", \"minutes_passed\": \"0.63\", \"locations_identified\": [\"{\\\"object\": \\\"bottle\\\", \\\"location\\\": \\\"person\\\"}\\\"]}"
    #backend_response = "{\"code_name\": \"6\", \"original_request\": \"spectacles\", \"location_time\": \"None\", \"minutes_passed\": \"None\", \"locations_identified\": []}"

    # backend_response = {"code_name": "1", "original_request": "cup", "location_time": "2020-02-25 11:20:53.901430", "minutes_passed": "0.03", "locations_identified": ["{\"object\": \"cup\", \"location\": \"person\"}"]}
#    assert backend_response is type(dict), "backend_response is not a dictionary (" + str(type(backend_response)) + ")"

    # rd.handle_backend_response(json.dumps(backend_response))
