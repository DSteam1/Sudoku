import select
from socket import error as soc_error
from threading import Thread

from common.utils import init_logging
from common.constants import *
import common.protocol as protocol
import sudoku.board as board

LOG = init_logging()


class ClientHandler(Thread):
    """
    A handler which the server uses to interact with the client
    """
    def __init__(self, server, client_socket, client_address, client_id):
        Thread.__init__(self)
        self.server = server
        self.id = client_id
        self.client_socket = client_socket
        self.client_address = client_address
        self.board = board.Board()
        self.board.setup_board()
        self.game = None

    def run(self):
        self.handle()

    def handle(self):
        """Handle the messages from the client. Loop until disconnection."""
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
                        if message_type == REQ_GAMES_MSG:
                            LOG.debug("Received game list request. Sending game list to client.")
                            self.send_game_list()
                        if message_type == INSERT_MSG:
                            LOG.debug("Attempting to insert")
                            self.handle_insert(message_content)
                        if message_type == JOIN_GAME_MSG:
                            LOG.debug("Client attempting to join ongoing game")
                            self.handle_join(message_content)
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

    def send_game_list(self):
        """Send the list of games to the client."""
        content = ""
        for game in self.server.games:
            content += str(game.id)
            content += CONTENT_SEPARATOR
        content = content[:-1]
        protocol.send(self.client_socket, GAME_LIST_MSG, content)

    def handle_join(self, content):
        """Handle game join request."""
        #TODO: handle join
        return

    def handle_create_game(self):
        """Handle game creation request."""
        self.game = self.server.create_game()
        self.game.add_connected_client(self)
        self.send_new_board_state()

    def handle_insert(self, msg_content):
        """Handle insertion event."""
        row, column, digit = protocol.parse_insert_msg_content(msg_content)
        validated_digit = self.game.update_board(row, column, digit)
        if not validated_digit:
            LOG.debug("Invalid insertion attempt of digit " + str(digit) + " into coordinates " +
                      str(row) + ":" + str(column))
        else:
            LOG.debug("Successful insertion ")
            self.game.broadcast_new_state()

    def send_new_board_state(self):
        """Send new board state to the client."""
        content = protocol.assemble_board_state_msg_content(self.game.board)
        protocol.send(self.client_socket, BOARD_STATE_MSG, content)

    def disconnect(self):
        """Disconnect the client."""
        self.client_socket.close()
        LOG.debug("Terminating client %s:%d" % self.client_address)