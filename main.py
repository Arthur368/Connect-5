import imp
import pygame as pg
from pygame.locals import *
from game_manager import Game_manager
import sys
from pygame import mixer
	
pg.init()

pg.display.set_caption("Gomoku(Five in a row)")

title_icon = pg.image.load("Images/black_piece.png")
pg.display.set_icon(title_icon)

# background music
mixer.music.load("Sound/background.mp3")
mixer.music.play(-1) # loop 

gm = Game_manager()

while True:
    gm.tick()