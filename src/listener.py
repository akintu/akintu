#!/usr/bin/python

import sys
import broadcast

class Listener(object):
    def __init__(self, host, onString, action, offString=None):
        self.onString = onString
        self.action = action
        self.offString = offString
        self.host = host
    
    def hear(self, bCast, spell=None):
        if self.onString == bCast.message.strip():
            if bCast.isinstance(broadcast.SpellBroadcast):
                self.action(self.host, spell, reverse=False)
            elif bCast.isinstance(broadcast.AttackBroadcast):                
                self.action(self.host, reverse=False)
                
        elif self.offString and self.offString == bCast.message.strip():
            if bCast.isinstance(broadcast.SpellBroadcast):
                self.action(self.host, spell, reverse=True)
            elif bCast.isinstance(broadcast.AttackBroadCast): 
                self.action(self.host, reverse=True)
        