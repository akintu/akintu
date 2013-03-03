'''
Welcome screens implemented using Tkinter GUI library
'''

from Tkinter import *
import ttk
import socket
import const
import sys
import re

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
        self.loadingworld = False
        self.loadingworldvar = StringVar()
        self.worldseed = StringVar()
        self.worldsave = StringVar()

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

    def _gethostgame(self):
        frame = ttk.Frame(self.master, padding='50 50 50 50')

        # Try to get your ip
        localip = ''
        try:
            fullhtml = urllib2.urlopen('http://www.internetfrog.com/myinternet/traceroute/').read()
            match = re.search('(?<=Your IP is: )\d\+\.\d\+\.\d\+\.\d\+', fullhtml)
            localip = match.group(0)
        except:
            pass
        if not localip:
            try:
                localip = socket.gethostbyname(socket.gethostname())
            except:
                pass
        if not localip:
            localip = '127.0.0.1'

        # Create the widgets
        backb = ttk.Button(frame, text='Back', command=self.playtype)
        finishb = ttk.Button(frame, text='Start', command=self.finishhost)
        ipl = ttk.Label(frame, text='Your IP address:  ' + localip)
        portl = ttk.Label(frame, text='Port to listen on:')
        portbox = ttk.Entry(frame, textvariable=self.portstr)
        newworldr = ttk.Radiobutton(frame, text='New World', variable=self.loadingworldvar, value='New World')
        loadworldr = ttk.Radiobutton(frame, text='Load World', variable=self.loadingworldvar, value='Load World')
        newworldbox = Entry(frame, textvariable=self.worldseed)
        loadworldcombo = ttk.Combobox(frame, textvariable=self.worldsave, values=(), state='readonly')
        # Lay out the widgets
        ipl.grid(column=2, row=1, stick=W, padx=5, pady=5)
        portl.grid(column=2, row=2, stick=W, padx=5, pady=5)
        portbox.grid(column=2, row=3, stick=(W, E), padx=5, pady=5)
        newworldr.grid(column=1, row=4, stick=W, padx=5, pady=5)
        loadworldr.grid(column=1, row=5, stick=W, padx=5, pady=5)
        newworldbox.grid(column=2, row=4, stick=(W, E), padx=5, pady=5)
        loadworldcombo.grid(column=2, row=5, stick=(W, E), padx=5, pady=5)
        backb.grid(column=1, row=6, stick=(N, S), padx=20, pady=20)
        finishb.grid(column=3, row=6, stick=(N, S), padx=20, pady=20)
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
        self.frame.pack_forget()
        self.frame = self._gethostgame()
        self.frame.pack()

    def finishjoin(self):
        try:
            self.port = int(self.portstr.get())
        except ValueError:
            return
        if self.joinip.get().strip() == '':
            return

        self.hosting = False
        self.success = True
        self.frame.quit()

    def finishhost(self):
        try:
            self.port = int(self.portstr.get())
        except ValueError:
            return
        if self.loadingworldvar.get() == '' or self.worldseed.get() == '':
            return
        if self.loadingworldvar.get() == 'New World':
            self.loadingworld = False
        else:
            self.loadingworld = True
            return

        self.hosting = True
        self.success = True
        self.frame.quit()


def runwelcome():
    root = Tk()
    root.title('Akintu')
    window = WelcomeWindow(root)
    root.mainloop()
    try:
        root.destroy()
    except:
        sys.exit()
    ret = []

    if window.loadingchar:
        ret.append('')  # TODO will be window.charsave.get() instead of ''
    else:
        ret.append((window.charname.get(), window.charrace.get(), window.charclass.get()))

    if window.hosting:
        if window.loadingworld:
            ret.append(window.worldsave.get())
        else:
            ret.append({const.SEED_KEY: window.worldseed.get()})
        ret.append(None)
    else:
        ret.append(None)
        ret.append(window.joinip.get())

    ret.append(window.port)

    # Return (player, state, ip, port)
    return tuple(ret)

if __name__ == '__main__':
    runwelcome()
