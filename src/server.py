from network import *
from location import *
from theorycraft import TheoryCraft
from playercharacter import *
import copy

class GameServer():
    def __init__(self, world):
        self.world = world
        self.SDF = ServerDataFactory()
        reactor.listenTCP(1337, self.SDF)

        LoopingCall(self.server_loop).start(0)

        self.player = {}  # {Port: PersonID} Dict of all players, pointing to their personid
        self.person = {} # {PersonID: Person} Dict of all persons
        self.combat = {}
        self.pane = {}  # {location.Pane: Pane} Dict of actual pane objects

    def server_loop(self):
        while not self.SDF.queue.empty():
            port, command = self.SDF.queue.get()

            ###### CreatePerson ######
            if isinstance(command, Person) and command.action == PersonActions.CREATE:
                self.load_pane(command.location.pane)

                person = None
                if port:
                    person = TheoryCraft.getNewPlayerCharacter(*command.details[1:])
                else:
                    person = TheoryCraft.getMonster()

                person.id = id(person)
                command.id = person.id
                person.ai.startup(self)

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
                            self.SDF.send(port, Person(PersonActions.CREATE, i, \
                                    self.person[i].location, details))

            ###### MovePerson ######
            if isinstance(command, Person) and command.action == PersonActions.MOVE:
                self.load_pane(command.location.pane)

                # If this is a legal move request
                if self.tile_is_open(command.location, command.id):

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
                                    self.SDF.send(p, Person(PersonActions.CREATE, i, \
                                            self.person[i].location, details))

                        self.unload_panes()
                        
                    # Check for combat range and initiate combat states
                    for p, i in self.player.iteritems():
                        for person in self.person.values():
                            if self.person[i].location.in_melee_range(person.location) and \
                                    person.team == "Monsters":

                                if i not in self.combat:
                                    if person.id not in self.combat:
                                        # Put monster into combat
                                        person.ai.pause()
                                        self.combat[person.id] = {'pane': person.location,
                                                                   'loc': person.location}

                                        self.load_pane(person.location, True)
                                        self.pane[person.location].person.append(person.id)

                                    # Put player into combat
                                    self.person[i].ai.pause()
                                    self.combat[i] = {'pane': person.location,
                                                       'loc': self.person[i].location}

                                    self.SDF.send(p, Update(i, UpdateProperties.COMBAT, \
                                            True, person.location))
                                    self.SDF.send(p, Person(PersonActions.CREATE, i, \
                                            Location((0, 0), (0, 0)), \
                                            (1, self.person[i].race, self.person[i].characterClass)))
                                    for ii in self.pane[person.location].person:
                                        details = None
                                        if isinstance(self.person[ii], PlayerCharacter):
                                            details = (1, self.person[ii].race, \
                                                    self.person[ii].characterClass)
                                        else:
                                            details = (2,)
                                        self.SDF.send(p, Person(PersonActions.CREATE, ii, \
                                                self.combat[ii]['loc'], details))
                                    self.pane[person.location].person.append(self.person[i].id)
                else:
                    if port:
                        command.location = self.person[command.id].location
                        self.SDF.send(port, command)
                    else:
                        self.person[command.id].ai.remove("RUN")
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
                self.person[command.id].ai.add("RUN", self.person[command.id].ai.run, \
                        self.person[command.id].movementSpeed, pid=command.id, direction=command.location)
                self.person[command.id].ai.start("RUN")

            ###### StopPerson ######
            if isinstance(command, Person) and command.action == PersonActions.STOP:
                self.person[command.id].ai.remove("RUN")

    def tile_is_open(self, location, pid=None):
        if location.pane not in self.pane:
            return False
        if pid and pid in self.combat:
            return self.pane[self.combat[pid]['pane']].is_tile_passable(location) and \
                location.tile not in [self.combat[i]['loc'].tile \
                for i in self.pane[self.combat[pid]['pane']].person]
        else:
            return self.pane[location.pane].is_tile_passable(location) and \
                        location.tile not in [self.person[i].location.tile \
                        for i in self.pane[location.pane].person]

    def load_pane(self, pane, combat=False):
        if pane not in self.pane:
            print("Loading pane " + str(pane))
            if combat:
                self.pane[pane] = self.pane[pane.pane].get_combat_pane(pane)
            else:
                self.pane[pane] = self.world.get_pane(pane, True)

            # Add all people in pane to global person table, then replace pane's person list with
            # a list of personIDs
            self.person.update(self.pane[pane].person)
            self.pane[pane].person = self.pane[pane].person.keys()
            for p in self.pane[pane].person:
                self.person[p].id = id(self.person[p])
                self.person[p].ai.startup(self)

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

                # Stop all AI behaviors
                for p in self.pane[pane].person:
                    self.person[p].ai.shutdown()

                del self.pane[pane]
