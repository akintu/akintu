from network import *
from location import *
from theorycraft import TheoryCraft
from playercharacter import *

class GameServer():
    def __init__(self, world):
        self.world = world
        self.SDF = ServerDataFactory()
        reactor.listenTCP(1337, self.SDF)

        LoopingCall(self.server_loop).start(0)

        self.players = {}  # {Port: Person} of all players
        self.panes = {}  # {location.Pane: Pane} Dictionary of actual pane objects

    def server_loop(self):
        while not self.SDF.queue.empty():
            port, command = self.SDF.queue.get()

            ###### CreatePerson ######
            if isinstance(command, Person) and command.action == PersonActions.CREATE:
                # Assume clients only send this when they want to create themselves
                # Send new sprite to all clients, then give calling client everything on pane

                self.load_panes(command)
                
                player = TheoryCraft.getNewPlayerCharacter(command.details[1], command.details[2])
                player.id = id(player)
                command.id = id(player)
                self.players[port] = player
                self.panes[command.location.pane].people[player.id] = player

                # Send command to each player in the affected pane
                for p, player in self.players.iteritems():
                    if self.players[port].location.pane == player.location.pane:
                        self.SDF.send(p, command)

                # Send list of players to the issuing client
                for i, person in self.panes[command.location.pane].people.iteritems():
                    if i != command.id:
                        details = None
                        if isinstance(person, PlayerCharacter):
                            details = (1, person.race, person.characterClass)
                        else:
                            details = (2,)
                        self.SDF.send(port, Person(PersonActions.CREATE, i, person.location, details))

            ###### MovePerson ######
            if isinstance(command, Person) and command.action == PersonActions.MOVE:
                self.load_panes(command)
                if self.panes[command.location.pane].is_tile_passable(command.location) and \
                        command.location.tile not in [x.location.tile for x in self.panes[command.location.pane].people.values()]:
                    
                    # If the origin and destination are in the same pane
                    if self.players[port].location.pane == command.location.pane:
                        # Update location and broadcast
                        self.panes[command.location.pane].people[command.id].location = command.location
                        self.players[port].location = command.location
                        for p, player in self.players.iteritems():
                            if p != port:
                                if command.location.pane == player.location.pane:
                                    self.SDF.send(p, command)
                    else:
                        # Remove player from old pane on all relevent clients and server
                        del self.panes[self.players[port].location.pane].people[command.id]
                        command.action = PersonActions.REMOVE
                        for p, player in self.players.iteritems():
                            if self.players[port].location.pane == player.location.pane:
                                self.SDF.send(p, command)

                        # Update location
                        self.players[port].location = command.location

                        # Add player to new pane lists
                        command.action = PersonActions.CREATE
                        command.details = (1, self.players[port].race, self.players[port].characterClass)
                        self.panes[command.location.pane].people[self.players[port].id] = self.players[port]

                        # Send command to each player in the affected pane
                        for p, player in self.players.iteritems():
                            if self.players[port].location.pane == player.location.pane:
                                self.SDF.send(p, command)

                        # Send list of players to the issuing client
                        for i, person in self.panes[command.location.pane].people.iteritems():
                            details = None
                            if isinstance(person, PlayerCharacter):
                                details = (1, person.race, person.characterClass)
                            else:
                                details = (2,)
                            self.SDF.send(port, Person(PersonActions.CREATE, i, person.location, details))

                        self.unload_panes()
                else:
                    self.players[port].stop_task()
                    command.location = self.players[port].location
                    self.SDF.send(port, command)

            ###### RemovePerson ######
            # The server queues up this command when a client disconnects
            if isinstance(command, Person) and command.action == PersonActions.REMOVE:
                command.id = self.players[port].id
                del self.panes[self.players[port].location.pane].people[self.players[port].id]
                for p, player in self.players.iteritems():
                    if self.players[port].location.pane == player.location.pane:
                        self.SDF.send(p, command)
                del self.players[port]
                self.unload_panes()

            ###### RunPerson ######
            if isinstance(command, Person) and command.action == PersonActions.RUN:
                self.players[port].set_task(self.run_person, 5, port, command.location)
                self.players[port].start_task()

            ###### StopPerson ######
            if isinstance(command, Person) and command.action == PersonActions.STOP:
                self.players[port].stop_task()

    def run_person(self, port, direction):
        self.SDF.queue.put((port, Person(PersonActions.MOVE, self.players[port].id, self.players[port].location.move(direction, 1))))

    def load_panes(self, command):
        if command.action in [PersonActions.CREATE, PersonActions.MOVE]:
            if command.location.pane not in self.panes:
                print("Loading pane " + str(command.location.pane))
                self.panes[command.location.pane] = self.world.get_pane(command.location.pane)
                self.panes[command.location.pane].generate_creatures()

    def unload_panes(self):
        current_panes = []
        for player in self.players.values():
            x, y = player.location.pane
            for (dx, dy) in [(_x, _y) for _x in range(-1, 2) for _y in range(-1, 2)]:
                current_panes.append((x + dx, y + dy))
        for pane in self.panes.keys():
            if pane not in current_panes:
                # Save pane state to disk and then...
                print("Unloading pane " + str(pane))
                del self.panes[pane]
