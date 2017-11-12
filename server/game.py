import sudoku.board as board
from common.utils import init_logging

LOG = init_logging()


class Game:
    """
    Instance of a sudoku game on the server side
    """
    def __init__(self, id):
        self.id = id
        self.board = board.Board()
        self.board.setup_board()
        self.connected_clients = {}
        # Dictionary with keys being client id-s and values being the score values
        self.scores = {}

    def add_connected_client(self, client):
        """Add a client to the game."""
        self.scores[client.id] = 0
        self.connected_clients[client.id] = client

    def remove_connected_client(self, client_id):
        """Remove a client from the game."""
        self.connected_clients.pop(client_id)
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
        complete = self.board.is_solved()
        return complete
