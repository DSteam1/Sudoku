from socket import error as socket_error

from constants import *


"""
Format of different messages
Messages never end with a separator
() are used to group together recurring parts here for clarity. They are NOT part of the actual messages.

Generic message
GENERIC_MSG + SEPARATOR + some_string

Insert message
INSERT_MSG + SEPARATOR + row + CONTENT_SEPARATOR + column + CONTENT_SEPARATOR + cell_value_to_be_inserted

Board state message
First part includes the values of all cells row by row. Second part includes the types of all cells row by row.
BOARD_STATE_MSG + SEPARATOR + (cell_value + CONTENT_SEPARATOR) + (cell_value + ...) until all values are here ... + 
+ SCORE_PLAYER_SEPARATOR + (cell_type + CONTENT_SEPARATOR) + (cell_type + CONTENT_SEPARATOR) + ... until all types are here

Game (id) list request message
REQ_GAMES_MSG + SEPARATOR + ?

Game list message
GAME_LIST_MSG + SEPARATOR + (game_id + CONTENT_SEPARATOR) + (game_id + CONTENT_SEPARATOR) + ... + game_id

Join game request message
JOIN_GAME_MSG + SEPARATOR + game_id

Create game request message
CREATE_GAME_MSG + SEPARATOR + ?

Score sending message
SEND_SCORES_MSG + SEPARATOR + (client_id + SCORE_PLAYER_SEPARATOR + client_score + CONTENT_SEPARATOR) + (client_id + ...

Successful join message
SUCCESSFUL_JOIN_MSG + SEPARATOR + some_string

Client disconnection request message
CLIENT_DISCONNECT_MSG + SEPARATOR + some_string

Failed game join message
FAILED_JOIN_MSG + SEPARATOR + some_string

Successful insert message
SUCCESSFUL_INS_MSG + SEPARATOR + some_string

Failed insert message
FAILED_INS_MSG + SEPARATOR + some_string
"""


def assemble(message_type, content):
    """Assemble a message."""
    character_count = len(message_type) + len(SEPARATOR) + len(content)
    if character_count > MSG_LENGTH:
        #TODO: handle messages with too large content. Probably not needed though.
        return
    message = message_type + SEPARATOR + str(content) + " " * (MSG_LENGTH - character_count)
    return message


def assemble_insert_msg_content(row, column, digit):
    """Assemble a digit insertion message."""
    return str(row) + CONTENT_SEPARATOR + str(column) + CONTENT_SEPARATOR + str(digit)


def assemble_board_state_msg_content(board):
    """
    Assemble a message conveying the current board state.
    The first half contains the digits and the second half contains values 1 and 2 depending on
    whether the cell is pre-entered or user-entered.
    """
    rows = board.ROWS
    content = ""
    for row in rows:
        for cell in row:
            content += str(cell.get_value())
            content += CONTENT_SEPARATOR
    content = content[:-1]
    content += SCORE_PLAYER_SEPARATOR
    for row in rows:
        for cell in row:
            content += str(cell.type)
            content += CONTENT_SEPARATOR
    content = content[:-1]
    return content


def assemble_send_scores_msg_content(scores):
    """Assemble a message containing the current scores of players."""
    content = ""
    for player in scores:
        content += (str(player) + SCORE_PLAYER_SEPARATOR + str(scores[player]) + CONTENT_SEPARATOR)
    content = content[:-1]
    return content


def parse(message):
    """Parse a message."""
    message_parts = message.split(";")
    message_type = message_parts[0]
    content = message_parts[1]
    return message_type, content


def parse_insert_msg_content(content):
    """Parse a digit insertion message."""
    content_parts = content.split(CONTENT_SEPARATOR)
    row = int(content_parts[0])
    column = int(content_parts[1])
    digit = int(content_parts[2])
    return row, column, digit

def parse_score_message(content):
    content_parts = content.split(CONTENT_SEPARATOR)
    return content_parts


def separate_board_state_msg_content(content):
    """Separate a board state message into two main parts."""
    parts = content.split(SCORE_PLAYER_SEPARATOR)
    digits = parts[0]
    cell_types = parts[1]
    return digits, cell_types


def send(socket, message_type, content):
    """Send a message."""
    message = assemble(message_type, content)
    parse(message)
    socket.sendall(message)


def receive(socket):
    """Receive a message."""
    try:
        message = socket.recv(MSG_LENGTH)
        return message
    except socket_error as err:
        raise err
