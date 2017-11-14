from mtTkinter import *
import tkMessageBox
from socket import AF_INET, SOCK_STREAM, socket, error
import OtherViews as OV
import MainView as MV
import GameView as GV
from threading import Thread

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

        self.existing_main_view = None
        self.existing_game_view = None
        self.game_started = False
        self.game_open = False

        self.nickname_view()  # Show nickname initially

        self.root.mainloop()

        # After exiting from main loop
        self.exit_game()
        self.disconnect()

    # Connect to server
    def connect(self):
        success = self.tryCreateConnection()
        if success:
            self.listener = ClientListener(self.socket, self)
            self.send_nickname()
            self.get_games()
        else:
            tkMessageBox.showinfo("Error", "Error connecting to server")
            self.count += 1

    def disconnect(self):
        try:
            self.socket.fileno()
        except:
            return
        LOG.info("Disconnected from server.")
        self.socket.close()

    def tryCreateConnection(self):
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

    def send_nickname(self):
        LOG.info("Sending nickname to server")
        protocol.send(self.socket, NICKNAME_MSG, self.nickname)
        LOG.info("Client is not expecting response for nickname message")

    def get_games(self):
        LOG.info("Requesting available games from server")
        protocol.send(self.socket, REQ_GAMES_MSG, "")
        LOG.info("Waiting response for games request")

    def create_game(self, players):
        LOG.info("Requesting new game creation")
        protocol.send(self.socket, CREATE_GAME_MSG, players)
        self.game_started = False
        LOG.info("Waiting response for new game creation")

    def join_game(self, id):
        LOG.info("Requesting joining a game")
        protocol.send(self.socket, JOIN_GAME_MSG, str(id))
        LOG.info("Waiting response for join game")

    def insert_number(self, row, column, digit):
        LOG.info("Requesting number insertion")
        msg = protocol.assemble_insert_msg_content(row, column, digit)
        protocol.send(self.socket, INSERT_MSG, msg)
        LOG.info("Waiting response for number insertion")

    # VIEWS

    def nickname_view(self):
        self.window_resize(_WIDTH, _HEIGHT)
        self.empty_frame(self.frame_container)
        OV.NicknameView(self.frame_container, self)

    def server_address_view(self):
        self.window_resize(_WIDTH, _HEIGHT)
        self.empty_frame(self.frame_container)
        OV.ServerAddressView(self.frame_container, self)

    def main_view(self, games):
        self.selected_game = None
        self.window_resize(_WIDTH, _HEIGHT)
        self.empty_frame(self.frame_container)
        self.existing_main_view = MV.MainView(self.frame_container, self, games)

    def update_main_view(self, games):
        if self.existing_main_view is None:
            self.main_view(games)
        else:
            self.existing_main_view.games = games
            self.existing_main_view.fill_games()

    def game_join_fault(self):
        if self.existing_main_view is not None:
            self.existing_main_view.display_join_fault()

    def game_full_fault(self):
        if self.existing_main_view is not None:
            self.existing_main_view.display_game_full()

    def game_view(self, digitsTypes = "", scores = ""):
        self.window_resize(_GAME_WIDTH, _GAME_HEIGHT)
        self.empty_frame(self.frame_container)
        self.existing_game_view = GV.GameView(self.frame_container, self, digitsTypes, scores, self.game_started)
        self.existing_main_view = None

    def update_game_view(self, digitsTypes, scores):
        if self.existing_game_view is None:
            self.game_view(digitsTypes, scores)
        else:
            if digitsTypes != "" :
                self.existing_game_view.update_board(digitsTypes)
            if scores != "":
                self.existing_game_view.fill_players(scores)

    def start_game(self):
        self.game_started = True
        if self.existing_game_view is not None:
            self.existing_game_view.hide_waiting_txt()

    def exit_game(self):
        LOG.info("Sending exit game message")
        protocol.send(self.socket, EXIT_GAME_MSG, "")
        LOG.info("Client is not expecting response for exit game message")
        self.game_open = False
        self.existing_game_view = None
        self.get_games()

    def show_end(self, content):
        self.existing_game_view.show_end(content)

    def empty_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def window_resize(self, width, height):
        self.root.minsize(width=width, height=height)


class ClientListener(Thread):
    def __init__(self, socket, app):
        Thread.__init__(self)
        self.socket = socket
        self.app = app
        self.daemon = True
        self.start()

    def run(self):
            try:
                while True:
                    msg = protocol.receive(self.socket)
                    if msg:
                        self.parse_and_handle_message(msg)
                    else:
                        self.shut_down()
                        break
            except error:
                return

    def parse_and_handle_message(self, msg):
        message_type, content = protocol.parse(msg)
        LOG.info("Received response with type " + message_type)
        if  message_type == GAME_LIST_MSG:
            games = content.split(CONTENT_SEPARATOR)
            self.app.update_main_view(games)
            LOG.info("Handled response with type " + message_type)
        elif message_type == SUCCESSFUL_JOIN_MSG:
            self.app.game_started = False
            LOG.info("Handled response with type " + message_type)
        elif message_type == START_GAME_MSG:
            self.app.start_game()
            LOG.info("Handled response with type " + message_type)
        elif message_type == BOARD_STATE_MSG:
            if self.app.game_open:
                digits, types = protocol.separate_board_state_msg_content(content)
                self.app.update_game_view((digits, types), "")
            LOG.info("Handled response with type " + message_type)
        elif message_type == SEND_SCORES_MSG:
            if self.app.game_open:
                scores = protocol.parse_score_message(content)
                self.app.update_game_view("", scores)
            LOG.info("Handled response with type " + message_type)
        elif message_type == SUCCESSFUL_INS_MSG:
            LOG.info("Handled response with type " + message_type + ": " + content)
        elif message_type == FAILED_INS_MSG:
            LOG.info("Handled response with type " + message_type + ": " + content)
        elif message_type == GAME_OVER_VICTORY_MSG:
            if self.app.game_open:
                self.app.show_end(content)
            LOG.info("Handled response with type " + message_type + ": " + content)
        elif message_type == GAME_OVER_LOSS_MSG:
            if self.app.game_open:
                self.app.show_end(content)
            LOG.info("Handled response with type " + message_type + ": " + content)
        elif message_type == FAILED_JOIN_MSG:
            self.app.game_join_fault()
            LOG.info("Handled response with type " + message_type + ": " + content)
        elif message_type == GAME_FULL_MSG:
            self.app.game_full_fault()
            LOG.info("Handled response with type " + message_type + ": " + content)
        else:
            LOG.info("Unknown message with type " + message_type)
            pass

    def shut_down(self):
        self.app.disconnect()





if __name__ == '__main__':
    Application()

