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
        nextb = ttk.Button(frame, text='Next', command=self.mapselect)
        classcombo = ttk.Combobox(frame, textvariable=self.charclass, values=CLASSES)
        racecombo = ttk.Combobox(frame, textvariable=self.charrace, values=RACES)
        classl = ttk.Label(frame, text='Class:')
        racel = ttk.Label(frame, text='Race:')
        # Lay out the widgets
        racel.grid(column=2, row=1, stick=W, padx=5, pady=5)
        racecombo.grid(column=2, row=2, stick=(N, S), padx=5, pady=5)
        classl.grid(column=2, row=3, stick=W, padx=5, pady=5)
        classcombo.grid(column=2, row=4, stick=(N, S), padx=5, pady=5)
        backb.grid(column=1, row=5, stick=(N, S), padx=20, pady=20)
        nextb.grid(column=3, row=5, stick=(N, S), padx=20, pady=20)
        return frame

    def mainmenu(self):
        self.frame.pack_forget()
        self.frame = self._getmainmenu()
        self.frame.pack()

    def newchar(self):
        self.frame.pack_forget()
        self.frame = self._getnewchar()
        self.frame.pack()

    def loadchar(self):
        pass

    def mapselect(self):
        if self.charrace.get() == '' or self.charclass.get() == '':
            return
        print self.charrace.get(), self.charclass.get()

if __name__ == '__main__':
    root = Tk()
    root.title("Akintu")
    window = WelcomeWindow(root)
    root.mainloop()
