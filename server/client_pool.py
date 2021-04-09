# -*- coding:utf-8 -*-

import selectors
import socket
from client_protocol import CommunicateData

class ClientPool(object):
    def __init__(self, sel):
        super(ClientPool, self).__init__()
        self._connections_dic = {}
        self._sel = sel

    def add_connection(self, ip, port, sock):
        key = ip + ':' + str(port)
        if key in self._connections_dic:
            print(key, 'already has been stored')
            return
        self._connections_dic[key] = sock
        sock.setblocking(False)
        events = selectors.EVENT_READ
        self._sel.register(sock, events, data=CommunicateData(self._sel, sock, (ip, port)))

    def del_connection(self, ip, port):
        key = ip + ':' + str(port)
        if not key in self._connections_dic:
            print(key, 'not exist')
            return
        self._sel.unregister(self._connections_dic[key])
        self._connections_dic[key].close()
        del self._connections_dic[key]

    def response_to_conn(self, key, mask):
        data = key.data
        ip, port = data.get_addr()
        sock = key.fileobj
        if mask & selectors.EVENT_READ:
            recv_data = sock.recv(4096)
            if recv_data:
                data.in_data(recv_data)
            else:
                print('closing connection to ', data.get_addr())
                self.del_connection(ip, port)
        if mask & selectors.EVENT_WRITE:
            data.send_data()
