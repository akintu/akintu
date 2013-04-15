#!/usr/bin/python

import sys
import os
from const import *

HELP_COLOR = 'lightblue'
HELP_MAX_LINES = 70

def navigateUpPage(title):
    '''Returns the dictionary of the page that is 
    "Up one level" from the current page.  This page
    is the one that should be returned to via the use
    of the esacpe key (or whatever has been bound
    in its place.)
    Inputs:
      title -- The title of the current page
    Outputs:
      Dict -- The dictionary of the page one layer
                above the current page, or
                None, if this page is the top
                page.
    '''
    if title == "Akintu Help Menu":
        return None
    if title in topPages:
        return topPages["Akintu Help Menu"]
    for key in topPages:
        if title in topPages[key]['options']:
            return topPages[key]
    print "ERROR: Can not find help page"

def navigateDownPage(currentTitle, position):
    '''Moves down one page based on the position of the input
    given.  Because the screen is using an index-based system,
    this will use an index based system rather than a name-based
    system to prevent having to reorder and refactor every time
    a new page is added.
    
    Returns a page Dictionary or a string filepath and a string 
    indicating which it is.
    '''
    pageName = topPages[currentTitle]['options'][position]
    if currentTitle == "Akintu Help Menu":
        return (topPages[pageName], "Dict")
    elif contentPaths[pageName] == "RESERVED_STATUS_EFFECTS":
        return (contentPaths[pageName], "String")
    else:
        path = contentPaths[pageName]
        f = open(path, 'r')
        text = f.read()
        f.close()
        # The first line is a comment.
        text = text.partition("\n")[2]
        # The second line is just whitespace.
        text = text.lstrip()
        textArray = text.splitlines()
        lines = text.count("\n")
        gluedPages = []
        if len(textArray) <= HELP_MAX_LINES:
            gluedPages = [text]
        else:
            textPages = []
            finalPosition = 0
            for i in range(len(textArray) / HELP_MAX_LINES):
                textPages.append(textArray[HELP_MAX_LINES * i:HELP_MAX_LINES * (i+1)])
                finalPosition = i + 1
            textPages.append(textArray[HELP_MAX_LINES * finalPosition:])
            # Now glue them together
            for page in textPages:
                gluedPage = ""
                for line in page:
                    gluedPage += "\n"
                    gluedPage += line
                gluedPages.append(gluedPage)
        return (gluedPages, "Path", pageName)

    
    
topPages = {
    'Akintu Help Menu' : {
            'title' : "Akintu Help Menu",
            'options' : \
            ['Game Basics', 
             'Monsters Information',
             'Equipment Information',
             'Status Effects',
             'Advanced Topics'],
             'color' : HELP_COLOR
            },
    'Game Basics' : {
            'title' : "Game Basics",
            'options' : \
            ['Attributes',
             'Classes',
             'Controls',
             'Death',
             'How to play -- Combat',
             'How to play -- Overworld',
             'Inventory',
             'Level-up',
             'Races',
             'Treasure Chests'],
             'color' : HELP_COLOR
             },
    'Monsters Information' : {
            'title' : "Monsters Information",
            'options' : ["Monster Details"],
            'color' : HELP_COLOR
            },
    'Equipment Information' : {
            'title' : "Equipment Information",
            'options' : \
            ['Armor Tolerance',
             'Armor Types',
             'Magical Equipment',
             'Weapon Types'],
            'color' : HELP_COLOR
            },
    'Status Effects' : {
            'title' : "Status Effects",
            'options' : \
            ['Status Effect Basics',
             'Status Effect Listing'],
            'color' : HELP_COLOR
            },
    'Advanced Topics' : {
            'title' : 'Advanced Topics',
            'options' : \
            ['Alternate Weapon Set',
             'Basic Tactics',
             'Dodge and Accuracy',
             'DR and Penetration',
             'Elemental Damage/Resistance',
             'Experience Gain',
             'Magic Resist and Spellpower',
             'Poison Tolerance\Rating',
             'Size',
             'Sneak and Awareness',
             'Spell Schools',
             'Wiki'],
            'color' : HELP_COLOR
            }
    }
            
contentPaths = {
    'Attributes' : os.path.join(HELP_PATH, 'help_attributes.txt'),
    'Classes' : os.path.join(HELP_PATH, 'help_classes.txt'),
    'Controls' : os.path.join(HELP_PATH, 'help_controls.txt'),
    'Death' : os.path.join(HELP_PATH, 'help_death.txt'),
    'How to play -- Combat' : os.path.join(HELP_PATH, 'help_how_to_play_combat.txt'),
    'How to play -- Overworld' : os.path.join(HELP_PATH, 'help_how_to_play_overworld.txt'),
    'Inventory' : os.path.join(HELP_PATH, 'help_inventory.txt'),
    'Level-up' : os.path.join(HELP_PATH, 'help_levelup.txt'),
    'Races' : os.path.join(HELP_PATH, 'help_races.txt'),
    'Treasure Chests' : os.path.join(HELP_PATH, 'help_treasure_chests.txt'),
    
    'Monster Details' : os.path.join(HELP_PATH, 'help_monster_listing.txt'),
    
    'Armor Tolerance' : os.path.join(HELP_PATH, 'help_armor_tolerance.txt'),
    'Armor Types' : os.path.join(HELP_PATH, 'help_armor.txt'),
    'Magical Equipment' : os.path.join(HELP_PATH, 'help_magical_equipment.txt'),
    'Weapon Types' : os.path.join(HELP_PATH, 'help_weapons.txt'),
    
    'Status Effect Basics' : os.path.join(HELP_PATH, 'help_status_effect_basics.txt'),
    'Status Effect Listing' : 'RESERVED_STATUS_EFFECTS',
    
    'Alternate Weapon Set' : os.path.join(HELP_PATH, 'help_alternate_weapon_set.txt'),
    'Basic Tactics' : os.path.join(HELP_PATH, 'help_basic_tactics.txt'),
    'Dodge and Accuracy' : os.path.join(HELP_PATH, 'help_dodge_mechanics.txt'),
    'DR and Penetration' : os.path.join(HELP_PATH, 'help_DR_and_armor_penetration.txt'),
    'Elemental Damage/Resistance' : os.path.join(HELP_PATH, 'help_elements.txt'),
    'Experience Gain' : os.path.join(HELP_PATH, 'help_experience.txt'),
    'Magic Resist and Spellpower' : os.path.join(HELP_PATH, 'help_spellpower_and_magic_resist.txt'),
    'Poison Tolerance\Rating' : os.path.join(HELP_PATH, 'help_poison_mechanics.txt'),
    'Size' : os.path.join(HELP_PATH, 'help_size.txt'),
    'Sneak and Awareness' : os.path.join(HELP_PATH, 'help_stealth_and_hidden_objects.txt'),
    'Spell Schools' : os.path.join(HELP_PATH, 'help_spell_schools.txt'),
    'Wiki' : os.path.join(HELP_PATH, 'help_wiki.txt')
    }
    
            
            
            
            
            
            
            
             
             
