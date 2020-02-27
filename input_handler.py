from message_constructor import MessageConstructor
from connection import MQTTConnection


class InputHandler:
    """
    Listens and processes intents / user input from snips.
    Sends valid requests to the backend system over MQTT
    """

    def __init__(self, broker, name, intents, intent_threshold=0.7, slot_threshold=0.7):
        print("[InputHandler] Initialising user input handler")
        self.connection = MQTTConnection(broker, name)  # So we can publish to the backend
        self.intents = intents
        self.intent_threshold = intent_threshold  # For checking confidence in user input
        self.slot_threshold = slot_threshold
        print("[InputHandler] Input handler loaded.")

    def handle_session_started(self, hermes, message):
        print("[InputHandler] A session started")
        session_id = message.session_id
        print("[InputHandler] Session ID: " + str(session_id))
        #hermes.publish_end_session(session_id, "")
        #hermes.publish_continue_session(session_id, "Hi, how can I help", [], send_intent_not_recognized=True)
        # hermes.publish_end_session(session_id, "")
        # hermes.publish_start_session_action("default", "Hi, how can i help", self.intents, True, True, None)

    def handle_session_ended(self, hermes, message):
        """
        Process incoming messages from the backend
        """
        print("The session ended!")
        session_id = message.session_id
        print("[InputHandler] Session ID: " + str(session_id))
        custom_data = message.custom_data
        print("[InputHandler] Session ID: " + str(custom_data))
        site_id = message.site_id
        print("[InputHandler] Session ID: " + str(site_id))
        termination = message.termination
        print("[InputHandler] Termination message: " + str(dir(termination)))
        print("[InputHandler] Termination data: " + str(termination.data))
        print("[InputHandler] Termination type: " + str(termination.termination_type))
        #print(message.termination)

    def handle_not_recognised(self, hermes, message):
        print("[Input Handler] Not recognised!!!!")

    def handle_user_input(self, hermes, intent_message):
        """
        Decodes and validates incoming intents
        :param hermes:
        :param intent_message:
        :return:
        """

        # Extract intent information
        session_id = intent_message.session_id
        intent_name = intent_message.intent.intent_name
        intent_confidence = intent_message.intent.confidence_score

        print("[InputHandler] Session ID " + str(session_id))
        print("[InputHandler] Intent name " + intent_name)
        print("[InputHandler] intent confidence " + str(intent_confidence))

        # Validate and handle incoming intents
        if intent_confidence < self.intent_threshold:
            print("[InputHandler] Poor intent confidence")
            if intent_name == "code-pig:StopSearch":
                print("[InputHandler] User wants to stop the search")
                self.handle_stop_search(hermes, session_id)
            else:
                self.handle_poor_intent(hermes, session_id)
        elif intent_name == "code-pig:LocateObject":
            self.handle_locate_object(hermes, intent_message, session_id)
        elif intent_name == "code-pig:ConfirmObject":
            self.handle_confirm_object(hermes, intent_message, session_id)
        elif intent_name == "code-pig:GiveObject":
            self.handle_give_object(hermes, intent_message, session_id)
        elif intent_name == "code-pig:StopSearch":
            self.handle_stop_search(hermes, session_id)
        else:
            self.handle_bad_intent(hermes, session_id)

    def handle_locate_object(self, hermes, intent_message, session_id):
        """
        Handles the LocateObject intent and sends requests to the backend
        :param hermes:
        :param intent_message:
        :param session_id:
        :return:
        """
        # Extract the object name and confidence
        slot_value, slot_score = self.extract_slot_info(intent_message.slots.home_object)

        # Validate the slot info
        if not slot_value:
            self.handle_no_object(hermes, session_id)
        elif slot_score < self.slot_threshold:
            self.handle_poor_object(hermes, session_id, slot_value)
        elif slot_value == "unknownword":
            self.handle_bad_object(hermes, session_id)
        else:
            self.send_frontend_request(hermes, session_id, slot_value)

    def handle_confirm_object(self, hermes, intent_message, session_id):
        """
        Handles the ConfirmObject Intent when validating user input
        :param hermes:
        :param intent_message:
        :param session_id:
        :return:
        """
        # Extract the object name and confidence
        slot_value, slot_score = self.extract_slot_info(intent_message.slots.yesno)

        if not slot_value:
            self.handle_bad_intent(hermes, intent_message)
        elif slot_value == "yes":
            self.send_frontend_request(hermes, session_id, self.validate_object)
        elif slot_value == "no":
            self.handle_negative_confirmation(hermes, session_id)
        elif slot_value == "maybe":
            self.send_frontend_request(hermes, session_id, self.validate_object)
        else:
            self.handle_stop_search(hermes, session_id)
        """Add handler for maybe's or escape commands"""

    def handle_give_object(self, hermes, intent_message, session_id):
        """
        Handles the GiveObject intent when validating user input
        :param hermes:
        :param intent_message:
        :param session_id:
        :return:
        """
        # Extract the object name and confidence
        slot_value, slot_score = self.extract_slot_info(intent_message.slots.item)

        print("[InputHandler] Extracted slot")

        if not slot_value:
            self.handle_bad_intent(hermes, intent_message)
        elif slot_score < 0.6:
            self.handle_poor_object(hermes, session_id, slot_value)
        elif slot_value == "unknownword":
            self.handle_bad_object(hermes, session_id)
        elif slot_value == "nothing":
            self.handle_stop_search(hermes, session_id)
        else:
            self.send_frontend_request(hermes, session_id, slot_value)

    def extract_slot_info(self, slot):
        """
        Pulls slots out of the intent message to be processed
        :param slot:
        :return:
        """
        # Extract the object name and confidence
        if slot:
            print("[InputHandler] Extracting slot info")
            slot_value = slot.first().value
            slot_score = 0
            print("[InputHandler] Slot value " + slot_value)
            for slots in slot:
                slot_score = slots.confidence_score
            print("[InputHandler] Slot score ", str(slot_score))
            return slot_value, slot_score
        else:
            print("[InputHandler] No slot to extract")
            return None, None

    def send_frontend_request(self, hermes, session_id, object_name):
        """
        Trigger a search for an object by sending the users specified object to the
        backend system
        :param hermes:
        :param session_id:
        :param object_name:
        :return:
        """
        # Send request to backend
        if object_name:
            print("[InputHandler] Sending request to backend")
            self.connection.con.publish("frontend/request", object_name)
            message = MessageConstructor.search_object(object_name)
            hermes.publish_end_session(session_id, message)
        else:
            hermes.publish_end_session(session_id, "Error")

    def handle_poor_intent(self, hermes, session_id):
        """When an intents confidence is too low"""
        sentence = MessageConstructor.poor_intent()
        hermes.publish_end_session(session_id, sentence)

    def handle_bad_intent(self, hermes, session_id):
        """When an intent is not "LocateObject" """
        message = MessageConstructor.bad_intent()
        hermes.publish_end_session(session_id, message)

    def handle_no_object(self, hermes, session_id):
        """When the user did not specify an object or the system did not hear it"""
        sentence = MessageConstructor.no_object()
        hermes.publish_continue_session(session_id, sentence, ["code-pig:GiveObject", "code-pig:StopSearch", "code-pig:InformObject", "code-pig:SetVolume", "code-pig:BookTickets", "code-pig:SetLights", "code-pig:TellJoke"], send_intent_not_recognized=True)

    def handle_poor_object(self, hermes, session_id, object_name):
        """When the system is not sure it heard the object correctly"""
        sentence = MessageConstructor.poor_object(object_name)
        self.validate_object = object_name
        hermes.publish_continue_session(session_id, sentence, ["code-pig:GiveObject", "code-pig:StopSearch", "code-pig:InformObject", "code-pig:SetVolume", "code-pig:BookTickets", "code-pig:SetLights", "code-pig:TellJoke"], send_intent_not_recognized=True)

    def handle_bad_object(self, hermes, session_id):
        """When the user is specifying an object that system doesnt recognise"""
        sentence = MessageConstructor.bad_object()
        hermes.publish_end_session(session_id, sentence)

    def handle_negative_confirmation(self, hermes, session_id):
        """When the user informs the system that wasnt the object they wanted to search for"""
        sentence = MessageConstructor.what_object()
        hermes.publish_continue_session(session_id, sentence, ["code-pig:GiveObject", "code-pig:StopSearch", "code-pig:InformObject", "code-pig:SetVolume", "code-pig:BookTickets", "code-pig:SetLights", "code-pig:TellJoke"], send_intent_not_recognized=True)

    def handle_positive_confirmation(self, hermes, session_id, object_name):
        """The user confirms the system heard their request properly"""
        sentence = MessageConstructor.search_object(object_name)
        self.send_frontend_request(hermes, session_id, object_name)

    def handle_stop_search(self, hermes, session_id):
        """When the user does not want to search for an object or end the search"""
        print("[InputHandler] Stopping the search")
        sentence = MessageConstructor.stop_search()
        print("[InputHandler] " + sentence)
        hermes.publish_end_session(session_id, sentence)
