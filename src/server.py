from network import *
from location import *
from theorycraft import TheoryCraft
from playercharacter import *
from ai import AI

class GameServer():
    def __init__(self, world):
        self.world = world
        self.ai = AI(self)
        self.world.set_ai(self.ai)
        self.SDF = ServerDataFactory()
        reactor.listenTCP(1337, self.SDF)

        LoopingCall(self.server_loop).start(0)

        self.player = {}  # {Port: PersonID} Dict of all players, pointing to their personid
        self.person = {} # {PersonID: Person} Dict of all persons
        self.pane = {}  # {location.Pane: Pane} Dict of actual pane objects

    def server_loop(self):
        while not self.SDF.queue.empty():
            port, command = self.SDF.queue.get()

            ###### CreatePerson ######
            if isinstance(command, Person) and command.action == PersonActions.CREATE:
                self.load_panes(command)
                
                person = None
                if port:
                    person = TheoryCraft.getNewPlayerCharacter(command.details[1], command.details[2])
                    # Does this work?
                    #person = TheoryCraft.getNewPlayerCharacter(*command.details)
                else:
                    person = TheoryCraft.getMonster()
                    
                person.id = id(person)
                command.id = person.id
                
                if port:
                    self.player[port] = person.id
                self.person[person.id] = person
                self.pane[command.location.pane].person.append(person.id)
                
                # Send command to each player in the affected pane
                for p, i in self.player.iteritems():
                    if command.location.pane == self.person[i].location.pane:
                        self.SDF.send(p, command)

                # Send list of players to the issuing client
                if port:
                    for i in self.pane[command.location.pane].person:
                        if i != command.id:
                            details = None
                            if isinstance(self.person[i], PlayerCharacter):
                                details = (1, self.person[i].race, self.person[i].characterClass)
                            else:
                                details = (2,)
                            self.SDF.send(port, Person(PersonActions.CREATE, i, self.person[i].location, details))

            ###### MovePerson ######
            if isinstance(command, Person) and command.action == PersonActions.MOVE:
                self.load_panes(command)
                
                # If this is a legal move request
                if self.tile_is_open(command.location):

                    # If the origin and destination are in the same pane
                    if self.person[command.id].location.pane == command.location.pane:
                    
                        # Update location and broadcast
                        self.person[command.id].location = command.location
                        for p, i in self.player.iteritems():
                            if p != port:
                                if command.location.pane == self.person[i].location.pane:
                                    self.SDF.send(p, command)
                    else:
                        # Remove person from players' person tables, and pane's person list
                        self.pane[self.person[command.id].location.pane].person.remove(command.id)
                        for p, i in self.player.iteritems():
                            if self.person[i].location.pane == self.person[command.id].location.pane:
                                self.SDF.send(p, Person(PersonActions.REMOVE, command.id))
                    
                        # Update location in server memory
                        self.person[command.id].location = command.location
                    
                        # Add player to new pane lists and send to clients in the affected pane
                        self.pane[command.location.pane].person.append(command.id)
                        command.action = PersonActions.CREATE
                        if isinstance(self.person[command.id], PlayerCharacter):
                            command.details = (1, self.person[command.id].race, \
                                self.person[command.id].characterClass)
                        else:
                            command.details = (2,)
                        for p, i in self.player.iteritems():
                            if self.person[i].location.pane == command.location.pane:
                                self.SDF.send(p, command)

                        # Send list of players to the issuing client
                        if command.id in [i for i in self.player.values()]:
                            p = [p for p, i in self.player.iteritems() if i == command.id][0]
                            for i in self.pane[command.location.pane].person:
                                if i != command.id:
                                    details = None
                                    if isinstance(self.person[i], PlayerCharacter):
                                        details = (1, self.person[i].race, self.person[i].characterClass)
                                    else:
                                        details = (2,)
                                    self.SDF.send(p, Person(PersonActions.CREATE, i, self.person[i].location, details))

                        self.unload_panes()
                else:
                    if port:
                        command.location = self.person[command.id].location
                        self.SDF.send(port, command)
                    else:
                        self.person[command.id].remove_ai(self.ai.run)
                        for p, i in self.player.iteritems():
                            if i == command.id:
                                self.SDF.send(p, Person(PersonActions.STOP, i))

            ###### RemovePerson ######
            if isinstance(command, Person) and command.action == PersonActions.REMOVE:
                if port:
                    command.id = self.player[port]
                    del self.player[port]
                self.pane[self.person[command.id].location.pane].person.remove(command.id)
                
                #Notify clients in the affected pane
                for p, i in self.player.iteritems():
                    if self.person[i].location.pane == self.person[command.id].location.pane:
                        self.SDF.send(p, command)
                del self.person[command.id]
                self.unload_panes()

            ###### RunPerson ######
            if isinstance(command, Person) and command.action == PersonActions.RUN:
                self.person[command.id].add_ai(self.ai.run, 5, pid=command.id, direction=command.location)

            ###### StopPerson ######
            if isinstance(command, Person) and command.action == PersonActions.STOP:
                self.person[command.id].remove_ai(self.ai.run)
             
    def tile_is_open(self, location):
        return self.pane[location.pane].is_tile_passable(location) and \
                        location.tile not in [self.person[i].location.tile \
                        for i in self.pane[location.pane].person]
             
    def load_panes(self, command):
        if command.action in [PersonActions.CREATE, PersonActions.MOVE]:
            if command.location.pane not in self.pane:
                print("Loading pane " + str(command.location.pane))
                self.pane[command.location.pane] = self.world.get_pane(command.location.pane, True)
                
                # Add all people in pane to global person table, then replace pane's person list with
                # a list of personIDs
                self.person.update(self.pane[command.location.pane].person)
                self.pane[command.location.pane].person = self.pane[command.location.pane].person.keys()

    def unload_panes(self):
        current_panes = []
        for i in self.player.values():
            x, y = self.person[i].location.pane
            for (dx, dy) in [(_x, _y) for _x in range(-1, 2) for _y in range(-1, 2)]:
                current_panes.append((x + dx, y + dy))
        for pane in self.pane.keys():
            if pane not in current_panes:
                # Save pane state to disk and then...
                print("Unloading pane " + str(pane))
                del self.pane[pane]
