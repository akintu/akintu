from network import *

class CombatServer():
    def __init__(self, server):
        self.server = server
        
    def handle(self, port, command):
        ###### MovePerson ######
        if isinstance(command, Person) and command.action == PersonActions.MOVE:
            
            # Exit combat
            if command.location.pane != (0, 0):
                self.server.SDF.send(port, Person(PersonActions.REMOVE, command.id))
                self.server.SDF.send(port, Update(command.id, UpdateProperties.COMBAT, \
                        False))
                self.server.SDF.send(port, Person(PersonActions.CREATE, command.id, \
                        self.server.person[command.id].location, \
                        self.server.person[command.id].getDetailTuple()))
                for i in self.server.pane[self.server.person[command.id].location.pane].person:
                    if i != command.id:
                        self.server.SDF.send(port, Person(PersonActions.CREATE, i, \
                                self.server.person[i].location, self.server.person[i].getDetailTuple()))
                self.server.person[command.id].cPane = None
                self.server.person[command.id].cLocation = None
                            
                newloc = self.server.person[command.id].location.move( \
                        10 - self.server.person[command.id].location.direction, 1)
                self.server.SDF.queue.put((None, Person(PersonActions.MOVE, pid, newloc)))
                self.server.unload_panes()
                
            # If this is a legal move request
            elif self.tile_is_open(command.location, command.id):

                    # Update location and broadcast
                    self.server.person[command.id].cLocation = command.location
                    for p, i in self.server.player.iteritems():
                        if p != port and self.server.person[command.id].cPane == \
                                self.server.person[i].cPane:
                            self.server.SDF.send(p, command)

                
    def tile_is_open(self, location, pid):
        if location.pane not in self.server.pane:
            return False
        return self.server.pane[self.server.person[pid].cPane].is_tile_passable(location) and \
                location.tile not in [self.server.person[i].cLocation.tile \
                for i in self.server.pane[self.server.person[pid].cPane].person]
