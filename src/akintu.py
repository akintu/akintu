'''
Main startup point for Akintu
'''

import pygame
from pygame.locals import *

import sys

from game import Game


def main():
    pygame.init()
    
    #TODO: all this can be changed when the menu is integrated
    #state is undefined right now, but we could pass in a directory
    #or a pickled object
    ip = None
    if len(sys.argv) != 1:
        ip = argv[1]
    game = Game("correcthorsebatterystaple!", ip, state=None)


if __name__ == "__main__":
    main()
