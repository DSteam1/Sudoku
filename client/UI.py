from SudokuBoard import *
from Tkinter import Tk, Canvas, Frame, Button, BOTH, TOP, BOTTOM, LEFT, RIGHT, END,  Label, CENTER, Listbox, Entry
import tkMessageBox

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
        if True:  # TODO: check if connection successful
            self.main_view()
        else:
            tkMessageBox.showinfo("Error", "Error connecting to server")
            self.count += 1

    def nickname_view(self):
        self.window_resize(_WIDTH, _HEIGHT)
        self.empty_frame(self.frame_container)
        NicknameView(self.frame_container, self)

    def server_address_view(self):
        self.window_resize(_WIDTH, _HEIGHT)
        self.empty_frame(self.frame_container)
        ServerAddressView(self.frame_container, self)

    def main_view(self):
        self.window_resize(_WIDTH, _HEIGHT)
        self.empty_frame(self.frame_container)
        MainView(self.frame_container, self)

    def game_view(self):
        self.window_resize(_GAME_WIDTH, _GAME_HEIGHT)
        self.empty_frame(self.frame_container)
        GameView(self.frame_container, self)

    def empty_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def window_resize(self, width, height):
        self.root.minsize(width=width, height=height)


class GameView:
    def __init__(self, container, main_ui):
        self.main_ui = main_ui

        self.frame_left = Frame(container)
        self.frame_left.pack(side=LEFT, padx=20, pady=20)

        self.scoreFont = tkFont.Font(family="Helvetica", size=15)

        board_name = main_ui.board_name

        with open('%s.sudoku' % board_name, 'r') as boards_file:  # Open board file (temporary solution)
            game = SudokuGame(boards_file)
        game.start()  # Start game
        SudokuUI(self.frame_left, game)  # Display sudoku board

        self.frame_right = Frame(container)
        self.frame_right.pack(side=RIGHT, padx=20, pady=10)

        games_txt = Label(self.frame_right, text="Scoreboard")
        games_txt.pack(side=TOP)

        self.games_lb = Listbox(self.frame_right, bg="gray99", selectbackground="gray99", height=6)
        self.games_lb.bind("<<ListboxSelect>>", self.no_selection)
        self.games_lb.pack()
        self.fill_players()

        games_txt = Label(self.frame_right, text="My score: 16", font=self.scoreFont)
        games_txt.pack(pady=20)

        games_txt = Label(self.frame_right, text="", height=3)
        games_txt.pack()

        games_txt = Label(self.frame_right, text="Events")
        games_txt.pack()

        self.events_lb = Listbox(self.frame_right, bg="gray99", selectbackground="gray99", height=6, width=30)
        self.events_lb.bind("<<ListboxSelect>>", self.no_selection)
        self.events_lb.pack()
        self.fill_events()

        self.enterButton = Button(self.frame_right, text="Exit game", command=self.exit_game)
        self.enterButton.pack( padx=10, pady=10)

    def fill_players(self):
        for idx, val in enumerate(self.get_players()):  # Insert all games to the list
            self.games_lb.insert(idx, val)
        self.games_lb.pack()

    def no_selection(self, event):
        w = event.widget
        w.selection_clear(w.curselection())

    def get_players(self):
        return ["David: 10", "Shade: 15", "Bob 16", "You: 16"]

    def fill_events(self):
        for idx, val in enumerate(["You inserted 9 correctly: +1 pts", "You made a mistake: -1 pts",
                                   "David made a mistake: -1 pts"]):
            self.events_lb.insert(idx, val)

    def exit_game(self):
        self.main_ui.main_view()

class MainView:
    """
        Main UI responsible for handling user inputs and sudoku board viewing
    """
    def __init__(self, container, main_ui):
        self.main_ui = main_ui

        self.frame_left = Frame(container)
        self.frame_left.pack(side=LEFT, padx=20, pady=20)

        games_txt = Label(self.frame_left, text="Available games:")
        games_txt.pack()

        self.games_lb = Listbox(self.frame_left)
        self.games_lb.pack()
        self.fill_games()

        self.enterButton = Button(self.frame_left, text="Refresh", command=self.refresh_games)
        self.enterButton.pack(side=LEFT, padx=10, pady=10)

        self.connectButton = Button(self.frame_left, text="Connect", command=self.connect)
        self.connectButton.pack(side=LEFT, padx=10, pady=10)

        frame_right = Frame(container)
        frame_right.pack(side=LEFT, padx=20, pady=20)

        self.nicknameLabel = Label(frame_right, text="Amount of players:")
        self.nicknameLabel.pack()

        self.players_lb = Listbox(frame_right)
        for i in range(2, 5):  # Possible amounts of players
            self.players_lb.insert(i, str(i))
        self.players_lb.pack()

        self.enterButton = Button(frame_right, text="Create new game", command=self.create_new_game)
        self.enterButton.pack(padx=10, pady=10)

    def hide(self, widget):
        widget.pack_forget()

    def refresh_games(self):
        self.games_lb.delete(0, END)
        self.fill_games()

    def fill_games(self):
        for idx, val in enumerate(get_games()):  # Insert all games to the list
            self.games_lb.insert(idx, val)
        self.games_lb.pack()

    def connect(self):
        selected_game = self.games_lb.curselection()
        if len(selected_game) == 0:
            tkMessageBox.showinfo("Error", "No game selected")
        elif "TODO" == "Connection failed":
            tkMessageBox.showinfo("Error", "Connection error")
        else:
            print("Connecting")
            self.main_ui.game_view()

    def create_new_game(self):
        player_count = self.players_lb.curselection()
        if len(player_count) == 0:
            tkMessageBox.showinfo("Error", "Select the amount of players")
            return


class ServerAddressView:

    def __init__(self, container, application):
        self.container = container
        self.application = application

        self.nicknameLabel = Label(container, text="Welcome to Sudoku!")
        self.nicknameLabel.pack(side=TOP)

        self.nicknameLabel = Label(self.container, text="Enter Sudoku server address: ")
        self.nicknameLabel.pack(side=LEFT)

        self.entry = Entry(self.container, bd=5)
        self.entry.pack(side=LEFT)

        self.enterButton = Button(self.container, text="Connect", command=self.handle_enter)
        self.enterButton.pack(side=LEFT, padx=20, pady=20)

        self.entry.insert(0, "127.0.0.1")  # should specify default

    def handle_enter(self):  # Handle proceed button
        address = self.entry.get()
        self.application.server = address
        self.application.connect()

    def fill_nickname(self, evt):
        w = evt.widget
        idx = int(w.curselection()[0])
        self.entry.delete(0, END)
        self.entry.insert(0, w.get(idx))


class NicknameView:
    """
        Main UI responsible for handling user inputs and sudoku board viewing
    """
    def __init__(self, container, main_ui):
        self.main_ui = main_ui

        self.nicknameLabel = Label(container, text="Welcome to Sudoku!")
        self.nicknameLabel.pack(side=TOP)

        self.frame_left = Frame(container)
        self.frame_left.pack(side=LEFT, padx=20, pady=20)

        self.nicknameLabel = Label(self.frame_left, text="Enter nickname: ")
        self.nicknameLabel.pack(side=LEFT)

        self.entry = Entry(self.frame_left, bd=5)
        self.entry.pack(side=LEFT)

        self.enterButton = Button(self.frame_left, text="Proceed", command=self.handle_enter)
        self.enterButton.pack(side=LEFT, padx=20, pady=20)

        self.frame_right = Frame(container)
        self.frame_right.pack(side=RIGHT)

        self.nicknameLabel = Label(self.frame_right, text="Previously used names:")
        self.nicknameLabel.pack()

        nickname_lb = Listbox(self.frame_right)
        for idx, val in enumerate(read_usernames()):  # Insert all previously used usernames to list
            nickname_lb.insert(idx, val)
        nickname_lb.pack()
        nickname_lb.bind('<<ListboxSelect>>', self.fill_nickname)

    def handle_enter(self):  # Handle proceed button
        nickname = self.entry.get()
        if self.validate_nickname(nickname):
            save_username(nickname)  # Save new username to file
            print("Proceeding")
            self.main_ui.server_address_view()  # Show server screen

    def fill_nickname(self, evt):
        w = evt.widget
        idx = int(w.curselection()[0])
        self.entry.delete(0, END)
        self.entry.insert(0, w.get(idx))

    def validate_nickname(self, nickname):
        # TODO: Username validation, spaces are not allowed!!
        if len(nickname) == 0:
            tkMessageBox.showinfo("Error", "Too short nickname")
            return False
        elif len(nickname) > 8:
            tkMessageBox.showinfo("Error", "Too long nickname")
            return False
        return True


def read_usernames():
    # TODO: Username reading from file
    return ["evelknievel", "user1", "dima"]


def get_games():
    # TODO: Username reading from file
    return ["Good game 3/4", "Intermediate 1/4", "FF 4/4"]


def save_username(username):
    # TODO: Appending username to file if not added
    pass


if __name__ == '__main__':
    Application()
