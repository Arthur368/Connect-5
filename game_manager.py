from more_itertools import sample
import pygame as pg
from pygame.locals import *
from game_object import *

screen = pg.display.set_mode((800, 600))

class Game_manager:

    def __init__(self) -> None:
        self.screen = pg.display.set_mode((800, 600))
        self.running = True
        self.current_board = Board(20, 50, "images/board.jpg", 535, 535)
    
    def tick(self) -> None:

        for event in pg.event.get():
    
            if event.type == pg.QUIT:
                pg.quit()
                exit()

        sample_piece = Piece(43 - 122/7, 73, "images/black_piece.png", 244/7, 244/7)
        sample_piece_2 = Piece(43 + 122/7, 73, "images/black_piece.png", 244/7, 244/7)
        
        self.current_board.draw(self.screen)
        sample_piece.draw(self.screen)
        sample_piece_2.draw(self.screen)

        pg.display.update()