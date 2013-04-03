'''
Welcome screens implemented using Tkinter GUI library
'''

from Tkinter import *
import ttk
import socket
import const
import sys
import os
import glob
import re
import urllib2

savesprefix = os.path.join('res', 'saves', 'characters')
if not os.path.exists(savesprefix):
    os.makedirs(savesprefix)
savesprefix = os.path.join('res', 'saves', 'worlds')
if not os.path.exists(savesprefix):
    os.makedirs(savesprefix)

IPFILENAME = os.path.join('res', 'ip_history.txt')
if os.path.exists(IPFILENAME):
    try:
        with open(IPFILENAME, 'r') as ipfile:
            IP = tuple(ipfile.readlines()[::-1][:5])
    except Exception as e:
        print 'Could not load ip file: ', IPFILENAME
        print e
        IP = ()
else:
    IP = ()
CLASSES = ('Assassin', 'Barbarian', 'Dragoon', 'Weapon Master', 'Spellsword',
           'Marksman', 'Druid', 'Tactician', 'Ninja', 'Anarchist', 'Shadow',
           'Nightblade', 'Battle Mage', 'Arcane Archer', 'Trickster',
           'Sorcerer')
RACES = ('Human', 'Dwarf', 'Elf', 'Halfling', 'Orc')
savesprefix = os.path.join('res', 'saves', 'characters')
CHARSAVES = [path.lstrip(savesprefix).lstrip(os.path.sep) for path in
             glob.glob(os.path.join(savesprefix, '*.akinc'))]
CHARSAVESWIDTH = len(max(CHARSAVES, key=len)) if CHARSAVES else 10
savesprefix = os.path.join('res', 'saves', 'worlds')
WORLDSAVES = [path.lstrip(savesprefix).lstrip(os.path.sep) for path in
              glob.glob(os.path.join(savesprefix, '*.akinw'))]
WORLDSAVESWIDTH = len(max(WORLDSAVES, key=len)) if WORLDSAVES else 10


class WelcomeWindow(object):

    def __init__(self, master):
        style = ttk.Style()
        style.configure('TitleLabel.TLabel', font='helvetica 80 bold')
        self.frame = Frame()

        self.master = master
        # Set a variable which tells whether the Player completed the menus
        self.success = False
        self.charrace = StringVar(value=RACES[0])
        self.charclass = StringVar(value=CLASSES[0])
        self.charname = StringVar(value='Mysterious Adventurer')
        self.charsave = StringVar(value='')
        self.joinip = StringVar()
        self.portstr = StringVar(value='1337')
        self.port = 1337
        self.hosting = True
        self.loadingchar = False
        self.loadingworld = False
        self.loadingworldvar = StringVar(value='New World')
        self.worldseed = StringVar(value='Correct Horse Battery Staple')
        self.worldsave = StringVar(value='')
        self.turnlengthstr = StringVar(value='')
        self.turnlength = -1
        self.ironman = BooleanVar(value=False)
        self.hardcore = BooleanVar(value=False)

        self.mainmenu()

    def _getmainmenu(self):
        frame = ttk.Frame(self.master, padding='100 40 100 100')
        # Create the widgets
        akintul = ttk.Label(frame, text='Akintu', style='TitleLabel.TLabel')
        newchar = ttk.Button(frame, text='New Character', command=self.newchar)
        loadchar = ttk.Button(frame,
                              text='Load Character',
                              command=self.loadchar)
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
        classcombo = ttk.Combobox(frame,
                                  textvariable=self.charclass,
                                  values=CLASSES,
                                  state='readonly')
        racecombo = ttk.Combobox(frame,
                                 textvariable=self.charrace,
                                 values=RACES,
                                 state='readonly')
        classl = ttk.Label(frame, text='Class:')
        racel = ttk.Label(frame, text='Race:')
        namel = ttk.Label(frame, text='Name:')
        namebox = ttk.Entry(frame, textvariable=self.charname)
        ironmancheck = ttk.Checkbutton(frame,
                                       text='Iron Man Mode',
                                       variable=self.ironman,
                                       onvalue=True,
                                       offvalue=False)
        hardcorecheck = ttk.Checkbutton(frame,
                                        text='Hardcore Mode',
                                        variable=self.hardcore,
                                        onvalue=True,
                                        offvalue=False)
        # Lay out the widgets
        namel.grid(column=2, row=1, stick=W, padx=5, pady=5)
        namebox.grid(column=2, row=2, stick=(W, E), padx=5, pady=5)
        racel.grid(column=2, row=3, stick=W, padx=5, pady=5)
        racecombo.grid(column=2, row=4, stick=(N, S), padx=5, pady=5)
        classl.grid(column=2, row=5, stick=W, padx=5, pady=5)
        classcombo.grid(column=2, row=6, stick=(N, S), padx=5, pady=5)
        ironmancheck.grid(column=2, row=7, stick=W, padx=5, pady=5)
        hardcorecheck.grid(column=2, row=8, stick=W, padx=5, pady=5)
        backb.grid(column=1, row=9, stick=(N, S), padx=20, pady=20)
        nextb.grid(column=3, row=9, stick=(N, S), padx=20, pady=20)
        return frame

    def _getloadchar(self):
        frame = ttk.Frame(self.master, padding='50 50 50 50')
        # Create the widgets
        backb = ttk.Button(frame, text='Back', command=self.mainmenu)
        nextb = ttk.Button(frame, text='Next', command=self.playtype)
        savel = ttk.Label(frame, text='Load Character:')
        savecombo = ttk.Combobox(frame,
                                 textvariable=self.charsave,
                                 values=CHARSAVES,
                                 state='readonly',
                                 width=CHARSAVESWIDTH)
        # Lay out the widgets
        savel.grid(column=2, row=1, stick=W, padx=5, pady=5)
        savecombo.grid(column=2, row=2, stick=(N, S), padx=5, pady=5)
        backb.grid(column=1, row=3, stick=(N, S), padx=20, pady=20)
        nextb.grid(column=3, row=3, stick=(N, S), padx=20, pady=20)
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
        ipcombobox = ttk.Combobox(frame, textvariable=self.joinip, values=IP)
        portbox = ttk.Entry(frame, textvariable=self.portstr)
        # Lay out the widgets
        ipl.grid(column=2, row=1, stick=W, padx=5, pady=5)
        ipcombobox.grid(column=2, row=2, stick=(W, E), padx=5, pady=5)
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
            url = 'http://www.internetfrog.com/myinternet/traceroute/'
            fullhtml = urllib2.urlopen(url).read()
            match = re.search('(?<=Your IP is: )\d+\.\d+\.\d+\.\d+', fullhtml)
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
        newworldr = ttk.Radiobutton(frame,
                                    text='New World',
                                    variable=self.loadingworldvar,
                                    value='New World')
        loadworldr = ttk.Radiobutton(frame,
                                     text='Load World',
                                     variable=self.loadingworldvar,
                                     value='Load World')
        newworldbox = Entry(frame, textvariable=self.worldseed)
        loadworldcombo = ttk.Combobox(frame,
                                      textvariable=self.worldsave,
                                      values=WORLDSAVES,
                                      state='readonly')
        turnlengthbox = Entry(frame, textvariable=self.turnlengthstr)
        turnlengthl = ttk.Label(frame, text='Turn length (empty for infinite)')
        # Lay out the widgets
        ipl.grid(column=2, row=1, stick=W, padx=5, pady=5)
        portl.grid(column=2, row=2, stick=W, padx=5, pady=5)
        portbox.grid(column=2, row=3, stick=(W, E), padx=5, pady=5)
        turnlengthl.grid(column=2, row=4, stick=W, padx=5, pady=5)
        turnlengthbox.grid(column=2, row=5, stick=(W, E), padx=5, pady=5)
        newworldr.grid(column=1, row=6, stick=W, padx=5, pady=5)
        loadworldr.grid(column=1, row=7, stick=W, padx=5, pady=5)
        newworldbox.grid(column=2, row=6, stick=(W, E), padx=5, pady=5)
        loadworldcombo.grid(column=2, row=7, stick=(W, E), padx=5, pady=5)
        backb.grid(column=1, row=8, stick=(N, S), padx=20, pady=20)
        finishb.grid(column=3, row=8, stick=(N, S), padx=20, pady=20)
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
        self.loadingchar = True
        self.frame.pack_forget()
        self.frame = self._getloadchar()
        self.frame.pack()
        self.prevplaytype = self.loadchar

    def playtype(self):
        if not self.loadingchar:
            if self.charrace.get() == '' or self.charclass.get() == '':
                return
        else:
            if self.charsave.get() == '':
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
            if self.turnlengthstr.get() == '':
                self.turnlength = -1
            else:
                self.turnlength = int(self.turnlengthstr.get())
                if self.turnlength <= 0:
                    self.turnlength = -1
        except ValueError:
            print 'Bad port number, try again.'
            return
        if self.loadingworldvar.get() == '':
            return
        if self.loadingworldvar.get() == 'New World':
            if self.worldseed.get() == '':
                return
            self.loadingworld = False
        else:
            if self.worldsave.get() == '':
                return
            self.loadingworld = True

        self.hosting = True
        self.success = True
        self.frame.quit()


def runwelcome():
    '''
    Runs the welcome screens, returning a tuple of values

    Returns:
        (player, state, ip, port, turnlength, ironman, hardcore)
    '''
    root = Tk()
    root.title('Akintu')
    window = WelcomeWindow(root)
    root.mainloop()
    try:
        root.destroy()
    except:
        sys.exit()
    if not window.success:
        raise Exception('Something went wrong with the welcome screens. '
                        'Aborting...')
    ret = []

    if window.loadingchar:
        ret.append(window.charsave.get())
    else:
        ret.append((window.charname.get(),
                    window.charrace.get(),
                    window.charclass.get()))

    if window.hosting:
        if window.loadingworld:
            ret.append(window.worldsave.get())
        else:
            ret.append({const.SEED_KEY: window.worldseed.get()})
        ret.append(None)
    else:
        ret.append(None)
        ret.append(window.joinip.get())
        ips = list(IP)[::-1]
        if window.joinip.get() + '\n' not in ips:
            ips.append(window.joinip.get() + '\n')
        with open(IPFILENAME, 'w') as ipfile:
            for ip in ips:
                ipfile.write(ip)

    ret.append(window.port)

    ret.append(window.turnlength)
    ret.append(window.ironman.get())
    ret.append(window.hardcore.get())

    # Return (player, state, ip, port, turnlength, ironman, hardcore)
    return tuple(ret)

if __name__ == '__main__':
    runwelcome()
