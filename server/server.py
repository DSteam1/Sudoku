from socket import socket, AF_INET, SOCK_STREAM

from clienthandler import *
from game import *
from common.utils import *


class Server:
    """
    Server instance
    """
    sock = socket(AF_INET, SOCK_STREAM)

    def __init__(self, server):
        try:
            LOG.info("Initializing server socket.")
            self.sock.bind(server)
            self.sock.listen(10)
            LOG.info("Server socket initialization complete.")
        except:
            LOG.error("Error initializing server socket.")
        self.games = {}
        self.latest_game_id = 0
        self.listen_for_connections()

    def listen_for_connections(self):
        """Wait for clients to connect. Connect with them when they initiate a connection."""
        try:
            client_id = 0
            while True:
                LOG.info("Awaiting connections from clients..")
                client_socket, client_address = self.sock.accept()
                LOG.debug("New client connected from %s:%d" % client_address)
                c = ClientHandler(self, client_socket, client_address, client_id)
                client_id += 1
                c.setDaemon(True)
                c.start()
        except KeyboardInterrupt:
            LOG.info("Received Keyboard Interrupt. Shutting down.")
            self.disconnect()
        finally:
            LOG.debug("Disconnecting all clients.")
            self.disconnect()

    def create_game(self, needed_players):
        """Create a new game instance."""
        game = Game(self.latest_game_id, self, needed_players)
        self.games[self.latest_game_id] = game
        self.latest_game_id += 1
        return game

    def end_game(self, game_id):
        """End a game instance."""
        self.games.pop(game_id)

    def disconnect(self):
        """Close the socket."""
        self.sock.close()


LOG = init_logging()
address, port = get_server_address_and_port()
Server((address, port))
