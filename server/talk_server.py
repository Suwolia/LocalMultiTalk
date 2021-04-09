# -*- coding:utf-8 -*-

import selectors
import socket
import argparse
import client_pool

sel = selectors.DefaultSelector()
c_pool = client_pool.ClientPool(sel)

def accept_wrapper(key, mask):
    lsock = key.fileobj
    conn, addr = lsock.accept()
    c_pool.add_connection(addr[0], addr[1], conn)

def start_listen_to(ip, port):
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lsock.bind((ip, port))
    lsock.listen()
    lsock.setblocking(False)
    events = selectors.EVENT_READ
    sel.register(lsock, events, data=None)

def selector_loop():
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            # listen socket in
            if key.data == None:
                accept_wrapper(key, mask)
            # handle connected socket
            else:
                c_pool.response_to_conn(key, mask)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Talk server argument parser')
    parser.add_argument('ip', help='Bind the ip to listen', type=str)
    parser.add_argument('port', help='Bind the port to listen', type=int)
    args = parser.parse_args()
    ip = args.ip
    port = args.port
    start_listen_to(ip, port)
    selector_loop()
