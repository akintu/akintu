from network import *
from location import *
from theorycraft import TheoryCraft
from playercharacter import *
from servercombat import *

class GameServer():
    def __init__(self, world, port):
        self.world = world
        self.SDF = ServerDataFactory()
        self.CS = CombatServer(self)
        reactor.listenTCP(port, self.SDF)

        LoopingCall(self.server_loop).start(0)

        self.player = {}  # {Port: PersonID} Dict of all players, pointing to their personid
        self.person = {} # {PersonID: Person} Dict of all persons
        self.pane = {}  # {location.Pane: Pane} Dict of actual pane objects

    def server_loop(self):
        while not self.SDF.queue.empty():
            port, command = self.SDF.queue.get()

            if command.id and self.person[command.id] and self.person[command.id].cPane:
                self.CS.handle(port, command)
                continue

            ###### CreatePerson ######
            if isinstance(command, Person) and command.action == PersonActions.CREATE:
                self.load_pane(command.location.pane)

                person = TheoryCraft.convertFromDetails(command.details)
                person.id = id(person)
                command.id = person.id
                person.ai.startup(self)

                if port:
                    self.player[port] = person.id
                self.person[person.id] = person
                self.pane[command.location.pane].person.append(person.id)

                # Send command to each player in the affected pane
                for p, i in self.player.iteritems():
                    if command.location.pane == self.person[i].location.pane and not self.person[i].cPane:
                        self.SDF.send(p, command)

                # Send list of players to the issuing client
                if port:
                    for i in self.pane[command.location.pane].person:
                        if i != command.id:
                            self.SDF.send(port, Person(PersonActions.CREATE, i, \
                                    self.person[i].location, self.person[i].getDetailTuple()))

            ###### MovePerson ######
            if isinstance(command, Person) and command.action == PersonActions.MOVE:
                self.load_pane(command.location.pane)

                # If this is a legal move request
                if self.tile_is_open(command.location):

                    # If the origin and destination are in the same pane
                    if self.person[command.id].location.pane == command.location.pane:

                        # Update location and broadcast
                        self.person[command.id].location = command.location
                        for p, i in self.player.iteritems():
                            if p != port and command.location.pane == self.person[i].location.pane and \
                                    not self.person[i].cPane:
                                self.SDF.send(p, command)

                    else:
                        # Remove person from players' person tables, and pane's person list
                        self.pane[self.person[command.id].location.pane].person.remove(command.id)
                        for p, i in self.player.iteritems():
                            if self.person[i].location.pane == self.person[command.id].location.pane \
                                    and not self.person[i].cPane:
                                self.SDF.send(p, Person(PersonActions.REMOVE, command.id))

                        # Update location in server memory
                        self.person[command.id].location = command.location

                        # Add player to new pane lists and send to clients in the affected pane
                        self.pane[command.location.pane].person.append(command.id)
                        command.action = PersonActions.CREATE
                        command.details = self.person[command.id].getDetailTuple()
                        for p, i in self.player.iteritems():
                            if self.person[i].location.pane == command.location.pane and \
                                    not self.person[i].cPane:
                                self.SDF.send(p, command)

                        # Send list of players to the issuing client
                        if command.id in self.player.values():
                            p = [p for p, i in self.player.iteritems() if i == command.id][0]
                            for i in self.pane[command.location.pane].person:
                                if i != command.id:
                                    self.SDF.send(p, Person(PersonActions.CREATE, i, \
                                            self.person[i].location, self.person[i].getDetailTuple()))

                        self.unload_panes()

                    # Check for combat range and initiate combat states
                    if command.id in self.player.values():
                        p = [p for p, i in self.player.iteritems() if i == command.id][0]
                        for person in self.pane[self.person[command.id].location.pane].person:
                            if self.person[command.id].location.in_melee_range( \
                                    self.person[person].location) and \
                                    self.person[person].team == "Monsters":
                                self.CS.startCombat(command.id, person)


                else:
                    if port:
                        command.location = self.person[command.id].location
                        command.details = True
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
                    if self.person[i].location.pane == self.person[command.id].location.pane and \
                            i not in self.combat:
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

    def tile_is_open(self, location):
        if location.pane not in self.pane:
            return False
        return self.pane[location.pane].is_tile_passable(location) and \
                location.tile not in [self.person[i].location.tile \
                for i in self.pane[location.pane].person]

    def load_pane(self, pane, pid=None):
        if pane not in self.pane:
            print("Loading pane " + str(pane))
            if pid:
                self.pane[pane] = self.pane[pane.pane].get_combat_pane(pane, self.person[pid])
                for i, p in self.pane[pane].person.iteritems():
                    p.cLocation = p.location
                    p.location = None
                    p.cPane = pane
                #print self.pane[pane.pane].person
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
                for i in self.pane[pane].person:
                    self.person[i].ai.shutdown()
                    del self.person[i]

                del self.pane[pane]
