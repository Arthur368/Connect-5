import pygame as pg
from pygame.locals import *
from game_manager import Game_manager
import sys
	
pg.init()

pg.display.set_caption("Gomoku(Five in a row)")

gm = Game_manager()

while True:
    gm.tick()