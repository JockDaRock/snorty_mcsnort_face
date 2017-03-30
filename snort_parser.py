import dpkt
import socket
from snortunsock import snort_listener
import paho.mqtt.client as mqtt
import json
import os

MQTT = os.environ['MQTT']

snort_mqtt = mqtt.Client()
snort_mqtt.connect(MQTT)
snort_mqtt.loop_start()


def mac_addr(address):
    """Convert a MAC address to a readable/printable string
       Args:
           address (str): a MAC address in hex form (e.g. '\x01\x02\x03\x04\x05\x06')
       Returns:
           str: Printable/readable MAC address
    """
    return ':'.join('%02x' % ord(chr(x)) for x in address)


def ip_to_str(address):
    """Print out an IP address given a string
    Args:
        address (inet struct): inet network address
    Returns:
        str: Printable/readable IP address
    """
    return socket.inet_ntop(socket.AF_INET, address)


def ip6_to_str(address):
    return socket.inet_ntop(socket.AF_INET6, address)


def main():
    snort_message = {}
    for msg in snort_listener.start_recv("/var/log/snort/snort_alert"):
        orig_msg = b'.'.join(msg.alertmsg)
        am = (str(orig_msg, 'utf-8').replace("\u0000", "")).replace("'", "")
        snort_message["alert_msg"] = str(am)
        print('alertmsg: %s' % str(am))
        buf = msg.pkt

        # Unpack the Ethernet frame (mac src/dst, ethertype)
        eth = dpkt.ethernet.Ethernet(buf)
        src_mac = mac_addr(eth.src)
        dest_mac = mac_addr(eth.dst)

        snort_message["src_mac"] = src_mac
        snort_message["dest_mac"] = dest_mac

        print('Ethernet Frame: ', mac_addr(eth.src), mac_addr(eth.dst), eth.type)

        if eth.type == dpkt.ethernet.ETH_TYPE_IP6:

            ip_type = "IPv6"
            snort_message["ip_type"] = ip_type

            ip = eth.data

            src_ip = ip6_to_str(ip.src)
            dest_ip = ip6_to_str(ip.dst)
            len = ip.plen
            hop_lim = ip.hlim
            packet_info = {"len": len, "hop_limit": hop_lim}

            snort_message["src_ip"] = src_ip
            snort_message["dest_ip"] = dest_ip
            snort_message["packet_info"] = packet_info

            # Print out the info
            print('IP: %s -> %s   (len=%d hop_limit=%d)\n' % \
                  (ip6_to_str(ip.src), ip6_to_str(ip.dst), ip.plen, ip.hlim))


        # Now unpack the data within the Ethernet frame (the IP packet)
        # Pulling out src, dst, length, fragment info, TTL, and Protocol
        elif eth.type == dpkt.ethernet.ETH_TYPE_IP:
            ip_type = "IPv4"
            snort_message["ip_type"] = ip_type

            ip = eth.data

            # Pull out fragment information (flags and offset all packed into off field, so use bitmasks)
            do_not_fragment = bool(ip.off & dpkt.ip.IP_DF)
            more_fragments = bool(ip.off & dpkt.ip.IP_MF)
            fragment_offset = ip.off & dpkt.ip.IP_OFFMASK

            src_ip = ip_to_str(ip.src)
            dest_ip = ip_to_str(ip.dst)
            len = ip.len
            ttl = ip.ttl
            DF = do_not_fragment
            MF = more_fragments
            offset = fragment_offset
            packet_info = {"len": len, "ttl": ttl, "DF": DF, "MF": MF, "offset": offset}

            snort_message["src_ip"] = src_ip
            snort_message["dest_ip"] = dest_ip
            snort_message["packet_info"] = packet_info

            # Print out the info
            #print('IP: %s -> %s   (len=%d ttl=%d DF=%d MF=%d offset=%d)\n' % \
            #      (ip_to_str(ip.src), ip_to_str(ip.dst), ip.len, ip.ttl, do_not_fragment, more_fragments,
            #       fragment_offset))

        else:
            ip_type = "Unsupported"
            snort_message["ip_type"] = ip_type

            src_ip = "N/A"
            dest_ip = "N/A"
            packet_info = {"not_supported_packet": "IP Packet unsupported"}

            snort_message["src_ip"] = src_ip
            snort_message["dest_ip"] = dest_ip
            snort_message["packet_info"] = packet_info

            #print('Non IP Packet type not supported %s\n' % eth.data.__class__.__name__)

        snort_mqtt.publish("snort/test", json.dumps(snort_message))


if __name__ == '__main__':
    main()
