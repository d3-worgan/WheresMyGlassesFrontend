import paho.mqtt.client as mqtt


class MQTTConnection:
    """
    class to wrap a paho client and create "connections" between system components
    """

    def __init__(self, broker, name, on_message=None):
        self.name = name
        self.con = mqtt.Client(name)
        self.con.on_connect = self.on_connect
        self.con.on_log = self.on_log
        self.con.on_disconnect = self.on_disconnect
        self.con.on_message = on_message  # Main callback (connection)
        self.con.connect(broker)
        self.con.loop_start()

    def subscribe_topic(self, topic):
        assert topic is not None, self.name + " did not specify a topic to subscribe to."
        self.con.subscribe(topic)
        print(self.name + " client subscribed to " + topic)

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
