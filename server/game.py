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
        self.connected_clients = []
        # Dictionary with keys being client id-s and values being the score values
        self.scores = {}

    def add_connected_client(self, client):
        """Add a client to the game."""
        self.connected_clients.append(client)

    def remove_connected_client(self, client_index):
        """Remove a client from the game."""
        index = self.connected_clients.pop(client_index)
        LOG.debug("Removed client with index " + str(index) + " from game")

    def get_connected_clients(self):
        """Get the list of connected clients in the game."""
        return self.connected_clients

    def update_board(self, row, column, digit, client_id):
        """Attempt to update the board attached to this game instance."""
        score_change = self.board.add_number(row, column, digit)
        if client_id in self.scores:
            self.scores[client_id] += score_change
        else:
            LOG.debug("Game could not update the score of client " + str(client_id) +
                      " since it is not in the scores dictionary.")
        return score_change

    def get_board(self):
        """Get the current board."""
        return board

    def broadcast_new_state(self):
        """Send the new board state to all clients connected to this game instance."""
        LOG.debug("Sending new board states to clients")
        for client in self.connected_clients:
            client.send_new_board_state(board)