'''
Tile Object
'''

import os

from const import*
from sprites import*

class Tile(object):
    def __init__(self, image = os.path.join("res", "images", "background", "grass.png"), passable = True):
        self.entities = []
        self.obstacles = []
        self.items = []
        self.chest = None
        self.image = image
        self.passable = passable
        self.entity_keys = []

    def __repr__(self):
        return "(%s, %s, %s)" % (self.passable, self.image, self.entities)

    def set_image(self, image):
        self.image = image

    def is_passable(self, check_entity_keys=False):
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
        self.entity_keys.append(key)
    
    def add_item(self, entity):
        self.entities.append(entity)
        self.items.append(entity)
    
    def remove_item(self, item):
        if item == self.chest:
            self.chest = None
        if item in self.entities:
            self.entities.remove(item)
        if item in self.items:
            self.items.remove(item)
            
    def remove_items(self):
        for item in self.items:
            self.remove_item(item)
    
    def get_items(self):
        return self.items
        
    def add_obstacle(self, entity):
        self.entities.append(entity)
        self.obstacles.append(entity)
        
    def remove_obstacle(self, entity):
        assert False
        pass
        
    def get_obstacles(self):
        return self.obstacles
        
    def add_chest(self, chest):
        if self.chest:
            self.remove_item(self.chest)
        self.add_item(chest)
        self.chest = chest
        
    def remove_chest(self):
        self.remove_item(self.chest)
        self.chest = None
        
    def get_chest(self):
        return self.chest
        
