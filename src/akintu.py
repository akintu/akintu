'''
Main startup point for Akintu
'''

import pygame
from pygame.locals import *

import sys

from game import Game


def main():
    pygame.init()
    game = Game()


if __name__ == "__main__":
    main()
