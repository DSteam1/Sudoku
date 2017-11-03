#! /usr/bin/env python
from socket import socket, AF_INET, SOCK_STREAM
from utils import *
from clienthandler import *


class Server:
    sock = socket(AF_INET,SOCK_STREAM)

    def __init__(self, server):
        try:
            LOG.info("Initializing server socket.")
            self.sock.bind(server)
            self.sock.listen(10)
            LOG.info("Server socket initialization complete.")
        except:
            LOG.error("Error initializing server socket.")
        self.listen_for_connections()

    def listen_for_connections(self):
        try:
            while True:
                LOG.info("Awaiting connections from clients..")
                client_socket, client_address = self.sock.accept()
                LOG.debug("New client connected from %s:%d" % client_address)
                c = ClientHandler(client_socket, client_address)
                c.setDaemon(True)
                c.start()
        except KeyboardInterrupt:
            LOG.info("Received Keyboard Interrupt. Shutting down.")
            self.disconnect()
        finally:
            LOG.debug("Disconnecting all clients.")
            self.disconnect()

    def disconnect(self):
        self.sock.close()


LOG = init_logging()

Server(('127.0.0.1', 7777))
