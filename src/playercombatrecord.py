#!/usr/bin/python

import sys

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
    
    
    
    
    
        