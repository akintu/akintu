
from theorycraft import TheoryCraft
from pygame.locals import *

import ability
import passiveability
import trait
import spell

# levelup.py
# Author: Devin Ekins -- G. Cube
#
# levelup contains a Levelup object which houses temporary data needed for
# the leveling up process.  It is designed to present a simple, clean interface
# to other modules with only one method necessary, next().  It is built to
# minimize the chance of character data corruption/loss in the event that 
# the levelup is interrupted, such as via power loss to the host computer.
# The levelup process can be seen as a "transaction" that only takes effect
# after all choices have been made, and no sooner.


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
        ''' Method is called when the next (or first) phase of a levelup needs
        to be processed/displayed.  It will advance to the appropriate phase
        of this levelup process and prepare its data for the final character
        modifications. '''
        if not self.phase:
            self._determinePhaseList()
            self.phase = self.phaseList[0]
        if self.phase == "TRAIT":
            text = "Select a new trait or upgrade an existing one."
            self.traitOptions = self.player.getLevelupTraitOptions()
            self.screen.show_tiling_dialog(text, self.traitOptions, bgcolor="dodgerblue")
        elif self.phase == "SKILL":
            text = "Select a new skill."
            self.skillOptions = self.player.getLevelupSkillOptions()
            self.screen.show_tiling_dialog(text, self.skillOptions, bgcolor="cadetblue")
        elif self.phase == "SPELL_1":
            text = "Select a new spell."
            self.spellOptions = self.player.getLevelupSpellOptions()
            self.screen.show_tiling_dialog(text, self.spellOptions, bgcolor="lightblue")
        elif self.phase == "SPELL_2":
            text = "Select another new spell."
            self.spellOptions = [x for x in self.player.getLevelupSpellOptions() if
                                x.name != self.spellA.name]
            self.screen.show_tiling_dialog(text, self.spellOptions, bgcolor="lightblue")
        elif self.phase == "COMBO":
            text = "Additionally you have earned these unique skills."
            combos = self.player.getLevelupCombos()
            combosDisplay = [x for x in combos if '--IGNORE--' not in x.name]
            self.screen.show_tiling_dialog(text, combosDisplay, bgcolor="deepskyblue")
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
            summaryDisplay = [x for x in self.summary if '--IGNORE--' not in x.name]
            self.screen.show_tiling_dialog(text, summaryDisplay, bgcolor="darkturquoise")

    def advance(self):
        '''Returns a dehydrated player if this levelup is complete.'''
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
        ''' Method reserved, but currently unused.'''
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
