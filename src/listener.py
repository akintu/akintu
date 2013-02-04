#!/usr/bin/python

import sys
import broadcast

class Listener(object):
    def __init__(self, host, onStringList, action, offStringList=None):
        self.onStringList = onStringList
        self.action = action
        self.offStringList = offStringList
        self.host = host
    
    def hear(self, bCast):
        for string in self.onStringList:
            if string == bCast.message.strip():
                if bCast.isinstance(broadcast.SpellBroadcast):
                    self.action(self.host, reverse=False, spell=bCast.spell)
                    return
                elif bCast.isinstance(broadcast.AttackBroadcast):
                    self.action(self.host, reverse=False, other=bCast.otherPerson)
                    return
        for string in self.offStringList:
            if string == bCast.message.strip():
                if bCast.isinstance(broadcast.SpellBroadcast):
                    self.action(self.host, reverse=True, spell=bCast.spell)
                    return
                elif bCast.isinstance(broadcast.AttackBroadcast):
                    self.action(self.host, reverse=True, other=bCast.otherPerson)
                    return                
            
        