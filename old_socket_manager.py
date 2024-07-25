import os
import socket
import network
import websocket_helper
from websocket import websocket
import select
import struct
import json
import sys

_server = None


def init():
    global _server
    
    if _server is None:
        print("initializing websocket server")
        _server = WebSocketServer()
    else:
        print("server already initialized")
        return


def Server():
    global _server
    return _server



class ClientClosedError(Exception):
    pass


class WebSocketClient:
    def __init__(self, conn):
        self.connection = conn
        
    

    def process(self):
        try:
            msg = self.connection.read()
            if not msg:
                return
            #print(msg)
            #msg = msg.decode("utf-8")
            #print(msg)
            s_len = struct.calcsize("<BBI")
            if len(msg) >= s_len:
                header = msg[:s_len]
                body = msg[s_len:]
                cmd, status, length = struct.unpack("<BBI", header)
            
                if cmd == 32:
                    cnt = 0
                    sz = os.stat(body)[6]
                    #self.connection.write(struct.pack("<BBI", 0x22,0x1,sz))
                    with open(body, "rb") as f:
                        while True:
                            
                            print(f"Sent %d of %d bytes\r" % (cnt, sz))
                            
                            buf = f.read(128)
                            if not buf:
                                break
                            
                            cnt += len(buf)
                            kral = (struct.pack("<BBI", 0x22,0x1,sz) + buf)
                            self.connection.write(kral)
                    
                
                if cmd == 33:
                    
                    test = " ".join(os.listdir('')).encode("utf-8")
                    
                    kral = (struct.pack("<BBI", 0x21,0x1,len(test)) + test)
                    self.connection.write(kral)
    #                 cnt = 0
    #                 sz = os.stat("socket_manager.py")[6]
    #                 with open("socket_manager.py", "rb") as f:
    #                     while True:
    #                         print(f"Sent %d of %d bytes\r" % (cnt, sz))
    #                         
    #                         buf = f.read(1024)
    #                         if not buf:
    #                             break
    #                         self.connection.write(buf)
    #                         cnt += len(buf)
                    
                    #self.connection.write(dir_list)
            
        except ClientClosedError:
            self.connection.close()

class WebSocketConnection:
    def __init__(self, addr, s, close_callback):
        self.client_close = False
        self._need_check = False

        self.address = addr
        self.socket = s
        self.ws = websocket(s)
        self.ws.ioctl(9, 2)
        self.poll = select.poll()
        self.close_callback = close_callback

        self.socket.setblocking(False)
        self.poll.register(self.socket, select.POLLIN)

    def read(self):
        poll_events = self.poll.poll(0)

        if not poll_events:
            return

        # Check the flag for connection hung up
        if poll_events[0][1] & select.POLLHUP:
            self.client_close = True

        msg_bytes = None
        try:
            msg_bytes = self.ws.read()
        except OSError:
            self.client_close = True

        # If no bytes => connection closed. See the link below.
        # http://stefan.buettcher.org/cs/conn_closed.html
        if not msg_bytes or self.client_close:
            raise ClientClosedError()

        return msg_bytes

    def write(self, msg):
        try:
            l = len(msg)
            if l < 126:
                # TODO: hardcoded "binary" type
                hdr = struct.pack(">BB", 0x82, l)
            else:
                hdr = struct.pack(">BBH", 0x82, 126, l)
                
            #self.ws.write(hdr)
            self.ws.write(msg)
        except OSError:
            self.client_close = True

    def is_closed(self):
        return self.socket is None

    def close(self):
        print("Closing connection.")
        self.poll.unregister(self.socket)
        self.socket.close()
        self.socket = None
        self.ws = None
        if self.close_callback:
            self.close_callback(self)

class WebSocketServer:
    def __init__(self, max_connections=1):
        self._listen_s = None
        self._listen_poll = None
        self._clients = []
        self._max_connections = max_connections
    
    def _make_client(self, conn):
        return WebSocketClient(conn)
    
    def _setup_conn(self, port):
        self._listen_s = socket.socket()
        self._listen_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._listen_poll = select.poll()
        
        ad = ""
        sta = network.WLAN(network.STA_IF)
        
        if sta.isconnected():
            ad = sta.ifconfig()[0]
            
        ai = socket.getaddrinfo('0.0.0.0', port)
        addr = ai[0][4]
        print(addr)
        

        self._listen_s.bind(addr)
        self._listen_s.listen(1)
        self._listen_poll.register(self._listen_s)
        for i in (network.AP_IF, network.STA_IF):
            iface = network.WLAN(i)
            if iface.active():
                print("WebSocket started on ws://%s:%d" % (iface.ifconfig()[0], port))
    
    def _check_new_connections(self, accept_handler):
        
        poll_events = self._listen_poll.poll(0)
        
        if not poll_events:
            return
        
        
        if poll_events[0][1] & select.POLLIN:
            accept_handler()
            
            

    def _accept_conn(self):
        
        cl, remote_addr = self._listen_s.accept()
        print("Client connection from:", remote_addr)

        if len(self._clients) >= self._max_connections:
            print("Max Connections reached closing socket", remote_addr)
            cl.close()
            return

        try:
            websocket_helper.server_handshake(cl)
        except OSError:
            # Not a websocket connection, serve webpage
            print("Not a websocket connection")
            cl.close()
            return

        self._clients.append(self._make_client(WebSocketConnection(remote_addr, cl, self.remove_connection)))
        
    def stop(self):
        if self._listen_poll:
            self._listen_poll.unregister(self._listen_s)
        self._listen_poll = None
        if self._listen_s:
            self._listen_s.close()
        self._listen_s = None

        for client in self._clients:
            client.connection.close()
        print("Stopped WebSocket server.")
    
    
    
    def update(self):
        if not self.active():
            return
        
        self._check_new_connections(self._accept_conn)
        
        if self.connected():
            for client in self._clients:
                client.process()
    
    def active(self):
        return self._listen_s is not None and self._listen_poll is not None
    
    def connected(self):
        return len(self._clients) > 0

    def start(self, port=80):
        if self._listen_s:
            self.stop()
        self._setup_conn(port)
        print("Started WebSocket server.")
    
         
    def send(self, msg):
        
        if not msg:
            return
        
        if self.active and self.connected:
            for client in self._clients:
                client.connection.write(msg)
    
    def remove_connection(self, conn):
        for client in self._clients:
            if client.connection is conn:
                self._clients.remove(client)
                return
