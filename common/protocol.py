from socket import error as socket_error

from constants import *


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
    """Assemble a message conveying the current board state."""
    rows = board.ROWS
    content = ""
    for row in rows:
        for cell in row:
            content += str(cell.get_value())
            content += CONTENT_SEPARATOR
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


def parse_board_state_msg_content(content):
    """Parse a board state message."""
    #TODO: parse board state message for client
    return


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
