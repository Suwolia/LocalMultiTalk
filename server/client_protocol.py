# -*- coding:utf-8 -*-

import struct

HEADLEN = 2

class CommunicateData(object):
    def __init__(self, sel, sock, addr):
        super(CommunicateData, self).__init__()
        self._sel = sel
        self._sock = sock
        self._addr = addr
        self._recv_buffer = b''
        self._send_buffer = b''
        self._content_len = None
        self._content = None

    def send_data(self):
        pass

    def in_data(self, data):
        self._recv_buffer += data
        self._check_content_len()
        self._get_content()

    def _check_content_len(self):
        if len(self._recv_buffer) >= HEADLEN:
            self._content_len = struct.unpack('>H', self._recv_buffer[:HEADLEN])[0]
            self._recv_buffer = self._recv_buffer[HEADLEN:]
    
    def _get_content(self):
        if self._content_len and len(self._recv_buffer) >= self._content_len:
            self._content = self._utf8_decode(self._recv_buffer[:self._content_len])
            self._recv_buffer = self._recv_buffer[self._content_len:]
            # destroy content length when consume it
            self._content_len = None


    def _utf8_encode(self, content):
        return 0

    def _utf8_decode(self, content):
        return 0
