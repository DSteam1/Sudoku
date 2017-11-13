import sudoku.board as board
import common.protocol as protocol
from common.utils import init_logging
from common.constants import *

LOG = init_logging()


class Game:
    """
    Instance of a sudoku game on the server side
    """
    def __init__(self, id, server, needed_players):
        self.id = id
        self.server = server
        self.board = board.Board()
        self.board.setup_board()
        self.connected_clients = {}
        # Dictionary with keys being client id-s and values being the score values
        self.scores = {}
        self.needed_players = needed_players
        self.has_started = False

    def add_connected_client(self, client):
        """Add a client to the game."""
        self.scores[client.id] = 0
        self.connected_clients[client.id] = client

    def remove_connected_client(self, client_id):
        """Remove a client from the game."""
        self.connected_clients.pop(client_id)
        self.scores.pop(client_id)
        LOG.debug("Removed client with id " + str(client_id) + " from game")

    def get_connected_clients(self):
        """Get the dictionary of connected clients in the game."""
        return self.connected_clients

    def update_board(self, row, column, digit, client_id):
        """Attempt to update the board attached to this game instance."""
        score_change = self.board.add_number(column, row, digit)
        if client_id in self.scores:
            self.scores[client_id] += score_change
            LOG.debug("Score of client with id " + str(client_id) + " changed by " + str(score_change))
        else:
            LOG.debug("Score of client with id " + str(client_id) + " could not be updated.")
        return score_change

    def notify_clients_of_game_completion(self):
        """Send victory/game over messages to all players."""
        LOG.debug("Game is complete. Sending game over messages to clients.")
        winning_client_id = max(self.scores, key=self.scores.get)
        winning_client = self.connected_clients[winning_client_id]
        winning_client_username = winning_client.username
        protocol.send(winning_client.client_socket, GAME_OVER_VICTORY_MSG, "You win!")
        for client in self.connected_clients.values():
            if client.id == winning_client_id:
                continue
            else:
                protocol.send(client.client_socket, GAME_OVER_LOSS_MSG,
                              winning_client_username + " wins!")

    def get_score(self, client_id):
        return self.scores[client_id]

    def get_board(self):
        """Get the current board."""
        return board

    def broadcast_new_state(self):
        """Send the new board state to all clients connected to this game instance."""
        LOG.debug("Sending new board states to clients")
        for client in self.connected_clients.values():
            client.send_new_board_state()

    def broadcast_scores(self):
        """Send the scores to all clients connected to this game instance."""
        LOG.debug("Sending scores to clients")
        for client in self.connected_clients.values():
            client.send_scores()

    def is_game_complete(self):
        """Check whether the game is complete."""
        complete = self.board.is_solved()
        return complete

    def terminate_game(self):
        """End the game."""
        LOG.debug("Terminating game.")
        self.server.end_game(self.id)

    def start_game_if_enough_players(self):
        if len(self.connected_clients) >= int(self.needed_players):
            LOG.debug("Starting the game since enough players have joined. Sending start game messages to all players.")
            self.has_started = True
            for client in self.connected_clients.values():
                protocol.send(client.client_socket, START_GAME_MSG, "")
