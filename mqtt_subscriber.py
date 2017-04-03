import paho.mqtt.client as mqtt

MQTT = "test.mosquitto.org"
MQTTPORT = 1883
client = mqtt.Client()


def on_connect(client, userdata, flags, rc):
    print("Connected with result " + str(rc))

    client.subscribe("snort/test")


def on_message(client, userdata, msg):
    print(msg.payload.decode('utf-8'))


client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT, MQTTPORT, 60)

client.loop_forever()
