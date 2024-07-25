import os
import socket
import network
import websocket_helper
from websocket import websocket
import select
import struct
import json
import sys
import time

_server = None


def init():
    global _server
    
    if _server is None:
        print("initializing TCP server")
        _server = TCPServer()
    else:
        print("server already initialized")
        return


def Server():
    global _server
    return _server



class ClientClosedError(Exception):
    pass


class TCPClient:
    def __init__(self, conn):
        self.connection = conn
        
    def put_file(self, path, size):
        result = False
        
        filename = path.split("/")[-1]
        base_path = path[:len(path) - len(filename)]
        temp_filename = "{}{}".format("_temp", filename)
        
        temp_path = base_path + temp_filename
        
        print(temp_path)
        d = {
            "command":"sendfile",
            "path" : path,
            "size" : size
        }
        
        m = json.dumps(d).encode()
        self.connection.write(m)
        
        cnt=0
        with open(temp_path, "wb+") as f:
            time.sleep_ms(1000)
            while True:
                print(f"Received %d of %d bytes\r" % (cnt, size))
                msg = self.connection.read()
                if not msg:
                    break
                f.write(msg)
                cnt += len(msg)
        
        result = (cnt == size)
        return (result, filename)
                
    
    def get_file(self, path, size):
        result = False
        d = {
            "command":"put",
            "path" : path,
            "size" : size
        }
        
        m = json.dumps(d).encode()
        self.connection.write(m)
        
        cnt = 0
        with open(path, "rb") as f:
            while True:
                print(f"Sent %d of %d bytes\r" % (cnt, size))
                
                buf = f.read(1024)
                if not buf:
                    break
                self.connection.write(buf)
                time.sleep_ms(100)
                cnt += len(buf)
        
        result = (cnt == size)
        #self.connection.write(b'\0')
        return result

    def process(self):
        try:
            msg = self.connection.read()
            if not msg:
                return
            
            msg = msg.decode("utf-8")
            print(msg)
            try:
                msg = json.loads(msg)
                
                if msg.get("error") is not None:
                    print(msg.get("error"))
                    return
                
                if msg.get("command") is not None:
                    if msg.get("command") == "get":
                        path = msg.get("path")
                        size = os.stat(path)[6]
                        result = self.get_file(path, size)
                        if not result:
                            print("Failed to send file")
                        
                    elif msg.get("command") == "put":
                        #self.connection.write(b'\0')
                        
                        path = msg.get("path")
                        size = msg.get("size")
                        self.put_file(path,size)
                        
                        
                        
                            
                
            except ValueError as e:
                print(e)
                t = { "error" : "la oglum olmadi" }
                a = json.dumps(t).encode()
                self.connection.write(b'{ "error" : "la oglum olmadi" }')
                return
            
            
        except ClientClosedError:
            self.connection.close()

class TCPConnection:
    def __init__(self, addr, s, close_callback):
        self.client_close = False
        self._need_check = False

        self.address = addr
        self.socket = s
        self.poll = select.poll()
        self.close_callback = close_callback

        self.socket.setblocking(False)
        self.poll.register(self.socket, select.POLLIN)

    def read(self, size=1024):
        poll_events = self.poll.poll(0)

        if not poll_events:
            return

        # Check the flag for connection hung up
        if poll_events[0][1] & select.POLLHUP:
            self.client_close = True

        msg_bytes = None
        try:
            msg_bytes = self.socket.read(size)
        except Exception as e:
            print(e)
            self.client_close = True

        # If no bytes => connection closed. See the link below.
        # http://stefan.buettcher.org/cs/conn_closed.html
        if not msg_bytes or self.client_close:
            raise ClientClosedError()

        return msg_bytes

    def write(self, msg):
        
        try:
            self.socket.write(msg)
        except Exception as e:
            print(e)
            self.client_close = True
        

    def is_closed(self):
        return self.socket is None

    def close(self):
        print("Closing connection.")
        self.poll.unregister(self.socket)
        self.socket.close()
        self.socket = None
        if self.close_callback:
            self.close_callback(self)

class TCPServer:
    def __init__(self, max_connections=1):
        self._listen_s = None
        self._listen_poll = None
        self._clients = []
        self._max_connections = max_connections
    
    def _make_client(self, conn):
        return TCPClient(conn)
    
    def _setup_conn(self, port):
        self._listen_s = socket.socket()
        self._listen_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._listen_poll = select.poll()
        
        ai = socket.getaddrinfo('0.0.0.0', port)
        addr = ai[0][4]
        
        self._listen_s.bind(addr)
        self._listen_s.listen(1)
        self._listen_poll.register(self._listen_s)
        for i in (network.AP_IF, network.STA_IF):
            iface = network.WLAN(i)
            if iface.active():
                print("TCP Socket started on %s:%d" % (iface.ifconfig()[0], port))
    
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


        self._clients.append(self._make_client(TCPConnection(remote_addr, cl, self.remove_connection)))
        
    def stop(self):
        if self._listen_poll:
            self._listen_poll.unregister(self._listen_s)
        self._listen_poll = None
        if self._listen_s:
            self._listen_s.close()
        self._listen_s = None

        for client in self._clients:
            client.connection.close()
        print("Stopped TCP server.")
    
    
    
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

    def start(self, port=8080):
        if self._listen_s:
            self.stop()
        self._setup_conn(port)
        print("Started TCP server.")
    
         
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
