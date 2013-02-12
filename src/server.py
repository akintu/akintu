from network import *
from location import *

class _Person():
    def __init__(self, location = Location((0, 0), (PANE_X/2, PANE_Y/2)), index = None):
        self.location = location
        self.index = index
        self.task = None
        self.task_frequency = 0
        self.task_running = False
        #self.timestamp = time.now

    def set_task(self, task, task_frequency, *args):
        if not self.task_running:
            self.task = LoopingCall(task, *args)
            self.task_frequency = task_frequency

    def start_task(self):
        if not self.task_running:
            self.task.start(1.0 / self.task_frequency)
            self.task_running = True

    def stop_task(self):
        if self.task and self.task_running:
            self.task.stop()
            self.task_running = False

class GameServer():
    def __init__(self, world):
        self.world = world
        self.SDF = ServerDataFactory()
        reactor.listenTCP(1337, self.SDF)

        LoopingCall(self.server_loop).start(0)

        self.players = {}  # {Port: _Player} of all players
        self.panes = {}  # {location.Pane: Pane} Dictionary of actual pane objects

    def server_loop(self):
        while not self.SDF.queue.empty():
            port, command = self.SDF.queue.get()

            ###### CreatePerson ######
            if isinstance(command, Person) and command.action == PersonActions.CREATE:
                #Assume clients only send this when they want to create themselves
                #Send new sprite to all clients, then give calling client everything on pane

                self.load_panes(command)
                command.index = len(self.panes[command.location.pane].people)
                self.players[port] = _Person(command.location, command.index)
                self.panes[command.location.pane].people.append(_Person(command.location))

                # Send command to each player in the affected pane
                for p, player in self.players.iteritems():
                    if self.players[port].location.pane == player.location.pane:
                        self.SDF.send(p, command)

                # Send list of players to the issuing client
                for i, p in enumerate(self.panes[command.location.pane].people):
                    self.SDF.send(port, Person(PersonActions.CREATE, i, p.location))

            ###### MovePerson ######
            if isinstance(command, Person) and command.action == PersonActions.MOVE:
                self.load_panes(command)
                if self.panes[command.location.pane].is_tile_passable(command.location) and \
                        command.location.tile not in [x.location.tile for x in self.panes[command.location.pane].people]:
                    if self.players[port].location.pane == command.location.pane:
                        #Update location and broadcast
                        self.panes[command.location.pane].people[command.index].location = command.location
                        self.players[port].location = command.location
                        for p, player in self.players.iteritems():
                            if command.location.pane == player.location.pane:
                                self.SDF.send(p, command)
                    else:
                        #Remove player from old pane on all relevent clients and server
                        self.panes[self.players[port].location.pane].people.pop(command.index)
                        command.action = PersonActions.REMOVE
                        for p, player in self.players.iteritems():
                            if self.players[port].location.pane == player.location.pane:
                                self.SDF.send(p, command)
                                if player.index > command.index:
                                    player.index -= 1

                        #Update location
                        self.players[port].location = command.location
                        self.players[port].index = len(self.panes[command.location.pane].people)

                        #Add player to new pane lists
                        command.index = self.players[port].index
                        command.action = PersonActions.CREATE
                        self.panes[command.location.pane].people.append(_Person(command.location))

                        # Send command to each player in the affected pane
                        for p, player in self.players.iteritems():
                            if self.players[port].location.pane == player.location.pane:
                                self.SDF.send(p, command)

                        # Send list of players to the issuing client
                        for i, p in enumerate(self.panes[command.location.pane].people):
                            self.SDF.send(port, Person(PersonActions.CREATE, i, p.location))

                        self.unload_panes()
                else:
                    self.players[port].stop_task()
                    command.location = self.players[port].location
                    self.SDF.send(port, command)

            ###### RemovePerson ######
            # The server queues up this command when a client disconnects
            if isinstance(command, Person) and command.action == PersonActions.REMOVE:
                command.index = self.players[port].index
                self.panes[self.players[port].location.pane].people.pop(command.index)
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
        self.SDF.queue.put((port, Person(PersonActions.MOVE, self.players[port].index, self.players[port].location.move(direction, 1))))

    def load_panes(self, command):
        if command.action in [PersonActions.CREATE, PersonActions.MOVE]:
            if command.location.pane not in self.panes:
                print("Loading pane " + str(command.location.pane))
                self.panes[command.location.pane] = self.world.get_pane(command.location.pane)

    def unload_panes(self):
        current_panes = []
        for player in self.players.values():
            x, y = player.location.pane
            for (dx, dy) in [(_x, _y) for _x in range(-1, 2) for _y in range(-1, 2)]:
                current_panes.append((x + dx, y + dy))
        for pane in self.panes.keys():
            if pane not in current_panes:
                #Save pane state to disk and then...
                print("Unloading pane " + str(pane))
                del self.panes[pane]
