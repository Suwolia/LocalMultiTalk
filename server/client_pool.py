# -*- coding:utf-8 -*-

import selectors
import socket
from client_protocol import CommunicateData
import struct

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
        sock.setblocking(False)
        events = selectors.EVENT_READ
        communicate_data = CommunicateData(self._sel, sock, (ip, port))
        communicate_data.add_read_callback(self.response_all_clients)
        self._connections_dic[key] = communicate_data
        print(key, 'has been connected in')
        self._sel.register(sock, events, data=communicate_data)

    def del_connection(self, ip, port):
        key = ip + ':' + str(port)
        if not key in self._connections_dic:
            print(key, 'not exist')
            return
        self._sel.unregister(self._connections_dic[key].get_socket())
        self._connections_dic[key].get_socket().close()
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

    def pack_response_for_all_clients(self):
        # collect all clients content
        response_bytes = b''
        for k, v in self._connections_dic.items():
            cts = v.get_contents()
            if cts:
                for c in cts:
                    response_bytes += struct.pack('>H', len(c))
                    response_bytes += c
        return response_bytes

    def response_all_clients(self):
        response_packed = self.pack_response_for_all_clients()
        for k, v in self._connections_dic.items():
            v.set_response(response_packed)
            v.change_event_mode('rw')

