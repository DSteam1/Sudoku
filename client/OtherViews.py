from SudokuBoard import *
from Tkinter import Tk, Canvas, Frame, Button, BOTH, TOP, BOTTOM, LEFT, RIGHT, END,  Label, CENTER, Listbox, Entry
import tkMessageBox


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
            self.main_ui.nickname = nickname
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

def save_username(username):
    # TODO: Appending username to file if not added
    pass