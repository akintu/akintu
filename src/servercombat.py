from network import *
import broadcast
from combat import *
from location import *

# TODO: Use user-defined timed-turns
seconds = 12

class CombatServer():
    def __init__(self, server):
        self.server = server
        self.combatStates = {}
        
    def handle(self, port, command):
        ###### MovePerson ######
        if isinstance(command, Person) and command.action == PersonActions.MOVE:
            activePlayer = self.server.person[command.id]
            
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
                activePlayer.cPane = None
                activePlayer.cLocation = None
                self.server.unload_panes()
                
            # If this is a legal move request
   
            elif self.tile_is_open(command.location, command.id) and \
                 activePlayer.AP >= activePlayer.totalMovementAPCost:
                activePlayer.AP -= activePlayer.totalMovementAPCost
                self.server.SDF.send(port, Update(command.id, UpdateProperties.AP, activePlayer.AP))
                # Update location and broadcast
                self.server.person[command.id].cLocation = command.location
                for p, i in self.server.player.iteritems():
                    if p != port and self.server.person[command.id].cPane == \
                            self.server.person[i].cPane:
                        self.server.SDF.send(p, command)
                self.check_turn_end(self.server.pane[self.server.person[command.id].cPane])
                            
    ### Utility ###
                
    def tile_is_open(self, location, pid):
        if location.pane not in self.server.pane:
            return False
        return self.server.pane[self.server.person[pid].cPane].is_tile_passable(location) and \
                location.tile not in [self.server.person[i].cLocation.tile \
                for i in self.server.pane[self.server.person[pid].cPane].person]
                
    def startCombat(self, playerId, monsterId):
        '''Initiates combat'''
        
        combatPane = self.server.person[monsterId].location
        self.combatStates[combatPane] = CombatState()
        if not self.server.person[monsterId].cPane:
            # Put monster into combat
            self.server.person[monsterId].ai.pause()
            self.server.person[monsterId].cPane = combatPane
            self.server.load_pane(self.server.person[monsterId].cPane, monsterId)           
            # Timer set
            self.combatStates[combatPane].turnTimer = reactor.callLater(seconds, self.check_turn_end, 
                              self.server.pane[combatPane], True)     

        # Put player into combat
        self.server.person[playerId].ai.remove("RUN")
        self.server.person[playerId].cPane = self.server.person[monsterId].location
        self.server.pane[combatPane].person.append(playerId)
        
        #TODO: Calculate starting location for reals
        self.server.person[playerId].cLocation = Location((0, 0), (0, 0))

        p = [p for p, i in self.server.player.iteritems() if i == playerId][0]
        self.server.SDF.send(p, Person(PersonActions.REMOVE, i))
        self.server.SDF.send(p, Update(i, UpdateProperties.COMBAT, \
                True))
        self.server.SDF.send(p, Person(PersonActions.CREATE, i, \
                self.server.person[playerId].cLocation, \
                self.server.person[playerId].getDetailTuple()))
        for i in self.server.pane[combatPane].person:
            if playerId != i:
                self.server.SDF.send(p, Person(PersonActions.CREATE, i, \
                        self.server.person[i].cLocation, self.server.person[i].getDetailTuple()))

        self.shout_turn_start(self.server.person[playerId], turn="Player")
        
    def check_turn_end(self, combatPane, timeExpired=False):
        ''' stuff '''
        APRemains = False
        for player in [self.server.person[x] for x in self.server.pane[combatPane].person if x in 
                                                                        self.server.player.values()]:
            if player.AP != 0:
                APRemains = True
        turnOver = False
        if not APRemains or timeExpired:
            turnOver = True
        if turnOver:
            self.combatStates[combatPane].turnTimer.cancel()
            self.end_turn(combatPane)
        # TODO: check to see if remaining AP is not enough to do anything
        # with.
        
    def end_turn(self, combatPane):
        ''' stuff '''
        for character in [self.server.person[x] for x in self.server.pane[combatPane].person]:
            self.shout_turn_start(character, turn="Monster")
        self.monster_phase(combatPane)
        for character in [self.server.person[x] for x in self.server.pane[combatPane].person]:
            self.upkeep(character)
        # New Turn here
        for character in [self.server.person[x] for x in self.server.pane[combatPane].person]:
            character.AP = character.totalAP
            for port in [p for p,i in self.server.player.iteritems() if i in 
                                                                    self.server.pane[combatPane].person]:
                    self.server.SDF.send(port, Update(character.id, UpdateProperties.AP, character.AP))
        for character in [self.server.person[x] for x in self.server.pane[combatPane].person]:
            self.shout_turn_start(character, turn="Player")
        self.combatStates[combatPane].turnTimer = reactor.callLater(seconds, self.check_turn_end, 
                                                                    combatPane, True)   
        
    def monster_phase(self, combatPane):
        print "Did monster phase stuff."
        return
        
    ### Combat Logic ###            
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
        target.statusList[:] = [x for x in target.statusList if x.turnsLeft != 0]
        # Refill AP
        
                
    def shout_turn_start(self, player, turn="Player"):
        '''Shouts to the Player that this particular turn is starting.
        Defaults to "Player"; "Monster" is the other valid value.'''
        bc = broadcast.TurnBroadcast({'turn':turn})
        bc.shout(player)
                
    def refill_resources(self, player):
        player.MP = player.totalMP
        player.HP = player.totalHP
        player.AP = player.totalAP      
          
class CombatState(object):
    def __init__(self):
        self.turnTimer = None
        
          