# -*- coding:utf-8 -*-

import socket
import selectors

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('10.254.44.229', 11493))
