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
            #protocol.send(self.client_socket, GENERIC_MSG, "Welcome! Testing server->client message sending")
            #LOG.debug("Sent welcome message to client " + str(self.client_address))
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
                            LOG.debug("Client is attempting to join an ongoing game.")
                            self.handle_join_game(message_content)
                        if message_type == CREATE_GAME_MSG:
                            LOG.debug("Client is attempting to create a new game.")
                            self.handle_create_game()
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
        content_list = list(self.server.games.keys())
        for element in content_list:
            content += str(element)
            content += CONTENT_SEPARATOR
        if len(content) > 0:
            content = content[:-1]
        protocol.send(self.client_socket, GAME_LIST_MSG, content)

    def send_scores(self):
        """Send the current scores."""
        content = protocol.assemble_send_scores_msg_content(self.game.scores)
        protocol.send(self.client_socket, SEND_SCORES_MSG, content)

    def handle_join_game(self, content):
        """Handle game join request."""
        game_id = int(content)
        if game_id in self.server.games.keys():
            self.game = self.server.games[game_id]
            self.game.add_connected_client(self)
            LOG.debug("Client " + str(self.id) + " joined game " + str(game_id))
            protocol.send(self.client_socket, SUCCESSFUL_JOIN_MSG, "Successfully joined game.")
            self.send_new_board_state()
            self.send_scores()
        else:
            LOG.debug("Client could not join game with id " + str(game_id) + ". Game with that id does not exist.")
            protocol.send(self.client_socket, FAILED_JOIN_MSG, "Failed to join game.")

    def handle_create_game(self):
        """Handle game creation request."""
        self.game = self.server.create_game()
        self.game.add_connected_client(self)
        self.send_new_board_state()
        self.send_scores()

    def handle_insert(self, msg_content):
        """Handle insertion event."""
        row, column, digit = protocol.parse_insert_msg_content(msg_content)
        score_change = self.game.update_board(row, column, digit, self.id)
        if not score_change or score_change < 1:
            LOG.debug("Invalid insertion attempt of digit " + str(digit) + " into coordinates " +
                      str(row) + ":" + str(column))
            protocol.send(self.client_socket, FAILED_INS_MSG, "Insertion failed.")
            self.send_scores()
        else:
            LOG.debug("Successful insertion")
            protocol.send(self.client_socket, SUCCESSFUL_INS_MSG, "Insertion successful.")
            self.game.broadcast_new_state()
            self.send_scores()

    def send_new_board_state(self):
        """Send new board state to the client."""
        content = protocol.assemble_board_state_msg_content(self.game.board)
        protocol.send(self.client_socket, BOARD_STATE_MSG, content)

    def disconnect(self):
        """Disconnect the client."""
        self.game.remove_connected_client(self.id)
        self.client_socket.close()
        LOG.debug("Terminating client %s:%d" % self.client_address)