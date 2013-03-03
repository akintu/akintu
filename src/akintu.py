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
    player, state, ip, port = welcome.runwelcome()

    pygame.init()
    game = Game(port=port, serverip=ip, state=state, player=player)


if __name__ == "__main__":
    main()
