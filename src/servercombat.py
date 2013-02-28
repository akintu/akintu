from network import *
import broadcast
from combat import *

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

                i = [i for i, p in self.server.person.iteritems() if p.location == \
                        self.server.person[command.id].cPane][0]
                self.server.person[i].ai.resume()
                self.server.person[i].cPane = None
                self.server.person[i].cLocation = None

                
                newloc = self.server.person[command.id].location.move( \
                        10 - self.server.person[command.id].location.direction, 1)
                self.server.SDF.queue.put((None, Person(PersonActions.MOVE, command.id, newloc, True)))
                self.server.person[command.id].cPane = None
                self.server.person[command.id].cLocation = None
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
                
    def upkeep(self, target):
        '''Applies all upkeep operations for this Person.  (Used during the combat
        phase: "Upkeep"'''
        if target.HPRegen > 0:
            Combat.healTarget(target, target.HPRegen)
        if target.MPRegen > 0:
            Combat.modifyResource(target, "MP", target.MPRegen)
        for stat in target.statusList:
            stat.upkeepActivate(target)
            if stat.turnsLeft > 0:
                stat.turnsLeft -= 1
        # Remove expired statuseffects
        target.statusList[:] = [x for x in target.statusList if x.turnsList != 0]
                
    def shout_turn_start(self, player, turn="Player"):
        '''Shouts to the Player that this particular turn is starting.
        Defaults to "Player"; "Monster" is the other valid value.'''
	    bc = broadcast.TurnBroadcast({'turn':turn})
	    bc.shout(player)
                
    def refill_resources(player):
        player.MP = player.totalMP
	    player.HP = player.totalHP
	    player.AP = player.totalAP      
          