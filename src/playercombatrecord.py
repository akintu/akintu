#!/usr/bin/python

import sys

class PlayerCombatRecord(object):

    '''This class will eventually be extended to record
    interesting feats this character has performed, such as
    how many monsters were killed by this player or whether
    they leveled from 1 to 20 without every wearing a using
    a physical attack or drinking a potion.
    
    This purpose may not be a great idea, and even if it is
    it might not be best to implement it here, that said...
    
    For now, it is used to track some combat state relative
    to a single player.  Is used and interacted with by 
    traits, passive abilities, and even some active abilities.
    '''
	def __init__(self):
		self._previousTurnTilesMoved = -1;
        self._previousTurnSpells = -1;
        self._previousTurnTrapUse = -1;
        self._previousTurnTrapSuccess = -1;
        self._previousTurnRangedAttacks = -1;
        self._previousTurnMeleeAttacks = -1;
        
        self._currentTurnTilesMoved = 0;
        self._currentTurnSpells = 0;
        self._currentTurnTrapUse = 0;
        self._currentTurnTrapSuccess = 0;
        self._currentTurnRangedAttacks = 0;
        self._currentTurnMeleeAttacks = 0;
		
        self._trapsOwned = 0;
        
    def nextTurn(self):
        '''Should be called immediately after a new turn begins (other than the first.)'''
        self._previousTurnTilesMoved = self._currentTurnTilesMoved;
        self._previousTurnSpells = self._currentTurnSpells;
        self._previousTurnTrapUse = self._currentTurnTrapUse;
        self._previousTurnTrapSuccess = self._currentTurnTrapSuccess;
        self._previousTurnRangedAttacks = self._currentTurnRangedAttacks;
        self._previousTurnMeleeAttacks = self._currentTurnMeleeAttacks;
        
        self._currentTurnTilesMoved = 0;
        self._currentTurnSpells = 0;
        self._currentTurnTrapUse = 0;
        self._currentTurnTrapSuccess = 0;
        self._currentTurnRangedAttacks = 0;
        self._currentTurnMeleeAttacks = 0;
        
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
    
    # Query Functions
    #  Context is assumed to be the current turn
    #  unless otherwise mentioned.
    
    # TODO? Should we just use this as a struct?
    
    
    
    
    
        