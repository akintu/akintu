'''
Welcome screens implemented using Tkinter GUI library
'''

from Tkinter import *
import ttk

CLASSES = ('Barbarian', 'Dragoon', 'Weapon Master', 'Spellsword', 'Anarchist',
           'Marksman', 'Druid', 'Tactician', 'Ninja', 'Assassin', 'Shadow',
           'Nightblade', 'Battle Mage', 'Arcane Archer', 'Trickster',
           'Sorcerer')
RACES = ('Human', 'Dwarf', 'Elf', 'Halfling', 'Orc', 'Khajiit')


class WelcomeWindow(object):

    def __init__(self, master):
        style = ttk.Style()
        style.configure('TitleLabel.TLabel', font='helvetica 80 bold')
        self.frame = Frame()

        self.master = master
        # Set a variable which tells whether the Player completed the menus
        self.success = False
        self.charrace = StringVar()
        self.charclass = StringVar()
        self.charname = StringVar(value='Mysterious Adventurer')
        self.joinip = StringVar()
        self.portstr = StringVar(value='1337')
        self.port = 1337
        self.hosting = True
        self.loadingchar = False

        self.mainmenu()

    def _getmainmenu(self):
        frame = ttk.Frame(self.master, padding='100 40 100 100')
        # Create the widgets
        akintul = ttk.Label(frame, text='Akintu', style='TitleLabel.TLabel')
        newchar = ttk.Button(frame, text='New Character', command=self.newchar)
        loadchar = ttk.Button(frame, text='Load Character', command=self.loadchar)
        # Lay out the widgets
        akintul.grid(column=1, row=1, sticky=(N, W, E, S), padx=10, pady=50)
        newchar.grid(column=1, row=2, stick=(N, S), padx=10, pady=10)
        loadchar.grid(column=1, row=3, stick=(N, S), padx=10, pady=10)
        return frame

    def _getnewchar(self):
        frame = ttk.Frame(self.master, padding='50 50 50 50')
        # Create the widgets
        backb = ttk.Button(frame, text='Back', command=self.mainmenu)
        nextb = ttk.Button(frame, text='Next', command=self.playtype)
        classcombo = ttk.Combobox(frame, textvariable=self.charclass, values=CLASSES, state='readonly')
        racecombo = ttk.Combobox(frame, textvariable=self.charrace, values=RACES, state='readonly')
        classl = ttk.Label(frame, text='Class:')
        racel = ttk.Label(frame, text='Race:')
        namel = ttk.Label(frame, text='Name:')
        namebox = ttk.Entry(frame, textvariable=self.charname)
        # Lay out the widgets
        namel.grid(column=2, row=1, stick=W, padx=5, pady=5)
        namebox.grid(column=2, row=2, stick=(W, E), padx=5, pady=5)
        racel.grid(column=2, row=3, stick=W, padx=5, pady=5)
        racecombo.grid(column=2, row=4, stick=(N, S), padx=5, pady=5)
        classl.grid(column=2, row=5, stick=W, padx=5, pady=5)
        classcombo.grid(column=2, row=6, stick=(N, S), padx=5, pady=5)
        backb.grid(column=1, row=7, stick=(N, S), padx=20, pady=20)
        nextb.grid(column=3, row=7, stick=(N, S), padx=20, pady=20)
        return frame

    def _getplaytype(self):
        frame = ttk.Frame(self.master, padding='50 50 50 50')
        # Create the widgets
        backb = ttk.Button(frame, text='Back', command=self.prevplaytype)
        joinb = ttk.Button(frame, text='Join Game', command=self.joingame)
        hostb = ttk.Button(frame, text='Host Game', command=self.hostgame)
        # Lay out the widgets
        joinb.grid(column=1, row=1, stick=(N, S), padx=5, pady=5)
        hostb.grid(column=1, row=2, stick=(N, S), padx=5, pady=5)
        backb.grid(column=1, row=3, stick=(N, S), padx=20, pady=20)
        return frame

    def _getjoingame(self):
        frame = ttk.Frame(self.master, padding='50 50 50 50')
        # Create the widgets
        backb = ttk.Button(frame, text='Back', command=self.playtype)
        finishb = ttk.Button(frame, text='Start', command=self.finishjoin)
        ipl = ttk.Label(frame, text='Host IP:')
        portl = ttk.Label(frame, text='Host Port:')
        ipbox = ttk.Entry(frame, textvariable=self.joinip)
        portbox = ttk.Entry(frame, textvariable=self.portstr)
        # Lay out the widgets
        ipl.grid(column=2, row=1, stick=W, padx=5, pady=5)
        ipbox.grid(column=2, row=2, stick=(W, E), padx=5, pady=5)
        portl.grid(column=2, row=3, stick=W, padx=5, pady=5)
        portbox.grid(column=2, row=4, stick=(W, E), padx=5, pady=5)
        backb.grid(column=1, row=5, stick=(N, S), padx=20, pady=20)
        finishb.grid(column=3, row=5, stick=(N, S), padx=20, pady=20)
        return frame

    def mainmenu(self):
        self.frame.pack_forget()
        self.frame = self._getmainmenu()
        self.frame.pack()

    def newchar(self):
        self.loadingchar = False
        self.frame.pack_forget()
        self.frame = self._getnewchar()
        self.frame.pack()
        self.prevplaytype = self.newchar

    def loadchar(self):
        #TODO implement loading a character
        self.loadingchar = True

    def playtype(self):
        if self.charrace.get() == '' or self.charclass.get() == '':
            return
        self.frame.pack_forget()
        self.frame = self._getplaytype()
        self.frame.pack()

    def joingame(self):
        self.frame.pack_forget()
        self.frame = self._getjoingame()
        self.frame.pack()

    def hostgame(self):
        #TODO implement hosting a game (default port 1337)
        pass

if __name__ == '__main__':
    root = Tk()
    root.title('Akintu')
    window = WelcomeWindow(root)
    root.mainloop()
