import json
from located_object import LocatedObject


class BackendResponse:
    """
    Used to implement communication protocol between backend-frontend. Backend does some
    computation using the information from the frontends request. The information e.g.
    location information is stored into a BackendResponse object. The BackendResponse object
    then packs the object into json so it can be sent over MQTT as a string. The frontend
    can then unpack the recieved message back into a BackendResponse object so that it can
    be processed.
    """
    def __init__(self, code_name, original_request, location_time, location_time_passed, locations_identified):
        self.code_name = code_name
        self.original_request = original_request
        self.location_time = location_time
        self.location_time_passed = location_time_passed
        self.locations_identified = []
        if locations_identified:
            for loc in locations_identified:
                x = json.loads(loc)
                print(x)
                lo = LocatedObject(x['camera_id'], x['object'], x['location'])
                self.locations_identified.append(lo)

    def pack(self):
        """
        Pack the objects information into a json object so that it can be transmitted over
        MQTT.
        :return: A json object containing the BackendResponse
        """
        package = {}
        package['code_name'] = self.code_name
        package['location_time'] = self.location_time
        locations_identified = []
        for location in self.locations_identified:
            locations_identified.append(location.to_json())
        package['locations_identified'] = locations_identified
        return json.dumps(package)

    def print(self):
        print("Code name: ", self.code_name)
        print("Location_time: ", self.location_time)
        print("Minutes passed: ", self.location_time_passed)
        for loc in self.locations_identified:
            print(loc.object + " " + loc.location)
