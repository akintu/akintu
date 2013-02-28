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
    ip = None
    if len(sys.argv) != 1:
        ip = argv[1]
    game = Game("CorrectHorseStapleBattery!", ip)


if __name__ == "__main__":
    main()
