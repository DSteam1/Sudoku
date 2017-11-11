from SudokuBoard import *
from Tkinter import Tk, Canvas, Frame, Button, BOTH, TOP, BOTTOM, LEFT, RIGHT, END,  Label, CENTER, Listbox, Entry
import tkMessageBox

_WIDTH = 666
_HEIGHT = 300
_GAME_HEIGHT = 600
_GAME_WIDTH = 800

class GameView:
    def __init__(self, container, main_ui, board_string):
        self.main_ui = main_ui

        self.frame_left = Frame(container)
        self.frame_left.pack(side=LEFT, padx=20, pady=20)

        self.scoreFont = tkFont.Font(family="Helvetica", size=15)

        game = SudokuGame(board_string)
        game.start()  # Start game
        SudokuUI(self.frame_left, game, main_ui)  # Display sudoku board

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
