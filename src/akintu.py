'''
Main startup point for Akintu
'''

import pygame
from pygame.locals import *

import sys
import os

from game import Game
from const import *
import welcome


def main():
    # Create the saves directories if they don't exist
    if not os.path.exists(CHAR_SAVE_PATH):
        os.makedirs(CHAR_SAVE_PATH)
    if not os.path.exists(WORLD_SAVE_PATH):
        os.makedirs(WORLD_SAVE_PATH)

    #JAB: Added this debugging backdoor to bypass the menu
    #argv[1] = "1" if server, anything else if client
    #argv[2] = character name
    port = 1337
    if len(sys.argv) > 1:
        num_players = sys.argv[1]
        name = sys.argv[2]
        player = (name, "Elf", "Assassin")
        if len(sys.argv) > 3:  
            player = sys.argv[3]

        state = {SEED_KEY: "fdsa"}
        if num_players == "1":
            ip = None
        else:
            ip = "localhost"
        turnlength = -1
        ironman = True
        hardcore = False
    else:
        player, state, ip, port, turnlength, ironman, hardcore = \
            welcome.runwelcome()

    print str(port) + " " + str(ip) + " " + str(state) + " " + str(player)
    pygame.init()
    game = Game(port=port,
                serverip=ip,
                state=state,
                player=player,
                turnlength=turnlength,
                ironman=ironman,
                hardcore=hardcore)


if __name__ == "__main__":
    main()
