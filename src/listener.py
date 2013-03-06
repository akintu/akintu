#!/usr/bin/python

import sys
import broadcast

class Listener(object):
    def __init__(self, callObject, host, onStringList, action, offStringList=None):
        self.onStringList = onStringList
        self.action = action
        self.offStringList = offStringList
        self.host = host
        self.callObject = callObject

    def hear(self, bCast):
        for string in self.onStringList:
            if string == bCast.message.strip():
                if isinstance(bCast, broadcast.SpellBroadcast):
                    self.action(self.callObject, self.host, reverse=False, spell=bCast.spell)
                    return
                elif isinstance(bCast, broadcast.AttackBroadcast):
                    self.action(self.callObject, self.host, reverse=False, other=bCast.otherPerson)
                    return
                elif isinstance(bCast, broadcast.DamageBroadcast):
                    return self.action(self.callObject, self.host, reverse=False, damage=bCast.amount)
                elif isinstance(bCast, broadcast.StatusBroadcast):
                    self.action(self.callObject, self.host, reverse=False, statusName=bCast.statusName)
                    return
                elif isinstance(bCast, broadcast.ResourceLevelBroadcast):
                    self.action(self.callObject, self.host, reverse=False, percent = bCast.resourceLevel)
                    return
                elif isinstance(bCast, broadcast.DodgeBroadcast):
                    self.action(self.callObject, self.host, reverse=False)
                    return
                elif isinstance(bCast, broadcast.TurnBroadcast):
                    self.action(self.callObject, self.host, reverse=False)
                    return
        for string in self.offStringList:
            if string == bCast.message.strip():
                if isinstance(bCast, broadcast.SpellBroadcast):
                    self.action(self.callObject, self.host, reverse=True, spell=bCast.spell)
                    return
                elif isinstance(bCast, broadcast.AttackBroadcast):
                    self.action(self.callObject, self.host, reverse=True, other=bCast.otherPerson)
                    return
                elif isinstance(bCast, broadcast.DamageBroadcast):
                    self.action(self.callObject, self.host, reverse=True, damage=bCast.amount)
                    return
                elif isinstance(bCast, broadcast.StatusBroadcast):
                    self.action(self.callObject, self.host, reverse=True, statusName=bCast.statusName)
                    return
                elif isinstance(bCast, broadcast.ResourceLevelBroadcast):
                    self.action(self.callObject, self.host, reverse=True)
                    return
                elif isinstance(bCast, broadcast.DodgeBroadcast):
                    self.action(self.callObject, self.host, reverse=True)
                    return
                elif isinstance(bCast, broadcast.TurnBroadcast):
                    self.action(self.callObject, self.host, reverse=True)
                    return

