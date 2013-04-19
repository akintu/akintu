#!/usr/bin/python

import sys

# playercombatrecord.py
# Author: Devin Ekins -- G. Cube
#
# playercombatrecord is a glorified struct containing information about the
# current and last turn of a player.  It has modifier methods for readability
# of other modules.  
#
# Having this module seperate serves two purposes:
#   1. It keeps PlayerCharacter slightly smaller.
#   2. It allows for a place for us to add long term statistics about a player
#      in the event that we want "Achievements" such as, "Walked 10,000 spaces"
#      or the like.  This would be valuable if we were purchased by Steam.  

class PlayerCombatRecord(object):

    def __init__(self):
        self._previousTurnTilesMoved = -1
        self._previousTurnSpells = -1
        self._previousTurnTrapUse = -1
        self._previousTurnTrapSuccess = -1
        self._previousTurnRangedAttacks = -1
        self._previousTurnMeleeAttacks = -1
        self._previousTurnTrapChaos = -1
        
        self._currentTurnTilesMoved = 0
        self._currentTurnSpells = 0
        self._currentTurnTrapUse = 0
        self._currentTurnTrapSuccess = 0
        self._currentTurnRangedAttacks = 0
        self._currentTurnMeleeAttacks = 0
        self._currentTurnTrapChaos = 0
        
        self._trapsOwned = 0
    
    def nextTurn(self):
        '''Should be called immediately after a new turn begins (other than the first.)'''
        self._previousTurnTilesMoved = self._currentTurnTilesMoved
        self._previousTurnSpells = self._currentTurnSpells
        self._previousTurnTrapUse = self._currentTurnTrapUse
        self._previousTurnTrapSuccess = self._currentTurnTrapSuccess
        self._previousTurnRangedAttacks = self._currentTurnRangedAttacks
        self._previousTurnMeleeAttacks = self._currentTurnMeleeAttacks
        self._previousTurnTrapChaos = self._currentTurnTrapChaos
        
        self._currentTurnTilesMoved = 0
        self._currentTurnSpells = 0
        self._currentTurnTrapUse = 0
        self._currentTurnTrapSuccess = 0
        self._currentTurnRangedAttacks = 0
        self._currentTurnMeleeAttacks = 0
        self._currentTurnTrapChaos = 0
        
    # Modifier functions
        
    def recordMeleeAttack(self):
        self._currentTurnMeleeAttacks += 1
        
    def recordRangedAttack(self):
        self._currentTurnRangedAttacks += 1
        
    def recordMovement(self):
        self._currentTurnTilesMoved += 1
        
    def recordTrapFailure(self):
        self._currentTurnTrapUse += 1
        
    def recordTrapSuccess(self):
        self._currentTurnTrapUse += 1
        self._currentTurnTrapSuccess += 1
        
    def recordSpell(self):
        self._currentTurnSpells += 1
        
    def recordTrapPlacement(self):
        self._trapsOwned += 1
  
    def recordTrapRemoval(self):
        self._trapsOwned -= 1
        
    def recordTrapChaos(self):
        self._currentTurnTrapChaos += 1
    
    
    
    
    
        