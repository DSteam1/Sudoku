import select
from socket import error as soc_error
from threading import Thread

from common.utils import init_logging
from common.constants import *
import common.protocol as protocol

LOG = init_logging()


class ClientHandler(Thread):
    def __init__(self, client_socket, client_address):
        Thread.__init__(self)
        self.client_socket = client_socket
        self.client_address = client_address

    def run(self):
        self.handle()

    def handle(self):
        client_shutdown = False
        try:
            protocol.send(self.client_socket, GENERIC_MSG, "Welcome! Testing server->client message sending")
            LOG.debug("Sent welcome message to client " + str(self.client_address))
            while not client_shutdown:
                read_sockets, write_sockets, error_sockets = select.select([self.client_socket], [], [])
                for socket in read_sockets:
                    message = protocol.receive(socket)
                    if message:
                        message_type, message_content = protocol.parse(message)
                        if message_type == GENERIC_MSG:
                            LOG.debug("Received message: " + message_content)
                        if message_type == CLIENT_DISCONNECT_MSG:
                            LOG.debug("Client requested disconnection with message: " + message_content)
                            client_shutdown = True
                    else:
                        LOG.debug("Client terminated connection")
                        client_shutdown = True

        except soc_error as e:
            LOG.debug("Lost connection with %s:%d" % self.client_address)
        finally:
            self.disconnect()

    def disconnect(self):
        self.client_socket.close()
        LOG.debug("Terminating client %s:%d" % self.client_address)