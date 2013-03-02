'''
Welcome screens implemented using Tkinter GUI library
'''

from Tkinter import *
import ttk


class WelcomeWindow(object):

    def __init__(self, master):
        self.master = master
        self.mainmenu()

    def _getmainmenu(self):
        frame = ttk.Frame(self.master, padding='100 40 100 100')
        ttk.Style().configure('TitleLabel.TLabel', font='helvetica 80 bold')
        akintul = ttk.Label(frame, text='Akintu', style='TitleLabel.TLabel')
        akintul.grid(column=1, row=1, sticky=(N, W, E, S), padx=10, pady=50)
        newchar = ttk.Button(frame, text='New Character', command=self.newchar)
        newchar.grid(column=1, row=2, stick=(N, S), padx=10, pady=10)
        loadchar = ttk.Button(frame, text='Load Character', command=self.loadchar)
        loadchar.grid(column=1, row=3, stick=(N, S), padx=10, pady=10)
        return frame

    def mainmenu(self):
        self.frame = self._getmainmenu()
        self.frame.grid(column=0, row=0, stick=(N, W, E, S))
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)

    def newchar(self):
        pass

    def loadchar(self):
        pass

if __name__ == '__main__':
    root = Tk()
    root.title("Akintu")
    window = WelcomeWindow(root)
    root.mainloop()
