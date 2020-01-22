from BackendResponse import BackendResponse

class MessageBuilder:
    """
    Class containing a number of output messages that can be sent to the text to speech engine
    """
    def __init__(self):
        print("Loading message builder...")

    @staticmethod
    def single_location_current_snapshot(br):
        """
        Construct a message to handle communication code 1
        :return: A string describing the location of an object in the current snapshot
        """
        if br.original_request[-1] == "s":
            message = "I just seen some %s by a %s" % (br.locations_identified[0].object, br.locations_identified[0].location)
        else:
            message = "I just seen a %s by a %s" % (br.locations_identified[0].object, br.locations_identified[0].location)
        print(message)
        return message

    @staticmethod
    def multiple_location_current_snapshot(br):
        """
        Contruct a message to handle communication code 2
        :return: A string describing the locations of the the object in the current snapshot
        """
        message = ""
        if br.original_request[-1] == "s":
            message += "I can see some %s in %s locations. There is one by a %s.." % (br.locations_identified[0].object, str(len(br.locations_identified)), br.locations_identified[0].location)
            for location in br.locations_identified[1:]:
                message += "and some more by a %s.." % (location.location)
        else:
            message = "I can see a %s in %s locations. There is one by a %s.." % (br.locations_identified[0].object, str(len(br.locations_identified)), br.locations_identified[0].location)
            for location in br.locations_identified[1:]:
                message += "and another by a %s.." % (location.location)
        print(message)
        return message

    @staticmethod
    def single_location_previous_snapshot(br):
        """
        Construct a message to handle communication code 3
        :return: A string describing the time and location of the object in a previous snapshot
        """
        print("Single location previous snapshot")
        message = ""
        if br.original_request[-1] == "s":
            message += "I seen some %s by a %s." % (br.locations_identified[0].object, br.locations_identified[0].location)
        else:
            message += "I seen a %s by a %s." % (br.locations_identified[0].object, br.locations_identified[0].location)

        if float(br.location_time_passed) <= 60.0:
            message += "That was %s minutes ago" % (round(float(br.location_time_passed), 0))
        elif float(br.location_time_passed) > 60.0:
            message += "That was at %s" % (br.location_time[11:16])

        return message

    @staticmethod
    def multiple_location_previous_snapshot(br):
        """
        Construct a message to handle communication code 4
        :return: A string describing the time and locations of an object in a previous snapshot 
        """
        if br.original_request[-1] == "s":
            message = "I seen some %s in %s locations. There is some by a %s.." % (br.locations_identified[0].object, str(len(br.locations_identified)), br.locations_identified[0].location)
            for location in br.locations_identified[1:]:
                message += "and some more by a %s." % (location.location)
        else:
            message = "I seen a %s in %s locations. There is one by a %s.." % (br.locations_identified[0].object, str(len(br.locations_identified)), br.locations_identified[0].location)
            for location in br.locations_identified[1:]:
                message += "and another by a %s." % (location.location)

        if float(br.location_time_passed) <= 60.0:
            message += " That was %s minutes ago" % (round(float(br.location_time_passed), 0))
        elif float(br.location_time_passed) > 60.0:
            message += " That was at %s" % (br.location_time[11:16])

        print(message)
        return message

    @staticmethod
    def not_found(br):
        """
        Construct a message to handle communication 5
        :return: A string informing that the specified object was not found
        """
        if br.original_request[-1] == "s":
            message = "I have not seen any %s, maybe I can help with something else" % (br.original_request)
        else:
            message = "I have not seen a %s, maybe I can help with something else" % (br.original_request)
        print(message)
        return message

    @staticmethod
    def unknown_object(br):
        """
        Construct a message to handle communication code 6
        :return: A string explaining that the specified object is not in the list of recognised objects
        """
        message = "i am not trained to search for %s, but maybe I can help you find something else" % (br.original_request)
        print(message)
        return message

    @staticmethod
    def poor_intent():
        message = "i do not think I heard that correctly, please ask again"
        return message

    @staticmethod
    def bad_intent():
        message = "i did not understand that, i might be able to help you find something"
        return message

    @staticmethod
    def no_object():
        message = "sorry. did you say you want to search for something. please tell me what you want to search for"
        return message

    @staticmethod
    def poor_object(name):
        message = "sorry. i did not hear that properly. did you want to look for %s" % (name)
        return message

    @staticmethod
    def bad_object():
        message = "i do not think I can help with the object, please ask again"
        return message

    @staticmethod
    def system_error():
        message = "there is a problem with the system."
        return message

    @staticmethod
    def search_object(name):
        #message = "lets see."
        if name[-1] == "s":
            message = "lets have a look for some %s " % (name)
        else:
            message = "lets have a look for a %s " % (name)
        return message

    @staticmethod
    def what_object():
        message = "okay. what did you want to look for"
        return message
