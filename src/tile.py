'''
Tile Object
'''

import os

from const import*
from sprites import*

class Tile(object):
    '''
    The Tile class handles the images and entities that
    gamescreen uses to draw the pane. If self.image isn't
    set, we use a default image to prevent the game from 
    crashing.
    A Tile can be passable or not, even without any entity
    objects. This is useful for things like water.
    '''
    def __init__(self, image = os.path.join("res", "images", "background", "grass.png"), passable = True):
        self.entities = []
        self.obstacles = []
        self.items = []
        self.chest = None
        self.trap = None
        self.image = image
        self.passable = passable
        self.entity_keys = []

    def __repr__(self):
        return "(%s, %s, %s)" % (self.passable, self.image, self.entities)

    def set_image(self, image):
        '''
        The background image of this tile.
        '''
        self.image = image
        
    def is_passable(self, check_entity_keys=False):
        '''
        Checks for 3 things:
            1. Is the tile object passable
            2. Are all the entities passable
            3. Are all the keys passable
        If any of these are False, the tile is not passable.
        '''
        if self.passable == False:
            return False
        for ent in self.entities:
            if ent.passable == False:
                return False
        if check_entity_keys:
            for key in self.entity_keys:
                if key in OBSTACLE_KEYS:
                    return False
        return True
        
    def add_entity_key(self, key):
        '''
        When we don't want to keep track of the entities
        in a pane, we keep track of the keys. This saves
        on resources and allows for non visible panes to
        be queried for passability.
        Soon to be depreciated.
        '''
        self.entity_keys.append(key)
    
    def add_entity(self, entity):
        '''
        Add an entity to this tile.
        '''
        self.entities.append(entity)
        
    def get_trigger_entities(self):
        '''
        Looks for all entities with a 'trigger' attribute.
        Returns a list of those entities.
        '''
        list = []
        for entity in self.entities:
            if hasattr(entity, 'trigger'):
                list.append(entity)
        return list
        
    def remove_entity(self, entity):
        '''
        Remove an entity from this tile.
        '''
        if entity in self.entities:
            self.entities.remove(entity)
        
    def clear_all_entities(self):
        '''
        When we want to recycle this tile, but reset its
        contents.
        '''
        self.entities = []
        self.obstacles = []
        self.items = []
        self.chest = None
        self.trap = None
        self.entity_keys = []
    
    def add_item(self, entity):
        '''
        Items are entities, but this can be used to maintain
        a separate list with this category.
        '''
        self.entities.append(entity)
        self.items.append(entity)
    
    def remove_item(self, item):
        '''
        Removes an item from this tile.
        '''
        if item == self.chest:
            self.chest = None
        if item in self.entities:
            self.entities.remove(item)
        if item in self.items:
            self.items.remove(item)
            
    def remove_items(self):
        '''
        Removes all items from this tile.
        '''
        for item in self.items:
            self.remove_item(item)
    
    def get_items(self):
        return self.items
        
    def add_obstacle(self, entity):
        '''
        Obstacles are entities, but not items. Trees
        and rocks fall into this category.
        '''
        self.entities.append(entity)
        self.obstacles.append(entity)
        
    def add_chest(self, chest):
        '''
        Only one chest can be placed on a tile, but
        we still allow other entity types to be placed.
        This allows for hidden treasure chests, or 
        mostly obscured treasure chests.
        '''
        if self.chest:
            self.remove_item(self.chest)
        self.add_item(chest)
        self.chest = chest
        
    def remove_chest(self):
        '''
        Removes the chest from this tile.
        '''
        self.remove_item(self.chest)
        self.chest = None
        
    def get_chest(self):
        '''
        Return the chest from this tile. None if no chest.
        '''
        return self.chest
        
    def addTrap(self, trap):
        '''
        Traps are like chests in that only one trap can be
        placed per tile.
        Soon to be depreciated
        '''
        if self.trap:
            self.remove_item(self.trap)
        self.add_item(trap)
        self.trap = trap
        
    def removeTrap(self):
        '''
        Remove the trap from this tile.
        '''
        if self.trap:
            self.remove_item(self.trap)
        self.trap = None
        
    def getTrap(self):
        '''
        If there is a trap, returns it. Otherwise None.
        '''
        return self.trap
        