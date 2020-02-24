import json


class LocatedObject:
    """
    A pair of objects which were located near each other
    """
    def __init__(self, camera_id, object, location):
        self.camera_id = camera_id
        self.object = object
        self.location = location

    def to_json(self):
        data = {}
        data['camera_id'] = self.camera_id
        data['object'] = self.object
        data['location'] = self.location
        json_data = json.dumps(data)
        return json_data
