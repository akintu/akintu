'''
Main startup point for Akintu
'''

import pygame
from pygame.locals import *

import sys

from game import Game
from const import *
import welcome


def main():
    #JAB: Added this debugging backdoor to bypass the menu
    #argv[1] = "1" if server, anything else if client
    #argv[2] = character name
    port = 1337
    if len(sys.argv) > 1:
        num_players = sys.argv[1]
        name = sys.argv[2]
        player = (name, "Elf", "Assassin")
        state = {SEED_KEY: "fdsa"}
        if num_players == "1":
            ip = None
        else:
            ip = "localhost"
    else:
        player, state, ip, port = welcome.runwelcome()

    print str(port) + " " + str(ip) + " " + str(state) + " " + str(player)
    pygame.init()
    game = Game(port=port, serverip=ip, state=state, player=player)


if __name__ == "__main__":
    main()
