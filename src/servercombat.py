from network import *
import broadcast
from combat import *
from location import *
from dice import *
import math
import region
import monster


class CombatServer():
    SECONDS = 45
    
    def __init__(self, server):
        self.server = server
        self.combatStates = {}

    def handle(self, port, command):
        ###### MovePerson ######
        if command.type == "PERSON" and command.action == "MOVE":
            activePlayer = self.server.person[command.id]

            # If this is a legal move request
            if self.server.tile_is_open(command.location, command.id) and \
                 activePlayer.AP >= activePlayer.totalMovementAPCost or\
                 activePlayer.remainingMovementTiles > 0:
                if activePlayer.remainingMovementTiles == 0:
                    Combat.modifyResource(activePlayer, "AP", -activePlayer.totalMovementAPCost)
                    Combat.resetMovementTiles(activePlayer)
                else:
                    Combat.decrementMovementTiles(activePlayer)

                # Update location and broadcast
                activePlayer.cLocation = command.location
                self.server.broadcast(command, -command.id, exclude=True)
                self.check_turn_end(activePlayer.cPane)
        
        ###### RemovePerson ######
        elif command.type == "PERSON" and command.action == "REMOVE":
            if command.id in self.server.person:
                if port:
                    command.id = self.server.player[port]
                    del self.server.player[port]
                    self.server.pane[self.server.person[command.id].location.pane].person.remove(command.id)
                self.server.pane[self.server.person[command.id].cPane].person.remove(command.id)

                #Notify clients in the affected pane
                self.server.broadcast(command, -command.id)
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
        
        #### Using Items ####
        elif command.type == "ITEM" and command.action == "USE":
            user = self.server.person[command.id]
            item = None
            for x in user.inventory.allConsumables:
                if x.name == command.itemName:
                    item = x
                    break
            if not item:
                print " Item not found: " + itemName
                return
            usable = item.canUse(user)
            if usable[0]:
                itemMessage = item.use(user)
                Combat.sendCombatMessage(itemMessage, user, color='purple', toAll=False)
                self.server.broadcast(Command("ITEM", "REMOVE", id=command.id, 
                        itemName=command.itemName), port=port)
            else:
                itemMessage = usable[1]
                Combat.sendCombatMessage(itemMessage, user, color='white', toAll=False)
            
            
        if command.id in self.server.person:
            self.update_dead_people(self.server.person[command.id].cPane)
        
    
    ### Utility Methods ###
                
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
        print "HELLO, My name is update dead people! I was just called."
        
        if not combatPane:
            return
            
        toUpdateList = []
        for char in [self.server.person[x] for x in self.server.pane[combatPane].person]:
            if char.HP <= 0:
                if char.team == "Monsters":
                    toUpdateList.append(char)
                elif char.team == "Players" and not char.hardcore:
                    Combat.sendCombatMessage(char.name + " has Fallen!", color='darkred', character=char)
                    self.softcoreDeath(char)
                elif char.team == "Players" and char.hardcore:
                    Combat.sendCombatMessage(char.name + " has Perished!", color='darkred', character=char)
                    # TODO: Delete saves, end game?
            
        
                
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
                
        if not livingPlayers:
            self.monster_victory(combatPane)
            return "END_COMBAT"
                
        rValue = "CONTINUE_COMBAT"
        if not monstersAlive and livingPlayers:
            rValue = "END_COMBAT"
            self.victory_phase(livingPlayers, combatPane)
        return rValue

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
            if self.server.tile_is_open(desiredLocation, monster.id):
                action = Command("PERSON", "MOVE", id=monster.id, location=desiredLocation)
                self.server.broadcast(action, -monster.id)
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
                print target.name + " has status: " + stat.name + " T=" + `int(stat.turnsLeft)`
     
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
            #monsterLeader.cPane = combatPane
            self.server.load_pane(combatPane, monsterId)
            # Timer set
            if CombatServer.SECONDS > 0:
                self.combatStates[combatPane].turnTimer = reactor.callLater(CombatServer.SECONDS, \
                        self.check_turn_end, combatPane, True)

        # Put player into combat -- Stop running if needed.
        currentPlayer.ai.remove("RUN")
        currentPlayer.cPane = combatPane
        self.server.pane[combatPane].person.append(playerId)

        spawn = monsterLeader.location.direction_to(currentPlayer.location)
        spawn = Location(((spawn - 1) % 3) * (PANE_X - 1) / 2, ((9 - spawn) // 3) * (PANE_Y - 1) / 2)
        currentPlayer.cLocation = spawn

        self.server.broadcast(Command("PERSON", "REMOVE", id=playerId), playerId)
        self.server.broadcast(Command("UPDATE", "COMBAT", combat=True), playerId)
        
        self.server.broadcast(Command("PERSON", "CREATE", id=playerId,
                    location=currentPlayer.cLocation, cPane=currentPlayer.cPane,
                    details=currentPlayer.dehydrate()), -playerId)
                                 
        # Populate the combat pane with all of the monsters.
        for id in self.server.pane[combatPane].person:
            if playerId != id:
                self.server.broadcast(Command("PERSON", "CREATE", id=id,
                        location=self.server.person[id].cLocation, 
                        details=self.server.person[id].dehydrate()), playerId)
            
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
                if CombatServer.SECONDS > 0:
                    print "No timer found!"
            elif self.combatStates[combatPane].turnTimer.active():
                self.combatStates[combatPane].turnTimer.cancel()
        if timeExpired or not APRemains:
            self.end_turn(combatPane)
        # TODO: check to see if remaining AP is not enough to do anything
        # with.

    def end_turn(self, combatPane):
        ''' stuff '''
        if self.update_dead_people(combatPane) == "CONTINUE_COMBAT":
            for character in [self.server.person[x] for x in self.server.pane[combatPane].person]:
                self.shout_turn_start(character, turn="Monster")
            self.monster_phase(combatPane)
            for character in [self.server.person[x] for x in self.server.pane[combatPane].person]:
                self.upkeep(character)
            # New Turn here
            for character in [self.server.person[x] for x in self.server.pane[combatPane].person]:
                #if not character.hasStatus("Stun"): TODO, uncomment after Beta
                character.AP = character.totalAP
                self.server.broadcast(Command("PERSON", "UPDATE", id=character.id, AP=character.AP),
                        pane=combatPane)
            for character in [self.server.person[x] for x in self.server.pane[combatPane].person]:
                self.shout_turn_start(character, turn="Player")
            if CombatServer.SECONDS > 0:
                if self.combatStates[combatPane].turnTimer.active():
                    self.combatStates[combatPane].turnTimer.cancel()
                self.combatStates[combatPane].turnTimer = reactor.callLater(CombatServer.SECONDS, self.check_turn_end,
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
                                 str(mon.totalAwareness) + " vs " + str(player.totalSneak) + ")",
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
        if CombatServer.SECONDS > 0 and state.turnTimer and state.turnTimer.active():
            state.turnTimer.cancel()
        char = livingPlayers[0]

        monsterLeader = self.server.get_monster_leader(char)
        self.server.SDF.queue.put((None, Command("PERSON", "REMOVE", id=monsterLeader.id)))
        
        for player in livingPlayers:
            self.giveVictoryExperience(player, state.deadMonsterList)
            self.giveGold(player, state.deadMonsterList)
            self.removeTemporaryStatuses(player)
            self.refillResources(player)
            self.exit_combat(player)
        # Cleanup, exit combat TODO
        
    

    #### End of Combat Phase Methods ####

    def giveVictoryExperience(self, player, monsterList):
        '''Grants the appropriate amount of EXP to a player at the end of
        a victorious combat.'''
        exp = Combat.calcExperienceGain(player, monsterList)
        #oldLevel = player.level
        player.addExperience(exp)
        #if oldLevel != newLevel:
        #    Combat.sendCombatMessage(player.name + " LEVELUP!", player, color='magenta')
        if player.experience >= player.getExpForNextLevel() and player.level < 5: # Remove hardcoded value TODO
                Combat.sendCombatMessage(player.name + " LEVELUP!", player, color='magenta')
        Combat.sendCombatMessage("Gained " + str(exp) + " Experience. (" + str(player.experience) +
                                 "/" + str(player.getExpForNextLevel()) + ")", 
                                 player, color='magenta', toAll=False)
        # Levelup is not performed here.
        
        
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
        player.cooldownList = []

    def removeTemporaryStatuses(self, player):
        '''Used to remove statuses that don't persist outside of combat'''
        removalList = [x for x in player.statusList if x.turnsLeft > -1]
        for removalStatus in removalList:
            Combat.removeStatus(player, removalStatus.name)

    def exit_combat(self, player, defeat=False):
        '''Removes the player from combat.'''
        self.server.pane[player.cPane].person.remove(player.id)
        player.cPane = None
        player.cLocation = None

        self.server.broadcast(Command("PERSON", "REMOVE", id=player.id), player.id)
        self.server.broadcast(Command("UPDATE", "COMBAT", combat=False), player.id)
        self.server.broadcast(Command("PERSON", "CREATE", id=player.id, \
                location=player.location, details=player.dehydrate()), player.id)
        self.server.send_world_items(player.id, player.location)
        for i in self.server.pane[player.location.pane].person:
            if i != player.id:
                self.server.broadcast(Command("PERSON", "CREATE", id=i, \
                        location=self.server.person[i].location, \
                        details=self.server.person[i].dehydrate()), player.id)

        self.server.unload_panes()
        self.server.broadcast(Command("CLIENT", "RESET_TARGETS", id=player.id), player.id)

    def monster_victory(self, combatPane):
        p = [p for i, p in self.server.person.iteritems() if p.location == combatPane][0]
        if self.combatStates[combatPane].turnTimer and self.combatStates[combatPane].turnTimer.active():
            self.combatStates[combatPane].turnTimer.cancel()
        
        p.ai.resume()
        p.cPane = None
        p.cLocation = None
        
    def softcoreDeath(self, player):
        '''Kicks player out of combat, back to Pane 0,0 and subtracts 10% of gold.
        Will restore HP/MP/AP to maximum, and remove all temporary status effects.'''
        goldLoss = player.inventory.gold / 10
        Combat.sendCombatMessage("You lose: " + str(goldLoss) + " gold for dying!",
                                player, color='darkred', toAll=False)
        player.inventory.gold -= goldLoss
        
        combatPane = player.cPane
        chars = [self.server.person[x] for x in self.server.pane[combatPane].person]
        players = [x for x in chars if x.team == "Players"]
        doMonsterVictory = False
        if players == [player]:
            # This player was the only one left.
            doMonsterVictory = True
        
        self.refillResources(player)
        self.removeTemporaryStatuses(player)
        self.server.broadcast(Command("CLIENT", "RESET_TARGETS", id=player.id), player.id)
        self.server.broadcast(Command("PERSON", "REMOVE", id=player.id), -player.id)
        self.server.broadcast(Command("UPDATE", "COMBAT", combat=False), player.id)

        respawn_location = Location((0, 0), (PANE_X / 2, PANE_Y / 2))
        self.server.pane[player.cPane].person.remove(player.id)
        self.server.pane[player.location.pane].person.remove(player.id)
        self.server.load_pane(respawn_location.pane)
        self.server.pane[respawn_location.pane].person.append(player.id)
        player.cPane = None
        player.cLocation = None
        player.location = respawn_location
        
        self.server.broadcast(Command("PERSON", "CREATE", id=player.id, \
                location=player.location, details=player.dehydrate()), -player.id)
        for i in self.server.pane[player.location.pane].person:
            if i != player.id:
                self.server.broadcast(Command("PERSON", "CREATE", id=i, \
                        location=self.server.person[i].location, \
                        details=self.server.person[i].dehydrate()), player.id)
        if doMonsterVictory:
            self.monster_victory(combatPane)

class CombatState(object):
    def __init__(self):
        self.turnTimer = None
        self.deadMonsterList = []
