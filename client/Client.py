from Tkinter import *
import logging
import tkMessageBox
from socket import AF_INET, SOCK_STREAM, socket
from socket import error as socket_error
from argparse import ArgumentParser
import OtherViews as OV
import MainView as MV
import GameView as GV

from common.utils import init_logging
from common.constants import *
import common.protocol as protocol

LOG = init_logging()

_WIDTH = 666
_HEIGHT = 300
_GAME_HEIGHT = 600
_GAME_WIDTH = 800

class Application():
    def __init__(self):
        self.root = Tk()
        self.root.minsize(width=_WIDTH, height=_HEIGHT)

        self.root.title("Sudoku")

        self.frame_container = Frame(self.root)
        self.frame_container.place(relx=0.5, rely=0.5, anchor=CENTER)

        self.board_name = "debug"
        #  self.board_name = "n00b"

        self.nickname_view()  # Show nickname initially
        #  self.game_view()  # Replace for debugging

        self.root.mainloop()

        # After exiting from main loop
        print("Closing connections")


        # Connect to server

    def connect(self):
        success = self.tryCreateConnection()
        if success:
            self.main_view()
        else:
            tkMessageBox.showinfo("Error", "Error connecting to server")
            self.count += 1

    def tryCreateConnection(self):  # self.server is set in ServerAddressDialog
        LOG.info("Connecting to %s." % self.server)
        port = 7777

        try:
            self.socket = socket(AF_INET, SOCK_STREAM)
            LOG.info("TCP socket created")
            server_address = (self.server, port)

            self.socket.connect(server_address)
            LOG.info('Socket connected to %s:%d' % self.socket.getpeername())
            LOG.info('Local end-point is  bound to %s:%d' % self.socket.getsockname())
            return True
        except:
            self.socket.close()
            self.master.destroy()
            return False

    def get_games(self):
        LOG.info("Requesting available games from server")
        protocol.send(self.socket, REQ_GAMES_MSG, "")
        LOG.info("Waiting respnse for games request")
        message = protocol.receive(self.socket)
        message_type, content = protocol.parse(message)
        LOG.info("Received response with type " + message_type)
        if(message_type == GAME_LIST_MSG):
            return content.split(CONTENT_SEPARATOR)
        else:
            #TODO: HANDLE PROBLEMS
            pass

    def create_game(self):
        LOG.info("Requesting new game creation")
        protocol.send(self.socket, CREATE_GAME_MSG, "")
        LOG.info("Waiting respnse for new game creation")
        message = protocol.receive(self.socket)
        message_type, content = protocol.parse(message)
        LOG.info("Received response with type " + message_type)
        if(message_type == BOARD_STATE_MSG):
            digits, cell_types = protocol.separate_board_state_msg_content(content)
            return digits
        else:
            # TODO: HANDLE PROBLEMS
            pass

    def insert_number(self, row, column, digit):
        LOG.info("Requesting number insertion")
        msg = protocol.assemble_insert_msg_content(row, column, digit)
        protocol.send(self.socket, INSERT_MSG, msg)
        LOG.info("Waiting response for number insertion")
        message = protocol.receive(self.socket)
        message_type, content = protocol.parse(message)
        LOG.info("Received response with type " + message_type)
        print(content)
        if(message_type == SEND_SCORES_MSG):
            return True
        else:
            return False

    # VIEWS

    def nickname_view(self):
        self.window_resize(_WIDTH, _HEIGHT)
        self.empty_frame(self.frame_container)
        OV.NicknameView(self.frame_container, self)

    def server_address_view(self):
        self.window_resize(_WIDTH, _HEIGHT)
        self.empty_frame(self.frame_container)
        OV.ServerAddressView(self.frame_container, self)

    def main_view(self):
        self.selected_game = None
        self.window_resize(_WIDTH, _HEIGHT)
        self.empty_frame(self.frame_container)
        MV.MainView(self.frame_container, self, self.get_games())

    def game_view(self, selected_game):
        if(selected_game == None):
            game = self.create_game()
        else:
            #TODO: JOIN WITH EXISTING GAME
            pass

        self.window_resize(_GAME_WIDTH, _GAME_HEIGHT)
        self.empty_frame(self.frame_container)
        GV.GameView(self.frame_container, self, game)

    def empty_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def window_resize(self, width, height):
        self.root.minsize(width=width, height=height)


if __name__ == '__main__':
    Application()

