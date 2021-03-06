from network import *
from location import *
from region import Region
from Queue import PriorityQueue
from theorycraft import TheoryCraft
from playercharacter import *
from servercombat import *
from combat import *
from state import State
from portal import Portal
import shop

class GameServer():
    def __init__(self, world, port, turnTime):
        self.world = world
        self.SDF = ServerDataFactory()
        self.CS = CombatServer(self)
        Combat.gameServer = self
        reactor.listenTCP(port, self.SDF)
        self.turnTime = turnTime

        LoopingCall(self.server_loop).start(0)

        self.player = {}  # {Port: PersonID} Dict of all players, pointing to their personid
        self.person = {} # {PersonID: Person} Dict of all persons
        self.pane = {}  # {location.Pane: Pane} Dict of actual pane objects
        self.shops = {} # {Pane : Shop} Dict of Shop objects

    def server_loop(self):
        '''
        Network.py fills SDF.queue with commands from the clients
        server_loop handles them in the general pattern of validating the command, updating the game
        state, and then broadcasting the command to everyone else who needs to act on it.
        '''
        while not self.SDF.queue.empty():
            port, command = self.SDF.queue.get()

            if command.type == "PERSON" and command.action == "REMOVE" and port \
                    and not hasattr(command, 'id'):
                command.id = self.player[port]
            if hasattr(command, 'id') and (command.id in self.person and self.person[command.id].cPane):
                self.CS.handle(port, command)
                continue
            if hasattr(command, 'id') and not (command.type == "PERSON" and command.action in \
                    ["CREATE", "LOAD"]) and command.id not in self.person:
                continue

            ###### CreatePerson ######
            if command.type == "PERSON" and (command.action == "CREATE" or command.action == "LOAD"):
                self.load_pane(command.location.pane)
                if command.action == "LOAD":
                    person = TheoryCraft.rehydratePlayer(command.details)
                elif command.action == "CREATE":
                    person = TheoryCraft.convertFromDetails(command.details)
                person.id = id(person)
                command.id = person.id
                person.ai.startup(self)

                if port:
                    self.player[port] = person.id
                self.person[person.id] = person
                self.pane[command.location.pane].person.append(person.id)
                if port:
                    self.broadcast(Command("UPDATE", "SEED", seed=self.world.seed), command.id)
                    self.broadcast(Command("UPDATE", "TURNTIME", turnTime=self.turnTime), command.id)

                # Send command to each player in the affected pane
                self.broadcast(command, -command.id)

                # Send list of players to the issuing client
                if port:
                    for i in self.pane[command.location.pane].person:
                        if i != command.id:
                            comm = Command("PERSON", "CREATE", id=i, \
                                    location=self.person[i].location, \
                                    details=self.person[i].dehydrate())
                            self.broadcast(comm, port=port)

                    self.send_world_items(command.location, port=port)

            ###### MovePerson ######
            if command.type == "PERSON" and command.action == "MOVE":
                self.load_pane(command.location.pane)

                portal=command.portal if hasattr(command, "portal") else None
                iLoc = command.iLocation if hasattr(command, "iLocation") else None
                if command.id in self.person:
                    if iLoc:
                        self.person[command.id].iLocation = iLoc
                    else:
                        iLoc = self.person[command.id].iLocation

                # If this is a legal move request
                if self.tile_is_open(command.location, pid=command.id, portal=portal, iLoc=iLoc):
                    if not portal:
                        #Check for entities that have a trigger() attribute
                        p = iLoc if iLoc in self.pane else command.location.pane if command.location.pane in self.pane else None
                        if command.location.pane in self.pane and not iLoc:
                            ent_list = self.pane[command.location.pane].get_trigger_entities(command.location)
                        elif iLoc in self.pane:
                            ent_list = self.pane[iLoc].get_trigger_entities(command.location)
                        for entity in ent_list:
                            portal_loc, new_loc = entity.trigger()
                            # print "PORTAL LOCATION: " + str(portal_loc)
                            # self.SDF.queue.put((None, Command("PERSON", "MOVE", id=command.id, portal=entity, iLocation=portal_loc, location=new_loc)))
                            #"SHOP" and command.action == "REQUESTSHOP"
                            if entity.portal_type == Portal.SHOP:
                                self.SDF.queue.put((None, Command("SHOP", "REQUESTSHOP", id=command.id)))

                    # If the origin and destination are in the same pane
                    if self.person[command.id].location.pane == command.location.pane:
                        # Update location and broadcast
                        self.person[command.id].location = command.location
                        self.broadcast(command, -command.id, exclude=True if port else False)
                    else:
                        # Remove person from players' person tables, and pane's person list
                        self.pane[self.person[command.id].location.pane].person.remove(command.id)
                        self.broadcast(Command("PERSON", "REMOVE", id=command.id), -command.id)

                        # Update location in server memory
                        self.person[command.id].location = command.location

                        # Add player to new pane lists and send to clients in the affected pane
                        self.pane[command.location.pane].person.append(command.id)
                        command.action = "CREATE"
                        command.details = self.person[command.id].dehydrate()
                        self.broadcast(command, pane=command.location.pane)

                        # Send list of players to the issuing client
                        if command.id in self.player.values():
                            for i in self.pane[command.location.pane].person:
                                if i != command.id:
                                    comm = Command("PERSON", "CREATE", id=i, \
                                            location=self.person[i].location, \
                                            details=self.person[i].dehydrate())
                                    self.broadcast(comm, command.id)

                            # HANDLE SENDING SPECIFIC PANE THINGS HERE
                            self.send_world_items(command.location, pid=command.id)

                        self.unload_panes()

                    # Check for combat range and initiate combat states
                    if command.id in self.player.values():
                        for person in self.pane[self.person[command.id].location.pane].person:
                            if self.person[command.id].location.in_melee_range( \
                                    self.person[person].location) and \
                                    self.person[person].team == "Monsters":
                                self.CS.startCombat(command.id, person)

                else:
                    if port:
                        command.location = self.person[command.id].location
                        command.details = True
                        self.broadcast(command, port=port)

            ###### RemovePerson ######
            if command.type == "PERSON" and command.action == "REMOVE":
                if command.id in self.person:
                    if port:
                        command.id = self.player[port]
                        del self.player[port]

                    self.pane[self.person[command.id].location.pane].person.remove(command.id)
                    self.broadcast(command, -command.id)
                    del self.person[command.id]
                    self.unload_panes()

            ###### Levelup Player ######
            if command.type == "PERSON" and command.action == "REPLACE":
                newPerson = TheoryCraft.rehydratePlayer(command.player)
                newPerson.location = self.person[command.id].location
                newPerson.id = command.id
                self.person[command.id] = newPerson
                self.broadcast(command, -command.id, exclude=True)

            #### Shop Creation ####
            if command.type == "SHOP" and command.action == "REQUESTSHOP":
                activePlayer = self.person[command.id]
                requestedPane = self.pane[activePlayer.location.pane]
                if self.world.is_town_pane(activePlayer.location):
                    currentShop = None
                    if requestedPane not in self.shops:
                        level = requestedPane.paneLevel
                        currentShop = shop.Shop(level=level)
                        self.shops[requestedPane] = currentShop
                    else:
                        currentShop = self.shops[requestedPane]
                    action = Command("SHOP", "OPEN", id=command.id,
                                     shopLevel=currentShop.level, shopSeed=currentShop.seed)
                    self.broadcast(action, pid=command.id)

            #### Respec ####
            if command.type == "RESPEC" and command.action == "REQUESTRESPEC":
                activePlayer = self.person[command.id]
                if self.world.is_town_pane(activePlayer.location):
                    if activePlayer.ironman:
                        text = "You are on Ironman mode, and are thus too cool to respec!"
                        action = Command("UPDATE", "TEXT", text=text, color='white')
                        self.broadcast(action, pid=activePlayer.id)
                    elif activePlayer.level > 1:
                        oldExp = activePlayer._experience
                        newHero = TheoryCraft.resetPlayerLevel(activePlayer)
                        newHero.location = self.person[command.id].location
                        newHero.id = command.id
                        newHero._experience = oldExp
                        self.person[command.id] = newHero
                        jerky = newHero.dehydrate()

                        # Send the newHero to the client.
                        action = Command("PERSON", "REPLACE", id=command.id, player=jerky)
                        self.broadcast(action, pid=-command.id)

            ###### Get Item / Open Chest ######
            if command.type == "PERSON" and command.action == "BASHCHEST":
                activePlayer = self.person[command.id]
                currentPane = self.pane[activePlayer.location.pane]
                chest, loc = currentPane.get_treasure_chest(activePlayer.location)
                if chest:
                    if chest.locked:
                        success = chest.bash(activePlayer)
                        if success:
                            chest.locked = False
                            text = activePlayer.name + " successfully bashed open a chest."
                            action = Command("UPDATE", "TEXT", text=text, color='lightskyblue')
                            self.broadcast(action, pid=-activePlayer.id)
                        else:
                            text = activePlayer.name + " failed to bash open a chest."
                            action = Command("UPDATE", "TEXT", text=text, color='red')
                            self.broadcast(action, pid=-activePlayer.id)
                    else:
                        text = "No need to bash -- chest is unlocked."
                        action = Command("UPDATE", "TEXT", text=text, color='white')
                        self.broadcast(action, pid=activePlayer.id)
            if command.type == "PERSON" and command.action == "OPEN":
                activePlayer = self.person[command.id]
                currentPane = self.pane[activePlayer.location.pane]
                chest, loc = currentPane.get_treasure_chest(activePlayer.location)
                if chest and chest.locked:
                    picklockSuccess = chest.pickLock(activePlayer)
                    if picklockSuccess:
                        chest.locked = False
                        text = activePlayer.name + " successfully unlocked a chest."
                        action = Command("UPDATE", "TEXT", text=text, color='lightskyblue')
                        self.broadcast(action, pid=-activePlayer.id)
                    else:
                        text = "The chest is locked"
                        if activePlayer.lockpicking > 0:
                            # This is a class that *could* unlock it with more Cunning.
                            text += " and you lack the Cunning to unlock it."
                        action = Command("UPDATE", "TEXT", text=text, color='red')
                        self.broadcast(action, pid=-activePlayer.id)
                    return
                if chest and not chest.locked:
                    inventories = chest.open(self.get_nearby_players(command.id))
                    currentPane.remove_chest(loc)

                    #Notify clients in the affected pane
                    for p, i in self.player.iteritems():    #Replace this with list of players on current pane
                        if self.person[i].location.pane == self.person[command.id].location.pane:
                            #Send animation request...
                            action_animate = Command(type="ENTITY", action="ANIMATE", location=loc)
                            self.broadcast(action_animate, port=p)
                            action_remove = Command(type="CHEST", action="REMOVE", location=loc)
                            self.broadcast(action_remove, port=p)

                            thisPlayer = self.person[self.player[p]]
                            itemList = inventories[thisPlayer]
                            if not itemList:
                                action = Command("UPDATE", "TEXT", text='Chest was empty', color='lightskyblue')
                                self.broadcast(action, port=p)
                            for item in itemList:
                                equipped = False
                                action = None
                                if isinstance(item, int):
                                    action = Command("ITEM", "CREATE", itemIdentifier=item, id=thisPlayer.id)
                                else:
                                    action = Command("ITEM", "CREATE", itemIdentifier=item.identifier, id=thisPlayer.id)
                                self.broadcast(action, port=p)
                                if thisPlayer.shouldAutoEquip(item):
                                    thisPlayer.equip(item)
                                    action = Command("ITEM", "EQUIP", itemIdentifier=item.identifier, id=thisPlayer.id)
                                    self.broadcast(action, port=p)
                                    equipped = True
                                text = ''
                                if isinstance(item, int):
                                    text = 'Found ' + `item` + ' pieces of gold.'
                                else:
                                    text = 'Found item: ' + item.displayName
                                if equipped:
                                    text ='Found and equipped item: ' + item.displayName
                                action = Command("UPDATE", "TEXT", text=text, color='lightskyblue')
                                self.broadcast(action, port=p)
                                thisPlayer.refreshAP()
                            action = Command("PERSON", "UPDATE", id=thisPlayer.id, AP=thisPlayer.AP, totalAP=thisPlayer.totalAP)
                            self.broadcast(action, port=p)
            # Get items: TODO

    ###### Utility Methods ######

    def broadcast(self, command, pid=None, port=None, pane=None, exclude=False):
        '''
        Broadcast a given command to a player or all players in a pane.
        Accepts one of a port, a person id (pid), or a pane.  (Do not pass in more than one!)
        If exclude is True, then command will be sent to all players in affected pane except
                for the player indicated by pid or port.
        Will only broadcast to human players, never to NPCs!
        If a port or id is given and is a negative value, the command will be broadcast
                to all players in the same pane as the player indicated.
        If a port or id is given and is a positive value, the command will be broadcast
                only to that player.
        '''
        sendToAll = True
        if port:
            sendToAll = True if port < 0 else False
            port = abs(port)
            playerkey = self.player[port]
            person = self.person[playerkey]#self.player[port]]
            pane = person.cPane if person.cPane else person.location.pane
        elif pid:
            sendToAll = True if pid < 0 else False
            pid = abs(pid)
            person = self.person[pid]
            pane = person.cPane if person.cPane else person.location.pane

        if sendToAll:
            for p, i in self.player.iteritems():
                if (self.person[i].cPane and self.person[i].cPane == pane) or \
                        (not self.person[i].cPane and self.person[i].location.pane == pane):
                    if not exclude or (i != pid and p != port):
                        self.SDF.send(p, command)
        else:
            if not port:
                port = [p for p, i in self.player.iteritems() if i == pid][0]
            self.SDF.send(port, command)

    def send_world_items(self, location, pid=None, port=None):
        '''
        The server keeps track of all consumables and sends them
        to the clients using this method.  Currently only chests
        are transmitted.  If we add items to the world, this is
        where you would send them.
        Uses the server's copy of the pane to determine what gets
        sent.
        '''
        if isinstance(location, Location):
            pane = location.pane
        else:
            pane = location
        chests = self.pane[pane].get_chest_list()
        # CHESTS
        if chests:
            for chest in chests:
                cmd = Command("CHEST", "ADD", chestType=chest[0], level=chest[1], location=Location(pane, chest[2]))
                self.broadcast(cmd, pid, port)
        # ITEMS (When added)

    def tile_is_open(self, location, pid=None, cPane=None, iLoc=None, portal=False):
        '''
        Uses the location, person id (pid), and cPane to figure out which pane is being evaluated.
        Then tests for obstacles on the pane, portals, and people acting as obstacles
        Returns false if the listed person may not move to the location.
        True otherwise
        '''

        if portal:  #Ensures we can take the portal, even if a player is on the other end
            return True
        if location.pane not in self.pane and not pid and not cPane:
            return False
        if not cPane and pid and pid in self.person and self.person[pid].cPane:
            cPane = self.person[pid].cPane
        loc = 'cLocation' if cPane else 'location'
        p = cPane if cPane else iLoc if iLoc else location.pane

        if not self.pane[p].is_tile_passable(location):
            return False
        if location.tile in [getattr(self.person[i], loc).tile for i in self.pane[p].person if i != pid]:
            return False
        if "Pit" in self.pane[p].fields.get_fields(location):
            return False
        return True

    def load_pane(self, pane, pid=None):
        '''
        Loads a pane that a person is moving onto into memory
        '''
        if pane not in self.pane:
            print("Loading pane " + str(pane))
            if pid:
                numPlayers = len([x for x in self.player.values() if self.person[x].location.pane == self.person[pid].location.pane])
                self.pane[pane] = self.pane[pane.pane].get_combat_pane(pane, self.person[pid], numPlayers)
                for i, p in self.pane[pane].person.iteritems():
                    p.cLocation = p.location
                    p.location = None
                    p.cPane = pane
            else:
                self.pane[pane] = self.world.get_pane(pane, True)

            # Add all people in pane to global person table, then replace pane's person list with
            # a list of personIDs
            self.person.update(self.pane[pane].person)
            self.pane[pane].person = self.pane[pane].person.keys()
            for p in self.pane[pane].person:
                self.person[p].id = id(self.person[p])
                self.person[p].ai.startup(self)
            #print self.pane.keys()

    def unload_panes(self, unloadAll=False):
        '''
        This is called whenever someone leaves a pane, but like a garbage collector, is not guaranteed
        to unload anything.  But it checks for panes that have nobody in an adjacent pane (because
        there's a reasonable chance they'll move back onto this pane) and only then unloads it
        '''
        current_panes = []
        for i in self.player.values():
            if self.person[i].cPane:
                current_panes.append(self.person[i].cPane)
            x, y = self.person[i].location.pane
            for (dx, dy) in [(_x, _y) for _x in range(-1, 2) for _y in range(-1, 2)]:
                current_panes.append((x + dx, y + dy))
        if unloadAll:
            current_panes = []
        for pane in self.pane.keys():
            #if pane not in current_panes and not (unloadAll and isinstance(pane, Location)):
            if pane not in [p.location.pane if p.location else p.cPane for p in self.person.values()]:
                print("Unloading pane " + str(pane))
                people = {}
                # Stop all AI behaviors
                for i in self.pane[pane].person:
                    self.person[i].ai.shutdown()
                    if i not in self.player.values():
                        people[i] = self.person[i]
                    del self.person[i]
                self.pane[pane].person = people

                self.pane[pane].save_state()
                del self.pane[pane]

    def save_all(self, shutdown=True):
        '''
        Save all panes without destroying them in the process
        '''
        if shutdown:
            self.unload_panes(True)
        else:
            for pane in self.pane.keys():
                #Save ID list of pane
                tmp_people_list = self.pane[pane].person
                if pane in self.pane:
                    people = {}
                    for i in self.pane[pane].person:
                        #self.person[i].ai.shutdown()
                        if i not in self.player.values():
                            people[i] = self.person[i]
                    self.pane[pane].person = people
                    self.pane[pane].save_state()
                    #Restore ID list of pane
                    self.pane[pane].person = tmp_people_list

        State.save_world()

    def get_nearby_players(self, personId):
        '''
        Accepts a personId and returns a list of players on the same pane.
        Works with overworld panes and combat panes
        '''
        pane = self.person[personId].cPane if self.person[personId].cPane else \
                self.person[personId].location.pane
        return [self.person[i] for i in self.player.values() if i in self.pane[pane].person]

    def get_monster_leader(self, cPane):
        '''
        The monster on the overworld that spawns the group you enter combat with is the "Monster Leader"
        Given a combatPane, this method returns the MonsterLeader so that he can be deleted.
        '''
        for p in self.person.values():
            if cPane == p.location:
                return p

    def find_path(self, loc1, loc2, pid=None, cPane=None):
        '''
        Pathfinding algorithm using a tweaked implementation of Dijkstra's Algorithm
        The difference is that we may not need a path directly to loc2.  If pid refers to a valid
        Person object, we just need a path to the closest location that is within attack range of
        the final target.  So loop through all possible locations searching for the location with the
        shortest path, and return that.
        '''
        if loc1 == loc2:
            return []
        if loc1.distance(loc2) == 1:
            return [loc2]

        Q = Region("SQUARE", Location(loc1.pane, (0, 0)), Location(loc1.pane, (PANE_X - 1, PANE_Y - 1))).locations
        dist = {}
        prev = {}
        q = PriorityQueue()
        for v in Q:
            dist[v] = float('inf')
            prev[v] = None

        dist[loc1] = 0
        q.put((0, loc1))

        while not q.empty():
            u = q.get()[1]
            if u == loc2 or dist[u] == float('inf'):
                break

            neighbors = [u.move(dir) for dir in [2, 4, 6, 8]]
            neighbors = [v for v in neighbors if v in Q and (self.tile_is_open(v, pid, cPane) or v == loc2)]
            for v in neighbors:
                Q.remove(v)
                alt = dist[u] + u.distance(v)
                if alt < dist[v]:
                    dist[v] = alt
                    prev[v] = u
                    q.put((dist[v], v))

        path = []
        u = loc2

        # Update destination to a location within attack range of the ultimate target
        if pid:
            minDist = (dist[u], u)
            for loc in [l for l in Region("DIAMOND", u, self.person[pid].attackRange - 1) if l.pane == loc1.pane]:
                if prev[loc] and dist[loc] < minDist[0]:
                    minDist = (dist[loc], loc)
            u = minDist[1]

        # If still no valid destination, find the closest point in anticipation of an obstacle
        # eventually being removed, such as an ally getting killed
        radius = 1
        while not prev[u] and radius < 10:
            R = Region("SQUARE", loc2, radius) - Region("SQUARE", loc2, radius - 1)
            for loc in [l for l in R if l.pane == loc1.pane]:
                if prev[loc]:
                    u = loc
                    break
            radius += 1

        # Follow the path backwards from destination to reconstitute the shortest path
        while prev[u]:
            path.append(u)
            u = prev[u]

        path.reverse()
        return path
