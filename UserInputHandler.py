from MessageBuilder import MessageBuilder
import time


class UserInputHandler:

    def __init__(self, pclient, intent_threshold=0.7, slot_threshold=0.7, ):
        print("Initialising User Input Handler")
        self.pclient = pclient  # Connection the backend handler
        self.intent_threshold = intent_threshold  # For checking confidence in user input
        self.slot_threshold = slot_threshold
        self.validate_object = None  # Stores the name of the object the system needs to validate
        self.waiting_for_response = False

    def handle_user_input(self, hermes, intent_message):

        # Extract intent information
        session_id = intent_message.session_id
        intent_name = intent_message.intent.intent_name
        intent_confidence = intent_message.intent.confidence_score

        print("Session ID " + str(session_id))
        print("Intent name " + intent_name)
        print("intent confidence " + str(intent_confidence))

        # Validate and handle incoming intents
        if intent_confidence < self.intent_threshold:
            self.handle_poor_intent(hermes, session_id)
        elif intent_name == "code-pig:LocateObject":
            self.handle_locate_object(hermes, intent_message, session_id)
        elif intent_name == "code-pig:ConfirmObject":
            self.handle_confirm_object(hermes, intent_message, session_id)
        elif intent_name == "code-pig:GiveObject":
            self.handle_give_object(hermes, intent_message, session_id)
        else:
            self.handle_bad_intent(hermes, session_id)

    def handle_locate_object(self, hermes, intent_message, session_id):

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
        # Extract the object name and confidence
        slot_value, slot_score = self.extract_slot_info(intent_message.slots.yesno)

        if not slot_value:
            self.handle_bad_intent(hermes, intent_message)
        elif slot_value == "yes":
            self.send_frontend_request(hermes, intent_message, self.validate_object)
        elif slot_value == "no":
            self.handle_negative_confirmation(hermes, session_id)

    def handle_give_object(self, hermes, intent_message, session_id):
        # Extract the object name and confidence
        slot_value, slot_score = self.extract_slot_info(intent_message.slots.item)

        print("Extracted slot")

        if not slot_value:
            self.handle_bad_intent(hermes, intent_message)
        elif slot_score < self.slot_threshold:
            self.handle_poor_object(hermes, session_id, slot_value)
        elif slot_value == "unknownword":
            self.handle_bad_object(hermes, session_id)
        else:
            self.send_frontend_request(hermes, session_id, slot_value)

    def extract_slot_info(self, slot):
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

    def send_frontend_request(self, hermes, session_id, object_name):
        # Send request to backend
        if object_name:
            print("Sending message to controller")
            self.pclient.publish("frontend/request", object_name)
            message = MessageBuilder.search_object(object_name)
            hermes.publish_end_session(session_id, message)
        else:
            hermes.publish_end_session(session_id, "Error")

    def handle_poor_intent(self, hermes, session_id):
        sentence = MessageBuilder.poor_intent()
        hermes.publish_end_session(session_id, sentence)

    def handle_bad_intent(self, hermes, session_id):
        message = MessageBuilder.bad_intent()
        hermes.publish_end_session(session_id, message)

    def handle_no_object(self, hermes, session_id):
        sentence = MessageBuilder.no_object()
        hermes.publish_continue_session(session_id, sentence, ["code-pig:GiveObject"])

    def handle_poor_object(self, hermes, session_id, object_name):
        sentence = MessageBuilder.poor_object(object_name)
        self.validate_object = object_name
        hermes.publish_continue_session(session_id, sentence, ["code-pig:ConfirmObject"])

    def handle_bad_object(self, hermes, session_id):
        sentence = MessageBuilder.bad_object()
        hermes.publish_end_session(session_id, sentence)

    def handle_negative_confirmation(self, hermes, session_id):
        sentence = MessageBuilder.what_object()
        hermes.publish_continue_session(session_id, sentence, ["code-pig:GiveObject"])

    def handle_positive_confirmation(self, hermes, session_id, object_name):
        sentence = MessageBuilder.search_object(object_name)
        self.send_frontend_request(hermes, session_id, object_name)


