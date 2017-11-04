from socket import error as socket_error

from constants import *


def assemble(message_type, content):
    character_count = len(message_type) + len(SEPARATOR) + len(content)
    if character_count > MSG_LENGTH:
        #TODO: handle messages with too large content. Probably not needed though.
        return
    message = message_type + SEPARATOR + str(content) + " " * (MSG_LENGTH - character_count)
    return message


def send(socket, message_type, content):
    message = assemble(message_type, content)
    parse(message)
    socket.sendall(message)


def parse(message):
    message_parts = message.split(";")
    message_type = message_parts[0]
    content = message_parts[1]
    return message_type, content


def receive(socket):
    try:
        message = socket.recv(MSG_LENGTH)
        return message
    except socket_error as err:
        raise err
