'''
This class is an extension of server.py.  It is broken into two to keep the combat specific commands
separate from their overworld cousins.
'''

from network import *
import broadcast
from combat import *
from location import *
from dice import *
import theorycraft
import math
import region
import monster
import spell
import time

class CombatServer():
    def __init__(self, server):
        self.server = server
        self.combatStates = {}

    def handle(self, port, command):
        '''
        Validate incoming commands, update game state, and broadcast to clients that need to act on them
        '''
        ###### MovePerson ######
        if command.type == "PERSON" and command.action == "MOVE":
            activePlayer = self.server.person[command.id]

            # If this is a legal move request
            if ((hasattr(command, 'force') and command.force) or
                activePlayer.AP >= activePlayer.totalMovementAPCost or
                activePlayer.remainingMovementTiles > 0) and \
                self.server.tile_is_open(command.location, command.id):
                if activePlayer.team == "Players":
                    activePlayer.record.recordMovement()
                    if not (hasattr(command, 'force') and command.force):
                        if activePlayer.remainingMovementTiles == 0:
                            Combat.modifyResource(activePlayer, "AP", -activePlayer.totalMovementAPCost)
                            Combat.resetMovementTiles(activePlayer)
                        else:
                            Combat.decrementMovementTiles(activePlayer)

                # Update location and broadcast, including possible trap interactions.
                activePlayer.cLocation = command.location
                self.server.broadcast(command, -command.id, exclude=True)
                if activePlayer.team == "Players":
                    self.check_trap_trigger(activePlayer, activePlayer.cLocation)
                    self.check_field_trigger(activePlayer, activePlayer.cLocation)
                    self.check_turn_end(activePlayer.cPane)

            elif port:
                # Invalid move attempted, ensure we're back where we started.
                command.location = self.server.person[command.id].cLocation
                command.details = True
                self.server.broadcast(command, command.id)

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
                self.update_dead_people(self.server.person[command.id].cPane)
                del self.server.person[command.id]

                self.server.unload_panes()

        #### Attack Target ####
        elif command.type == "ABILITY" and command.action == "ATTACK":
            source = self.server.person[command.id]
            target = None
            if isinstance(command.targetId, Location):
                target = command.targetId
            else:
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
                if abilToUse.targetType != 'self' and abilToUse.targetType != 'location':
                    Combat.sendCombatMessage(source.name + " is using " + abilToUse.name + " on " + target.name,
                                             source, color=color)
                else:
                    Combat.sendCombatMessage(source.name + " is using " + abilToUse.name,
                                             source, color=color)
                abilToUse.use(target)
            else:
                Combat.sendCombatMessage(useDuple[1], source, toAll=False)
            self.check_turn_end(self.server.person[command.id].cPane)

        #### Place Trap or Use ability on location ####
        elif command.type == "ABILITY" and command.action == "PLACE_TRAP":
            source = self.server.person[command.id]
            abilToUse = None
            for abil in source.abilities:
                if abil.name == command.abilityName:
                    abilToUse = abil
            if abilToUse:
                useDuple = abilToUse.canUse(command.targetLoc)
                if useDuple[0]:
                    Combat.sendCombatMessage(source.name + " is placing a " + abilToUse.name, source,
                                             color='orange')
                    abilToUse.use(command.targetLoc)
                    self.server.broadcast(command, -command.id)
                else:
                    Combat.sendCombatMessage(useDuple[1], source, toAll=False)
                self.check_turn_end(self.server.person[command.id].cPane)

        #### End turn command "N" ####
        elif command.type == "ABILITY" and command.action == "END_TURN":
            target = self.server.person[command.id]
            Combat.modifyResource(target, "AP", -target.AP)
            Combat.decrementMovementTiles(target, removeAll=True)
            self.check_turn_end(self.server.person[command.id].cPane)

        #### Switch gear ####
        elif command.type == "ABILITY" and command.action == "SWITCH_GEAR":
            target = self.server.person[command.id]
            switchGearAP = 5
            if target.AP < switchGearAP:
                Combat.sendCombatMessage("Not enough AP to switch weapons (" + `switchGearAP` + " needed.)", target, toAll=False)
            else:
                Combat.sendCombatMessage("Switched Weapon Sets; new main weapon is: " + target.equippedItems.alternateWeapon.displayName,
                                            target, toAll=False)
                target.switchGear()
                self.server.broadcast(Command("ABILITY", "SWITCH_GEAR", id=target.id), pid=target.id)
                Combat.modifyResource(target, "AP", -switchGearAP)
                self.check_turn_end(self.server.person[command.id].cPane)
                # Gear swapping is performed on both server and client side (sadly).

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
                self.check_turn_end(user.cPane)
            else:
                itemMessage = usable[1]
                Combat.sendCombatMessage(itemMessage, user, color='white', toAll=False)

        if command.id in self.server.person:
            self.update_dead_people(self.server.person[command.id].cPane)

    ### Utility Methods ###

    def check_trap_discover(self, player):
        '''Iterates through every trap and attempts to discover its location (and report it to the player.)'''
        # Get a list of all hostile traps on the pane.
        combatPane = self.server.pane[player.cPane]
        hostileTraps = combatPane.hostileTraps

        # Iterate through the list checking to see if it was detected and is not yet visible, if so, add it to a set of traps.
        detectedTraps = []
        for trap in hostileTraps:
            if not trap.visible:
                difference = player.cLocation.distance(trap.location)
                if Dice.rollTrapDetect(trap, player, difference):
                    detectedTraps.append(trap)

        # Actually discover the trap.
        for trap in detectedTraps:
            self.discover_trap(trap, player)

    def discover_trap(self, trap, finder):
        '''Tells all players where a trap is, and who found it.'''
        Combat.sendCombatMessage(finder.name + " found a " + trap.name + "!", finder, color='beige')
        trap.visible = True
        action = Command("TRAP", "DISCOVER", id=finder.id, trapName=trap.name, trapLevel=trap.level, targetLoc=trap.location)
        self.server.broadcast(action, pid=-finder.id)

    def check_trap_trigger(self, actor, location):
        '''Checks to see if a monster or player just stepped on a trap
        at the given location, and if so, trigger the trap.  If the trap
        is out of charges, this will remove the trap.'''
        triggerEnts = self.server.pane[actor.cPane].get_trigger_entities(location)
        for tEnt in triggerEnts:
            if tEnt.shouldTrigger(actor):
                tEnt.trigger(actor)
            if tEnt.charges <= 0:
                try:
                    self.server.pane[actor.cPane].hostileTraps.remove(tEnt)
                except:
                    pass
                self.server.pane[actor.cPane].removeTrap(location, hostile=True)
                self.server.broadcast(Command("TRAP", "REMOVE", location=location), \
                        -actor.id)

    def check_field_trigger(self, actor, location):
        '''Checks to see if a monster or player just stepped on a status
        field.  If it did, it applies the effect(s) of the status field(s)
        to the actor.'''
        triggerFieldNames = self.server.pane[actor.cPane].fields.get_fields(location)
        for fName in triggerFieldNames:
            effect = spell.fieldEffects[fName]
            effect(actor)

    def update_fields(self, cPane):
        '''Checks the combat pane for status fields that need to be removed
        because they expired.'''
        pass
            
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
        if not combatPane:
            return

        allMonsters = [self.server.person[x] for x in self.server.pane[combatPane].person
                            if self.server.person[x].team == "Monsters"]
        toUpdateList = []
        for char in [self.server.person[x] for x in self.server.pane[combatPane].person]:
            if char.HP <= 0:
                if char.team == "Monsters":
                    toUpdateList.append(char)
                elif char.team == "Players":
                    if not char.hardcore:
                        Combat.sendCombatMessage(char.name + " has Fallen!", color='darkred', character=char)
                        if "Devil" in [m.name for m in allMonsters]:
                            Combat.sendCombatMessage("Puny mortal! You're no match for me!", color='orange', character=char, toAll=False)
                            Combat.sendCombatMessage("Your town needs you, " + char.name + ". Please free us from the Devil!", \
                                                        color='yellow', character=char, toAll=False)
                        self.softcoreDeath(char)
                    else:
                        Combat.sendCombatMessage(char.name + " has Perished!", color='darkred', character=char)
                        self.hardcoreDeath(char)
                    for id in self.server.pane[combatPane].person:
                        if self.server.person[id].team == "Monsters":
                            try:
                                self.server.personp[id].detectedPlayers.remove(char)
                            except:
                                # If the monster isn't in the list, this throws an error normally.
                                pass

        for char in toUpdateList:
            self.combatStates[combatPane].deadMonsterSet.add(char)
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

    def monsterMove(self, monster):
        ''' Makes a monster take a single step in a self-determined direction.'''
        player = monster.getNearestPlayer(monster.detectedPlayers)
        if not player:
            return "NO_MOVE"
        else:
            src = monster.cLocation
            dest = player.cLocation
            path = self.server.find_path(src, dest, monster.id)
            if len(path) <= 1:
                return "NO_MOVE"
            desiredLocation = path[0] # Src is not included in path.
            self.combatStates[monster.cPane].monsterStatusDict[monster] = "MOVING"
            action = Command("PERSON", "MOVE", id=monster.id, location=desiredLocation)
            self.server.SDF.queue.put((None, action))
            self.check_field_trigger(monster, desiredLocation)
            self.check_trap_trigger(monster, desiredLocation)
            # Monsters can die from traps.
            if monster.HP <= 0:
                return "DEAD"
            delay = monster.movementTime
            reactor.callLater(delay, self.monsterFinishedMoving, monster)
            return "MOVED"

    def monsterFinishedMoving(self, monster):
        '''Called to unlock a monster's state such that it may make another move
        or have its turn ended.'''
        combatPane = monster.cPane
        self.combatStates[combatPane].monsterStatusDict[monster] = "READY"

    ### Combat Phase Logic Methods ###

    def upkeep(self, target):
        '''Applies all upkeep operations for this Person.  (Used during the combat
        phase: "Upkeep"'''

        if target.team == "Players":
            target.record.nextTurn()
        if target.HPRegen > 0:
            Combat.healTarget(target, target, target.HPRegen)
        if target.MPRegen > 0:
            Combat.modifyResource(target, "MP", target.MPRegen)

        # Decrement status effects and cooldowns.
        for stat in target.statusList:
            stat.upkeepActivate(target)
            if stat.turnsLeft > 0:
                stat.turnsLeft -= 1
        target.decrementClientStatuses()
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

        # Reset remaining movement tiles.
        Combat.decrementMovementTiles(target, removeAll=True)

        # Decremenet the client's view of the statuses.
        action = Command("PERSON", "DECREMENT_STATUSES", id=target.id)
        self.server.broadcast(action, -target.id)

        # Enable for Debugging:
        # for stat in target.statusList:
            # if stat.turnsLeft == -1:
                # print target.name + " has status enabled: " + stat.name
            # else:
                # print target.name + " has status: " + stat.name + " T=" + `int(stat.turnsLeft)`

        # Check to see if this player discovered any traps.
        # Apply field effects as well.
        if target.team == "Players":
            self.check_trap_discover(target)
            self.check_field_trigger(target, target.cLocation)

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
            if self.server.turnTime > 0:
                self.combatStates[combatPane].turnTimer = reactor.callLater(self.server.turnTime, \
                        self.check_turn_end, combatPane, True)

        # Put player into combat -- Stop running if needed.
        currentPlayer.ai.remove("run")
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

        monsters = [self.server.person[x] for x in self.server.pane[combatPane].person
                    if self.server.person[x].team == "Monsters"]
        for mon in monsters:
            self.combatStates[combatPane].monsterStatusDict[mon] = "TURN_OVER"

        self.shout_turn_start(self.server.person[playerId], turn="Player")

    def check_turn_end(self, combatPane, timeExpired=False):
        ''' Check to see if the turn should end for players. '''
        if self.combatStates[combatPane].isMonsterTurn:
            return
        APRemains = False
        for player in [self.server.person[x] for x in self.server.pane[combatPane].person if x in
                self.server.player.values()]:
            if player.AP != 0 or player.remainingMovementTiles != 0:
                APRemains = True
                break
        if not APRemains:
            if not self.combatStates[combatPane].turnTimer:
                if self.server.turnTime > 0:
                    print "No timer found!"
            elif self.combatStates[combatPane].turnTimer.active():
                self.combatStates[combatPane].turnTimer.cancel()
        if timeExpired or not APRemains:
            self.end_turn(combatPane)


    def end_turn(self, combatPane):
        ''' Actually end the turn of all players. '''
        if self.update_dead_people(combatPane) == "CONTINUE_COMBAT":
            for character in [self.server.person[x] for x in self.server.pane[combatPane].person]:
                self.shout_turn_start(character, turn="Monster")
            print "Starting monster turn."
            self.combatStates[combatPane].isMonsterTurn = True
            self.monster_phase(combatPane, initial=True)

    def prepare_player_turn(self, combatPane):
        ''' Prepare the players' turns for starting.  Calls upkeep before starting the players' turns.'''
        for character in [self.server.person[x] for x in self.server.pane[combatPane].person]:
            self.upkeep(character)
        self.update_dead_people(combatPane)
        # New Turn here
        for character in [self.server.person[x] for x in self.server.pane[combatPane].person
                            if self.server.person[x].team == "Players"]:
            character.AP = character.totalAP
            self.server.broadcast(Command("PERSON", "UPDATE", id=character.id, AP=character.AP),
                    pane=combatPane)
            if character.hasStatus("Stun"):
                Combat.modifyResource(character, "AP", (-character.AP + 1))
        self.server.broadcast(Command("UPDATE", "TURNTIME"), pane=combatPane)
        for character in [self.server.person[x] for x in self.server.pane[combatPane].person]:
            self.shout_turn_start(character, turn="Player")
        if self.server.turnTime > 0:
            if self.combatStates[combatPane].turnTimer.active():
                self.combatStates[combatPane].turnTimer.cancel()
            self.combatStates[combatPane].turnTimer = reactor.callLater(self.server.turnTime, self.check_turn_end,
                    combatPane, True)
        skipPlayerTurn = True
        for character in [self.server.person[x] for x in self.server.pane[combatPane].person if self.server.person[x].team == "Players"]:
            if character.AP > 0:
                skipPlayerTurn = False
                break
        if skipPlayerTurn:
            self.check_turn_end(combatPane)
        print "Starting player turn."


    def monster_turn_over(self, combatPane):
        ''' Returns True if all monsters are done with their turns. '''
        chars = [self.server.person[x] for x in self.server.pane[combatPane].person]
        monsters = [x for x in chars if x.team == "Monsters" and x not in
                    self.combatStates[combatPane].deadMonsterSet]
        monFree = 0
        for mon in monsters:
            #print mon.name + " AP: " + str(mon.AP)
            if self.combatStates[combatPane].monsterStatusDict[mon] != "TURN_OVER":
                monFree += 1
        #print str(monFree)
        if monFree == 0:
            return True
        return False

    def monster_phase(self, combatPane, initial=False):
        ''' Is frequently called to determine monster combat AI and perform their
        interactions in combat according to whether they can move or not, based on
        their state in the monsterStatusDict dictionary.
            Will initialize monsters if initial = True for the start of their turns.
            Will quickly return if no monsters are available to move.
            Will start the player turn process if all monsters are incapable of
            further moves.'''
        #start = time.clock()

        if combatPane not in self.server.pane:
            return

        chars = [self.server.person[x] for x in self.server.pane[combatPane].person]
        players = [x for x in chars if x.team == "Players"]
        initMonsters = [x for x in chars if x.team == "Monsters" and x not in
                    self.combatStates[combatPane].deadMonsterSet]

        # Initialize Monster State
        if initial:
            for mon in initMonsters:
                if not mon.hasStatus("Stun"):
                    mon.AP = mon.totalAP
                    self.combatStates[combatPane].monsterStatusDict[mon] = "TURN_START"
                else:
                    self.combatStates[combatPane].monsterStatusDict[mon] = "TURN_OVER"

        monsters = [x for x in initMonsters if
                    self.combatStates[combatPane].monsterStatusDict[x] == "READY" or
                    self.combatStates[combatPane].monsterStatusDict[x] == "TURN_START"]
        if self.monster_turn_over(combatPane):
            #end = time.clock()
            #print str(end-start) + " turn over"
            self.prepare_player_turn(combatPane)
            self.combatStates[combatPane].isMonsterTurn = False
            return
        for mon in monsters:
            if self.combatStates[combatPane].monsterStatusDict[mon] == "TURN_START":
                mon.detectedPlayers = []
                self.check_field_trigger(mon, mon.cLocation)
                for player in players:
                    if not player.inStealth() or player.hasStatus("Conceal"):
                        mon.detectedPlayers.append(player)
                    elif mon.detectStealth(player):
                        mon.detectedPlayers.append(player)
                        Combat.sendCombatMessage("Detected " + player.name + "! (" +
                                     str(mon.totalAwareness) + " vs " + str(player.totalSneak) + ")",
                                    player, color='red')
                self.combatStates[combatPane].monsterStatusDict[mon] = "READY"

            if self.combatStates[combatPane].monsterStatusDict[mon] == "READY":
                # Try to use an ability.
                if mon.getUsableAbilities(self.server, combatPane, mon.detectedPlayers):
                    actionResult = mon.performAction(self.server, combatPane)
                    if actionResult == "Failure":
                        self.combatStates[combatPane].monsterStatusDict[mon] == "TURN_OVER"
                    else:
                        self.update_dead_people(combatPane)
                    continue
                # Try to move closer; does the monster have enough AP or movement tiles?
                else:
                    #print "Considering Movement"
                    if mon.remainingMovementTiles > 0:
                        #print mon.name + " has movement tiles left: " + `mon.remainingMovementTiles`
                        mon.remainingMovementTiles -= 1
                    elif mon.AP >= mon.totalMovementAPCost:
                        #print mon.name + " has AP left: " + `mon.AP`
                        mon.AP -= mon.totalMovementAPCost
                        mon.remainingMovementTiles = mon.totalMovementTiles - 1
                    else:
                        #print mon.name + " should be ending his turn."
                        self.combatStates[combatPane].monsterStatusDict[mon] = "TURN_OVER"
                        continue
                    moveResult = self.monsterMove(mon)
                    #print "Move Result: " + moveResult
                    if moveResult == "NO_MOVE":
                        self.combatStates[combatPane].monsterStatusDict[mon] = "TURN_OVER"
                    elif moveResult == "DEAD":
                        self.update_dead_people(combatPane)
                        self.combatStates[combatPane].monsterStatusDict[mon] = "TURN_OVER"
                    else:
                        continue
                        # The monster is currently moving.
        #end = time.clock()
        #print str(end-start) + " seconds to execute monster_phase()"
        if len([self.server.person[x] for x in self.server.pane[combatPane].person \
                if self.server.person[x].team == "Players"]) > 0:
            reactor.callLater(0.09, self.monster_phase, combatPane)

    def victory_phase(self, livingPlayers, combatPane):
        '''Cleans up arena, gives experience/gold to players,
        restores their health to full, and kicks them out of combat.'''
        state = self.combatStates[combatPane]
        if self.server.turnTime > 0 and state.turnTimer and state.turnTimer.active():
            state.turnTimer.cancel()

        monsterLeader = self.server.get_monster_leader(combatPane)
        self.server.SDF.queue.put((None, Command("PERSON", "REMOVE", id=monsterLeader.id)))

        for player in livingPlayers:
            self.giveVictoryExperience(player, state.deadMonsterSet)
            self.giveGold(player, state.deadMonsterSet)
            self.removeTemporaryStatuses(player)
            self.refillResources(player)
            self.exit_combat(player)

    #### End of Combat Phase Methods ####

    def giveVictoryExperience(self, player, monsterList):
        '''Grants the appropriate amount of EXP to a player at the end of
        a victorious combat.'''
        exp = Combat.calcExperienceGain(player, monsterList)
        player.addExperience(exp)
        if player.experience >= player.getExpForNextLevel() and player.level < 5: # Remove hardcoded value TODO
                Combat.sendCombatMessage(player.name + " LEVELUP!", player, color='magenta')
        Combat.sendCombatMessage("Gained " + str(exp) + " Experience. (" + str(player.experience) +
                                 "/" + str(player.getExpForNextLevel()) + ")",
                                 player, color='magenta', toAll=False)
        if "Devil" in [m.name for m in monsterList]:
            Combat.sendCombatMessage("You may have beaten me, mortal, but I have many friends!", player, color='orange', toAll=False)
            Combat.sendCombatMessage("Thank you " + player.name + "! You've driven the great evil from our town.", player, color='green', toAll=False)
        # Levelup is not performed here.

    def giveGold(self, player, monsterList):
        ''' Gives the appropriate amount of gold for victory to the specified
        player.'''
        gold = 0
        for monster in monsterList:
            gold += monster.level * 3 + monster.GP * 2
        player.inventory.addItem(gold)
        Combat.sendCombatMessage("Gained " + str(gold) + " gold. (total: " + str(player.inventory.gold) +
                                 ")", player, color='magenta', toAll=False)

    def refillResources(self, player):
        ''' Sets the resources of the specified player to their maximums.'''
        Combat.modifyResource(player, "MP", player.totalMP)
        Combat.modifyResource(player, "HP", player.totalHP)
        Combat.modifyResource(player, "AP", player.totalAP)
        player.cooldownList = []

    def removeTemporaryStatuses(self, player):
        '''Used to remove statuses that don't persist outside of combat.
        Currently all statuses are removed, as statuses aren't functioning
        properly when persisting.  This would be nice to implement later
        however. TODO'''
        removalList = [x for x in player.statusList]
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
                location=player.location, details=player.dehydrate(), checkLevelup=True), player.id)
        self.server.send_world_items(location=player.location, pid=player.id)
        for i in self.server.pane[player.location.pane].person:
            if i != player.id:
                self.server.broadcast(Command("PERSON", "CREATE", id=i, \
                        location=self.server.person[i].location, \
                        details=self.server.person[i].dehydrate()), player.id)

        self.server.unload_panes()

    def monster_victory(self, combatPane):
        '''
        Called when all players have died, and the monsters have won
        Starts the monsters moving around in the overworld again, and cleans up combat
        '''
        p = [p for i, p in self.server.person.iteritems() if p.location == combatPane]
        if len(p) > 0:
            p = p[0]
            if self.combatStates[combatPane].turnTimer and self.combatStates[combatPane].turnTimer.active():
                self.combatStates[combatPane].turnTimer.cancel()

            p.ai.resume()
            p.cPane = None
            p.cLocation = None

    def death(self, player):
        '''
        Cleans up combat for a player who has died, and restarts them in town
        '''

        combatPane = player.cPane
        chars = [self.server.person[x] for x in self.server.pane[combatPane].person]
        players = [x for x in chars if x.team == "Players"]
        doMonsterVictory = False
        if players == [player]:
            # This player was the only one left.
            doMonsterVictory = True

        self.refillResources(player)
        self.removeTemporaryStatuses(player)
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

    def hardcoreDeath(self, player):
        '''
        Cleans up combat for a player, deletes their save file, and recreates their character at level 1
        '''

        Combat.sendCombatMessage("You've Died Forever... HARDCORE!!", player, color='darkred', toAll=False)

        #Tell client to remove player's save file
        self.server.broadcast(Command("PERSON", "DELETE", id=player.id), player.id)

        new_char = theorycraft.TheoryCraft.getNewPlayerCharacter(
                            name=player.name, race=player.race, characterClass=player.characterClass,
                            ironman=player.ironman, hardcore=player.hardcore)
        new_char.location = player.location
        new_char.cLocation = player.cLocation
        new_char.cPane = player.cPane
        new_char.id = player.id
        new_char.ai.startup(self.server)

        self.server.person[player.id].ai.shutdown()
        self.server.person[player.id] = new_char

        self.death(new_char)
        self.server.broadcast(Command("CLIENT", "DEATH", id=new_char.id), new_char.id)

    def softcoreDeath(self, player):
        '''Kicks player out of combat, back to Pane 0,0 and subtracts 10% of gold.
        Will restore HP/MP/AP to maximum, and remove all temporary status effects.'''
        goldLoss = player.inventory.gold / 10
        Combat.sendCombatMessage("You lose: " + str(goldLoss) + " gold for dying!",
                                player, color='darkred', toAll=False)
        player.inventory.gold -= goldLoss
        self.death(player)


class CombatState(object):
    '''
    This is a container class for storing the Deferred objects generated when creating Delayed Calls
    '''
    def __init__(self):
        self.turnTimer = None
        self.deadMonsterSet = set([])
        self.monsterStatusDict = {}
        # Has form: Monster : 'READY'
        # or Monster : 'MOVING'
        # or Monster : 'TURN_START'
        # or Monster : 'TURN_OVER'
        self.isMonsterTurn = False
        # Used as a lock for turn end processing.



