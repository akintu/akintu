from network import *
import broadcast
from combat import *
from location import *
from dice import *
import region
import monster

# TODO: Use user-defined timed-turns
seconds = 45

class CombatServer():
    def __init__(self, server):
        self.server = server
        self.combatStates = {}

    def handle(self, port, command):
        ###### MovePerson ######
        if command.type == "PERSON" and command.action == "MOVE":
            activePlayer = self.server.person[command.id]

            # Exit combat
            if command.location.pane != (0, 0):
                self.server.SDF.send(port, Command("PERSON", "REMOVE", id=command.id))
                self.server.SDF.send(port, Command("UPDATE", "COMBAT", combat=False))
                self.server.SDF.send(port, Command("PERSON", "CREATE", id=command.id, \
                        location=self.server.person[command.id].location, \
                        details=self.server.person[command.id].getDetailTuple()))
                for i in self.server.pane[self.server.person[command.id].location.pane].person:
                    if i != command.id:
                        self.server.SDF.send(port, Command("PERSON", "CREATE", id=i, \
                                location=self.server.person[i].location, \
                                details=self.server.person[i].getDetailTuple()))

                i = [i for i, p in self.server.person.iteritems() if p.location == \
                        self.server.person[command.id].cPane][0]
                self.server.person[i].ai.resume()
                self.server.person[i].cPane = None
                self.server.person[i].cLocation = None

                newloc = self.server.person[command.id].location.move( \
                        10 - self.server.person[command.id].location.direction, 1)
                self.server.SDF.queue.put((None, Command("PERSON", "MOVE", id=command.id, \
                        location=newloc, details=True)))
                activePlayer.cPane = None
                activePlayer.cLocation = None
                self.server.unload_panes()

            # If this is a legal move request
            elif self.tile_is_open(command.location, command.id) and \
                 activePlayer.AP >= activePlayer.totalMovementAPCost or\
                 activePlayer.remainingMovementTiles > 0:
                if activePlayer.remainingMovementTiles == 0:
                    Combat.modifyResource(activePlayer, "AP", -activePlayer.totalMovementAPCost)
                    Combat.resetMovementTiles(activePlayer)
                else:
                    Combat.decrementMovementTiles(activePlayer)

                # Update location and broadcast
                self.server.person[command.id].cLocation = command.location
                for p, i in self.server.player.iteritems():
                    if p != port and self.server.person[command.id].cPane == \
                            self.server.person[i].cPane:
                        self.server.SDF.send(p, command)
                self.check_turn_end(self.server.person[command.id].cPane)
        
        ###### RemovePerson ######
        elif command.type == "PERSON" and command.action == "REMOVE":
            if command.id in self.server.person:
                if port:
                    command.id = self.server.player[port]
                    del self.server.player[port]
                self.server.pane[self.server.person[command.id].cPane].person.remove(command.id)

                #Notify clients in the affected pane
                for p, i in self.server.player.iteritems():
                    if self.server.person[i].cPane == self.server.person[command.id].cPane:
                        self.server.SDF.send(p, command)
                del self.server.person[command.id]
                self.server.unload_panes()
        
        #### Attack Target ####
        elif command.type == "ABILITY" and command.action == "ATTACK":
            source = self.server.person[command.id]
            target = self.server.person[command.targetId]
            abilToUse = None
            for abil in source.abilities:
                if abil.name == command.abilityName:
                    abilToUse = abil
            for spl in source.spellList:
                if spl.name == command.abilityName:
                    abilToUse = spl
            if not abilToUse:
                abilToUse = source.selectBasicAttack()
            useDuple = abilToUse.canUse(target)
            if useDuple[0]:
                color = 'orange'
                if abilToUse.targetType == 'friendly' or abilToUse.targetType == 'self':
                    color = 'green'
                if abilToUse.targetType != 'self':
                    Combat.sendCombatMessage(source.name + " is using " + abilToUse.name + " on " + target.name,
                                             source, color=color)
                else:
                    Combat.sendCombatMessage(source.name + " is using " + abilToUse.name,
                                             source, color=color)
                abilToUse.use(target)
            else:
                Combat.sendCombatMessage(useDuple[1], source)
            self.check_turn_end(self.server.person[command.id].cPane)
        elif command.type == "ABILITY" and command.action == "END_TURN":
            target = self.server.person[command.id]
            Combat.modifyResource(target, "AP", -target.AP)
            Combat.decrementMovementTiles(target, removeAll=True)
            self.check_turn_end(self.server.person[command.id].cPane)
        if command.id in self.server.person:
            self.update_dead_people(self.server.person[command.id].cPane)

    ### Utility Methods ###

    def tile_is_open(self, location, pid):
        if location.pane not in self.server.pane:
            return False
        return self.server.pane[self.server.person[pid].cPane].is_tile_passable(location) and \
                location.tile not in [self.server.person[i].cLocation.tile \
                for i in self.server.pane[self.server.person[pid].cPane].person]

    def shout_turn_start(self, player, turn="Player"):
        '''Shouts to the Player that this particular turn is starting.
        Defaults to "Player"; "Monster" is the other valid value.'''
        bc = broadcast.TurnBroadcast({'turn':turn})
        bc.shout(player)

    def update_dead_people(self, combatPane):
        '''Checks the list of Persons on this combat Pane to see if they have HP > 0.
        If they do not, it will "remove them" from the combatPane and add them to a
        deadList associated with this CombatState.  If all monsters are dead and at least
        one player remains, enters the victory phase.'''
        toUpdateList = []
        for char in [self.server.person[x] for x in self.server.pane[combatPane].person]:
            if char.HP <= 0 and char.team == "Monsters":
                toUpdateList.append(char)
                
        for char in toUpdateList:
            self.combatStates[combatPane].deadMonsterList.append(char)
            Combat.sendCombatMessage(message=char.name + " Died!", color='magenta', character=char)
            self.server.SDF.queue.put((None, Command("PERSON", "REMOVE", id=char.id)))
            
        monstersAlive = False
        livingPlayers = []
        for char in [self.server.person[x] for x in self.server.pane[combatPane].person]:
            if char.team == "Monsters":
                monstersAlive = True
            if char.team == "Players":
                livingPlayers.append(char)
                
        if not monstersAlive and livingPlayers:
            self.victory_phase(livingPlayers, combatPane)    

    def monsterMove(self, monster, visiblePlayers):
        tilesLeft = monster.totalMovementTiles
        while tilesLeft > 0:
            player = monster.getNearestPlayer(visiblePlayers)
            if not player:
                return "Failed"
            direction = monster.cLocation.direction_to(player.cLocation)
            # Monsters cannot move in diagonal directions.
            if direction == 7:
                direction = Dice.choose([4,8])
            elif direction == 1:
                direction = Dice.choose([2,4])
            elif direction == 9:
                direction = Dice.choose([6,8])
            elif direction == 3:
                direction = Dice.choose([2,6])
            desiredLocation = monster.cLocation.move(direction, 1)
            if self.tile_is_open(desiredLocation, monster.id):
                action = Command("PERSON", "MOVE", id=monster.id, location=desiredLocation)
                #self.server.SDF.queue.put((None, action))
                for port in self.server.player.keys():
                    self.server.SDF.send(port, action)
                monster.cLocation = desiredLocation

                tilesLeft -= 1
            elif tilesLeft == monster.totalMovementTiles:
                # Monster couldn't move at all.
                return "Failed"
            else:
                break
        monster.AP -= monster.totalMovementAPCost
        return "Moved"

    ### Combat Phase Logic Methods ###

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
        for cooldown in target.cooldownList:
            cooldown[1] -= 1
        # Remove expired statuseffects and cooldowns
        toRemove = []
        for stat in target.statusList:
            if stat.turnsLeft == 0:
                toRemove.append(stat)
        for removalStatus in toRemove:
            Combat.removeStatus(target, removalStatus.name)
        target.cooldownList[:] = [x for x in target.cooldownList if x[1] > 0]
        if target.team == "Players":
            Combat.decrementMovementTiles(target, removeAll=True)
        # Refill AP (performed in end_turn)
        for stat in target.statusList:
            if stat.turnsLeft == -1:
                print target.name + " has status enabled: " + stat.name
            else:
                print target.name + " has status: " + stat.name + " T=" + str(stat.turnsLeft)
     
    def startCombat(self, playerId, monsterId):
        '''Initiates combat for the first player to enter combat.
        monsterId is the identifier for the Monster on the overworld
        that triggered combat.'''
        combatPane = self.server.person[monsterId].location
        self.combatStates[combatPane] = CombatState()
        monsterLeader = self.server.person[monsterId]
        currentPlayer = self.server.person[playerId]
        
        if not monsterLeader.cPane:
            # Put monster into combat
            monsterLeader.ai.pause()
            monsterLeader.cPane = combatPane
            self.server.load_pane(combatPane, monsterId)
            # Timer set
            self.combatStates[combatPane].turnTimer = reactor.callLater(seconds, self.check_turn_end,
                    combatPane, True)

        # Put player into combat -- Stop running if needed.
        currentPlayer.ai.remove("RUN")
        currentPlayer.cPane = combatPane
        self.server.pane[combatPane].person.append(playerId)

        #TODO: Calculate starting location for reals
        spawn = monsterLeader.location.direction_to(currentPlayer.location)
        spawn = Location(((spawn - 1) % 3) * (PANE_X - 1) / 2, ((9 - spawn) // 3) * (PANE_Y - 1) / 2)
        currentPlayer.cLocation = spawn

        port = [p for p, i in self.server.player.iteritems() if i == playerId][0]
        self.server.SDF.send(port, Command("PERSON", "REMOVE", id=playerId))
        self.server.SDF.send(port, Command("UPDATE", "COMBAT", combat=True))
        
        for p in self.server.getAllCombatPorts(playerId):
            self.server.SDF.send(p, Command("PERSON", "CREATE", id=playerId,
                    location=currentPlayer.cLocation, cPane=currentPlayer.cPane,
                    details=currentPlayer.getDetailTuple()))
                                 
        # Populate the combat pane with all of the monsters.
        for id in self.server.pane[combatPane].person:
            if playerId != id:
                self.server.SDF.send(port, Command("PERSON", "CREATE", id=id,
                        location=self.server.person[id].cLocation, 
                        details=self.server.person[id].getDetailTuple()))
            
        self.shout_turn_start(self.server.person[playerId], turn="Player")

    def check_turn_end(self, combatPane, timeExpired=False):
        ''' stuff '''
        APRemains = False
        for player in [self.server.person[x] for x in self.server.pane[combatPane].person if x in
                self.server.player.values()]:
            if player.AP != 0 or player.remainingMovementTiles != 0:
                APRemains = True
                break
        if not APRemains:
            if not self.combatStates[combatPane].turnTimer:
                print "No timer found!"
            else:
                self.combatStates[combatPane].turnTimer.cancel()
        if timeExpired or not APRemains:
            self.end_turn(combatPane)
        # TODO: check to see if remaining AP is not enough to do anything
        # with.

    def end_turn(self, combatPane):
        ''' stuff '''
        self.update_dead_people(combatPane)
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
                self.server.SDF.send(port, Command("PERSON", "UPDATE", id=character.id, AP=character.AP))
        for character in [self.server.person[x] for x in self.server.pane[combatPane].person]:
            self.shout_turn_start(character, turn="Player")
        self.combatStates[combatPane].turnTimer = reactor.callLater(seconds, self.check_turn_end,
                combatPane, True)

    def monster_phase(self, combatPane):
        chars = [self.server.person[x] for x in self.server.pane[combatPane].person]
        players = [x for x in chars if x.team == "Players"]
        monsters = [x for x in chars if x.team == "Monsters" and x not in
                    self.combatStates[combatPane].deadMonsterList]
        for mon in monsters:
            visiblePlayers = []
            for player in players:
                if not player.inStealth() or player.hasStatus("Conceal"):
                    visiblePlayers.append(player)
                elif mon.detectStealth(player):
                    visiblePlayers.append(player)
                    Combat.sendCombatMessage("Detected " + player.name + "! (" + 
                                str(player.totalSneak) + " vs " + str(mon.totalAwareness) + ")",
                                player, color='red')
            while( True ):
                if not mon.getUsableAbilities(self.server, combatPane, visiblePlayers) and \
                       mon.AP >= mon.totalMovementAPCost:
                    moveResult = self.monsterMove(mon, visiblePlayers)
                    if moveResult == "Failed":
                        break
                    else:
                        continue
                message = mon.performAction(self.server, combatPane)
                if message == "Failure":
                    break
        allCharIds = [charId for charId in self.server.pane[combatPane].person]
        for charId in allCharIds:
            char = self.server.person[charId]
        return

    def victory_phase(self, livingPlayers, combatPane):
        '''Cleans up arena, gives experience/gold to players, 
        restores their health to full, and kicks them out of combat.'''
        state = self.combatStates[combatPane]
        try:
            state.turnTimer.cancel()
        except:
            pass
        for player in livingPlayers:
            self.giveVictoryExperience(player, state.deadMonsterList)
            self.giveGold(player, state.deadMonsterList)
            self.removeTemporaryStatuses(player)
            self.refillResources(player)
        # Cleanup, exit combat TODO
        

    #### Victory Methods ####

    def giveVictoryExperience(self, player, monsterList):
        '''Grants the appropriate amount of EXP to a player at the end of
        a victorious combat.'''
        exp = Combat.calcExperienceGain(player, monsterList)
        Combat.sendCombatMessage("Gained " + str(exp) + " Experience. (" + str(player.experience) +
                                 "/" + str(player.getExpForNextLevel()) + ")", 
                                 player, color='magenta', toAll=False)
        oldLevel = player.level
        newLevel = player.addExperience(exp)
        if oldLevel != newLevel:
            Combat.sendCombatMessage(player.name + " LEVELUP!", player, color='magenta')
        
    def giveGold(self, player, monsterList):
        gold = 0
        for monster in monsterList:
            gold += monster.level * 3 + monster.GP * 2
        player.inventory.addItem(gold)
        Combat.sendCombatMessage("Gained " + str(gold) + " gold. (total: " + str(player.inventory.gold) +
                                 ")", player, color='magenta', toAll=False)
        
    def refillResources(self, player):
        Combat.modifyResource(player, "MP", player.totalMP)
        Combat.modifyResource(player, "HP", player.totalHP)
        Combat.modifyResource(player, "AP", player.totalAP)

    def removeTemporaryStatuses(self, player):
        '''Used to remove statuses that don't persist outside of combat'''
        removalList = [x for x in player.statusList if x.turnsLeft > -1]
        for removalStatus in removalList:
            Combat.removeStatus(player, removalStatus.name)


    #### Death Methods ####

    def softcoreDeath(self, player):
        goldLoss -= int(round(player.inventory.gold * 0.1))
        if goldLoss > player.inventory.gold:
            goldLoss = player.inventory.gold
        # Display message of gold loss better: TODO
        Combat.screen.show_text("You lose: " + str(goldLoss) + " gold for dying.",
                                color='yellow', size=16)
        player.inventory.gold -= goldLoss
        # Transport player to town TODO

class CombatState(object):
    def __init__(self):
        self.turnTimer = None
        self.deadMonsterList = []
