
from theorycraft import TheoryCraft
from pygame.locals import *

import ability
import passiveability
import trait
import spell


class Levelup(object):
    def __init__(self, player, screen):
        self.player = player
        self.screen = screen
        self.phase = None
        self.phaseList = []
        self.skill = None
        self.spellA = None
        self.spellB = None
        self.trait = None
        self.summary = []
        
        self.traitOptions = []
        self.skillOptions = []
        self.spellOptions = []
        
    def next(self):
        if not self.phase:
            self._determinePhaseList()
            self.phase = self.phaseList[0]
        if self.phase == "TRAIT":
            text = "Select a new trait or upgrade an existing one."
            self.traitOptions = self.player.getLevelupTraitOptions()
            self.screen.show_dialog(text, self.traitOptions, bgcolor="dodgerblue")
        elif self.phase == "SKILL":
            text = "Select a new skill."
            self.skillOptions = self.player.getLevelupSkillOptions()
            self.screen.show_dialog(text, self.skillOptions, bgcolor="cadetblue")
        elif self.phase == "SPELL_1":
            text = "Select a new spell."
            self.spellOptions = self.player.getLevelupSpellOptions()
            self.screen.show_dialog(text, self.spellOptions, bgcolor="lightblue")
        elif self.phase == "SPELL_2":
            text = "Select another new spell."
            self.spellOptions = self.player.getLevelupSpellOptions()
            self.screen.show_dialog(text, self.spellOptions, bgcolor="lightblue")
        elif self.phase == "COMBO":
            text = "Additionally you have earned these unique skills."
            combos = self.player.getLevelupCombos()
            self.screen.show_dialog(text, combos, bgcolor="deepskyblue")
        elif self.phase == "SUMMARY":
            text = "This is a summary of the statistics and abilities you have gained."
            self.summary.append(self.trait)
            if self.skill:
                self.summary.append(self.skill)
            if self.spellA:
                self.summary.append(self.spellA)
            if self.spellB:
                self.summary.append(self.spellB)
            self.summary.append(self.player.getLevelupStats())
            self.screen.show_dialog(text, self.summary, bgcolor="darkturquoise")
        
    def input(self, keystroke):
        '''Returns True if this levelup is complete.'''
        if keystroke == K_RIGHT or keystroke == K_KP6 or keystroke == K_l:
            self.screen.move_dialog(6)
            return False
        elif keystroke == K_LEFT or keystroke == K_KP4 or keystroke == K_h:
            self.screen.move_dialog(4)
            return False
        elif keystroke == K_UP or keystroke == K_KP8 or keystroke == K_k:
            self.screen.move_dialog(8)
            return False
        elif keystroke == K_DOWN or keystroke == K_KP2 or keystroke == K_j:
            self.screen.move_dialog(2)
            return False
        elif keystroke == K_SPACE or keystroke == K_a:
            if self.phase == "TRAIT":
                self.trait = self.traitOptions[self.screen.hide_dialog()]
                self._advancePhase()
                return False
            elif self.phase == "SKILL":
                self.skill = self.skillOptions[self.screen.hide_dialog()]
                self._advancePhase()
                return False
            elif self.phase == "SPELL_1":
                self.spellA = self.spellOptions[self.screen.hide_dialog()]
                self.spellOptions.remove(self.spellA)
                self._advancePhase()
                return False
            elif self.phase == "SPELL_2":
                self.spellB = self.spellOptions[self.screen.hide_dialog()]
                self._advancePhase()
                return False
            elif self.phase == "COMBO":
                self.summary.extend(self.player.getLevelupCombos())
                self._advancePhase()
                return False
            elif self.phase == "SUMMARY":
                self._modifyHero()
                self.screen.hide_dialog()
                self.reset()
                return self.player.dehydrate()
                
    def _modifyHero(self):
        # skills are added via summary object.
        if self.spellA:
            self.player.spellList.append(spell.Spell(self.spellA.name, self.player))
        if self.spellB:
            self.player.spellList.append(spell.Spell(self.spellB.name, self.player))
        if self.trait.name in [x.name for x in self.player.traits]:
            for t in self.player.traits:
                if t.name == self.trait.name:
                    t.advanceTier()
        else:
            self.player.traits.append(trait.Trait(self.trait.name, self.player))
        for item in self.summary:
            if isinstance(item, ability.AbilityStub):
                self.player.abilities.append(ability.Ability(item.name, self.player))
            elif isinstance(item, passiveability.PassiveAbilityStub):
                self.player.passiveAbilities.append(passiveability.PassiveAbility(item.name, self.player))
        # Stats have already been added.
                
    def _advancePhase(self):
        currentPhaseIndex = self.phaseList.index(self.phase)
        self.phase = self.phaseList[currentPhaseIndex + 1]
        self.next()
        
    def _determinePhaseList(self):
        self.phaseList = ["TRAIT"]
        if self.player.level in self.player.skillLevels:
            self.phaseList.append("SKILL")
        if self.player.level in self.player.spellLevels:
            if self.player.spellLevels[self.player.level] == 1:
                self.phaseList.append("SPELL_1")
            elif self.player.spellLevels[self.player.level] == 2:
                self.phaseList.append("SPELL_1")
                self.phaseList.append("SPELL_2")
        self.phaseList.append("COMBO")
        self.phaseList.append("SUMMARY")
        
    def reset(self):
        self.phase = None
        self.phaseList = []
        self.skill = None
        self.spellA = None
        self.spellB = None
        self.trait = None
        self.summary = []
        
        self.traitOptions = []
        self.skillOptions = []
        self.spellOptions = []