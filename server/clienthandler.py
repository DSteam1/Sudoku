import select
from socket import error as soc_error
from threading import Thread

from common.utils import init_logging

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
            while not client_shutdown:
                read_sockets, write_sockets, error_sockets = \
                        select.select([self.client_socket] , [], [])
                #TODO: handle messages
                client_shutdown = True

        except soc_error as e:
            LOG.debug("Lost connection with %s:%d" % self.client_address)
        finally:
            self.disconnect()

    def disconnect(self):
        self.client_socket.close()
        LOG.debug("Terminating client %s:%d" % self.client_address)