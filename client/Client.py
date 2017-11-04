from Tkinter import *
import logging
import tkMessageBox
from socket import AF_INET, SOCK_STREAM, socket
from socket import error as socket_error
from argparse import ArgumentParser

FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG,format=FORMAT)
LOG = logging.getLogger()

class NicknameDialog:
    def __init__(self, parent):
        self.parent = parent
        self.top = Toplevel(parent)

        self.nicknameLabel = Label(self.top, text="Nickname: ")
        self.nicknameLabel.pack(side=LEFT)

        self.entry = Entry(self.top, bd=5)
        self.entry.pack(side=LEFT)
        self.entry.insert(0, "nick")

        self.enterButton = Button(self.top, text="Enter", command=self.handleEnterButton)
        self.enterButton.pack(side=LEFT)

    #TODO: spaces are not allowed!!
    def handleEnterButton(self):
        nickname = self.entry.get()
        if(len(nickname) == 0):
            self.tooShortNicknameError()
        elif(len(nickname) > 8):
            self.tooLongNicknameError()
        else:
            self.parent.nickname = nickname
            self.top.destroy()

    def tooShortNicknameError(self):
        tkMessageBox.showinfo("Error", "Too short nickname")

    def tooLongNicknameError(self):
        tkMessageBox.showinfo("Error", "Too long nickname")

class ServerAddressDialog:
    def __init__(self, parent):
        self.parent = parent
        self.top = Toplevel(parent)

        self.serverAddressLabel = Label(self.top, text="Server address: ")
        self.serverAddressLabel.pack(side=LEFT)

        self.entry = Entry(self.top, bd=5)
        self.entry.insert(0, "127.0.0.1") #should specify default
        self.entry.pack(side=LEFT)

        self.connectButton = Button(self.top, text="Enter", command=self.handleEnterButton)
        self.connectButton.pack(side=LEFT)

    def handleEnterButton(self):
        server = self.entry.get()
        if(len(server) == 0):
            self.tooShortServerError()
        else:
            self.parent.server = server
            self.top.destroy()

    def tooShortServerError(self):
        self.top.tkMessageBox.showinfo("Error", "Please enter server address")

class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        n = NicknameDialog(self)
        self.wait_window(n.top)
        s = ServerAddressDialog(self)
        self.wait_window(s.top)

        if(self.tryCreateConnection()):
            print("Connection successful")


    def tryCreateConnection(self): #self.server is set in ServerAddressDialog
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
            tkMessageBox.showinfo("Error", "Could not connect to server. Closing the application")
            self.socket.close()
            self.master.destroy()
            return False


app = Application()
app.mainloop()
