import os
import socket
import paho.mqtt.client as mqtt
import struct
import binascii

ALERTMSG_LENGTH = 256
SNAPLEN = 1500
MQTT = os.environ['MQTT']

snort_mqtt = mqtt.Client()
snort_mqtt.connect(MQTT)
snort_mqtt.loop_start()
s = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
format = "%ds9l%ds" % (ALERTMSG_LENGTH, SNAPLEN)
format_size = struct.calcsize(format)
try:
    os.remove("/var/log/snort/snort_alert")
except OSError:
    pass
s.bind("/var/log/snort/snort_alert")

while True:
    data, addr = s.recvfrom(4096)
    msg, ts_sec, ts_usec, caplen, pktlen, dlthdr, nethdr, transhdr, data_snort, val, pkt = struct.unpack(format, data[:format_size])
    #print(pkt)
    #print(msg)
    snort_mqtt.publish("snort/test", str(msg))
conn.close()
