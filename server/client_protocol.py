# -*- coding:utf-8 -*-

import struct
import selectors

HEADLEN = 2

class CommunicateData(object):
    def __init__(self, sel, sock, addr):
        super(CommunicateData, self).__init__()
        self._sel = sel
        self._sock = sock
        self._addr = addr
        self._addr_str = addr[0] + ':' + str(addr[1]) + ' '
        self._recv_buffer = b''
        self._send_buffer = b''
        self._content_len = None
        self._contents = []
        self._response_packed_content = None
        self._read_over_callback = []

    def add_read_callback(self, func):
        self._read_over_callback.append(func)

    def get_socket(self):
        return self._sock

    def get_addr(self):
        return self._addr

    def send_data(self):
        if self._response_packed_content:
            try:
                sent = self._sock.send(self._response_packed_content)
            except:
                pass
            self._response_packed_content = self._response_packed_content[sent:]
            if sent and not self._response_packed_content:
                self._response_packed_content = None
                self.change_event_mode('r')


    def change_event_mode(self, mode):
        if mode == 'r':
            self._sel.modify(self._sock, selectors.EVENT_READ, self)
        elif mode == 'w':
            self._sel.modify(self._sock, selectors.EVENT_WRITE, self)
        elif mode == 'rw':
            self._sel.modify(self._sock, selectors.EVENT_READ | selectors.EVENT_WRITE, self)
        else:
            raise RuntimeWarning('Unknow mode was set to', repr(self))

    def in_data(self, data):
        self._recv_buffer += data
        self._check_content_len()
        self._get_content()

    def get_contents(self):
        if len(self._contents) == 0:
            return None
        else:
            decorate_contents = []
            for c in self._contents:
                decorate_contents.append(self._utf8_encode(self._addr_str) + c)
            return decorate_contents

    def set_response(self, packed_content):
        self._response_packed_content = packed_content
        self._contents = []

    def _check_content_len(self):
        if len(self._recv_buffer) >= HEADLEN:
            self._content_len = struct.unpack('>H', self._recv_buffer[:HEADLEN])[0]
            self._recv_buffer = self._recv_buffer[HEADLEN:]
    
    def _get_content(self):
        if self._content_len and len(self._recv_buffer) >= self._content_len:
            _content = self._recv_buffer[:self._content_len]
            translate_content = self._utf8_decode(_content)
            print('received', self._addr_str, translate_content)
            self._contents.append(_content)
            self._recv_buffer = self._recv_buffer[self._content_len:]
            # destroy content length when consume it
            self._content_len = None
            
            for cb in self._read_over_callback:
                cb()

    def _utf8_encode(self, content):
        return content.encode('utf-8')

    def _utf8_decode(self, content):
        return content.decode()

