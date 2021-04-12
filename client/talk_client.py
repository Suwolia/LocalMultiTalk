# -*- coding:utf-8 -*-

import socket
import selectors
import argparse
from protocol import CommunicateData
import threading
import sys

sel = selectors.DefaultSelector()


def connect_to_talk_server(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex((ip, port))
    communicate_data = CommunicateData(sel, sock, (ip, port))
    sel.register(sock, selectors.EVENT_READ | selectors.EVENT_WRITE, data=communicate_data)
    return communicate_data


def selector_loop():
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            if mask & selectors.EVENT_READ:
                key.data.recv_data()
            elif mask & selectors.EVENT_WRITE:
                key.data.send_data()

def user_input(c_data):
    while True:
        message = sys.stdin.readline()
        c_data.set_content(message)
        # c_data.change_event_mode('rw')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Talk client argument parser')
    parser.add_argument('ip', help='Connect to the server ip address', type=str)
    parser.add_argument('port', help='Connect to the server port', type=int)
    args = parser.parse_args()
    ip = args.ip
    port = args.port
    communicate_data = connect_to_talk_server(ip, port)
    threading.Thread(target=user_input, args=(communicate_data,)).start()
    selector_loop()


