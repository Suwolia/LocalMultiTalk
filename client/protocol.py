# -*- coding:utf-8 -*-

import selectors
import socket
import struct

HEADLEN = 2

class CommunicateData(object):
    def __init__(self, sel, sock, addr):
        super(CommunicateData, self).__init__()
        self._sel = sel
        self._sock = sock
        self._addr = addr
        # self._contents = []
        self._recv_content_len = None
        self._recv_buffer = b''
        self._send_buffer = b''

    def change_event_mode(self, mode):
        if mode == 'r':
            self._sel.modify(self._sock, selectors.EVENT_READ, data=self)
        elif mode == 'w':
            self._sel.modify(self._sock, selectors.EVENT_WRITE, data=self)
        elif mode == 'rw':
            self._sel.modify(self._sock, selectors.EVENT_READ | selectors.EVENT_WRITE, data=self)
        else:
            print('unknow mode was set')

    def send_data(self):
        if self._send_buffer:
            try:
                sent = self._sock.send(self._send_buffer)
            except:
                raise RuntimeWarning('send failed')
            self._send_buffer = self._send_buffer[sent:]
            if sent and not self._send_buffer:
                self._send_buffer = b''
                # self.change_event_mode('r')

    def recv_data(self):
        recv = self._sock.recv(2048)
        if recv:
            self._recv_buffer += recv
        self._get_recv_content_len()
        self._get_content()

    def _get_recv_content_len(self):
        if len(self._recv_buffer) >= HEADLEN:
            self._recv_content_len = struct.unpack('>H', self._recv_buffer[:HEADLEN])[0]
            self._recv_buffer = self._recv_buffer[HEADLEN:]

    def _get_content(self):
        if self._recv_content_len and len(self._recv_buffer) >= self._recv_content_len:
            _content = self._recv_buffer[:self._recv_content_len]
            print('Received message', self._utf8_decode(_content))
            self._recv_buffer = self._recv_buffer[self._recv_content_len:]
            self._recv_content_len = None

    def _utf8_decode(self, content):
        return content.decode('utf-8')

    def _utf8_encode(self, content):
        return content.encode('utf-8')

    def set_content(self, content):
        _content_packed = self._utf8_encode(content)
        _content_packed_len = len(_content_packed)
        self._send_buffer += struct.pack('>H', _content_packed_len)
        self._send_buffer += _content_packed
