from network import *

class _Person():
    def __init__(self, location, index):
        self.location = location
        self.index = index

class GameServer():
    def __init__(self, world):
        self.world = world
        self.SDF = ServerDataFactory()
        reactor.listenTCP(1337, self.SDF)

        LoopingCall(self.server_loop).start(0)
        LoopingCall(self.timer_actions).start(0.5)

        self.players = {}  # {Port: _Player} of all players
        self.people = {}  # {location.Pane: List(Location)} containing lists of people's locations
        self.panes = {}  # {location.Pane: Pane} Dictionary of actual pane objects

    def server_loop(self):
        while not self.SDF.queue.empty():
            port, command = self.SDF.queue.get()

            ###### CreatePerson ######
            if isinstance(command, Person) and command.action == PersonActions.CREATE:
                #Assume clients only send this when they want to create themselves
                #Send new sprite to all clients, then give calling client everything on pane

                self.load_panes(command)
                command.index = len(self.people[command.location.pane])
                self.players[port] = _Person(command.location, command.index)
                self.people[command.location.pane].append(command.location)

                # Send command to each player in the affected pane
                for p, player in self.players.iteritems():
                    if self.players[port].location.pane == player.location.pane:
                        self.SDF.send(p, command)

                # Send list of players to the issuing client
                for i, l in enumerate(self.people[command.location.pane]):
                    self.SDF.send(port, Person(PersonActions.CREATE, i, l))

            ###### MovePerson ######
            if isinstance(command, Person) and command.action == PersonActions.MOVE:
                self.load_panes(command)
                if self.panes[command.location.pane].is_tile_passable(command.location):
                    if self.players[port].location.pane == command.location.pane:
                        #Update location and broadcast
                        self.people[command.location.pane][command.index] = command.location
                        for p, player in self.players.iteritems():
                            if command.location.pane == player.location.pane:
                                self.SDF.send(p, command)
                    else:
                        #Remove player from old pane on all relevent clients and server
                        self.people[self.players[port].location.pane].pop(command.index)
                        command.action = PersonActions.REMOVE
                        for p, player in self.players.iteritems():
                            if self.players[port].location.pane == player.location.pane:
                                self.SDF.send(p, command)

                        #Update location
                        self.players[port].location = command.location

                        #Add player to new pane lists
                        command.index = len(self.people[command.location.pane])
                        command.action = PersonActions.CREATE
                        self.people[command.location.pane].append(command.location)

                        # Send command to each player in the affected pane
                        for p, player in self.players.iteritems():
                            if self.players[port].location.pane == player.location.pane:
                                self.SDF.send(p, command)

                        # Send list of players to the issuing client
                        for i, l in enumerate(self.people[command.location.pane]):
                            self.SDF.send(port, Person(PersonActions.CREATE, i, l))

            ###### RemovePerson ######
            if isinstance(command, Person) and command.action == PersonActions.REMOVE:
                command.index = self.players[port].index
                self.people[self.players[port].location.pane].pop(command.index)
                for p, player in self.players.iteritems():
                    if self.players[port].location.pane == player.location.pane:
                        self.SDF.send(p, command)
                del self.players[port]

    def timer_actions(self):
        pass

    def load_panes(self, command):
        if command.action in [PersonActions.CREATE, PersonActions.MOVE]:
            if command.location.pane not in self.panes.keys():
                self.panes[command.location.pane], _ = self.world.get_pane(command.location.pane)
                self.people[command.location.pane] = []

    def unload_panes(self):
        current_panes = list()
        for player in self.players.values():
            x, y = player.location.pane
            for (dx, dy) in [(x, y) for x in range(-1, 2) for y in range(-1, 2)]:
                current_panes.append((x + dx, y + dy))
        for pane in self.panes:
            if pane not in current_panes:
                #Save pane state to disk and then...
                print("Unloading pane " + str(pane))
                del self.panes[pane]
                del self.people[pane]

def move_person(self, direction, distance):
    newloc = self.location.move(direction, distance)
    if self.pane.is_tile_passable(newloc):
        self.CDF.send(MovePerson(self.index, newloc))
        self.location = newloc
        if self.pane != newloc.pane:
            self.switch_panes(newloc)
            self.screen.add_person(self.index, None, self.location)
        self.screen.update_person(self.index, self.location)