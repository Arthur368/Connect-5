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
        self.turn = "black"
        self.page = 1 # page 1 for game page

    def change_turn(self):

        if self.turn == "black":
            self.turn = "white"
        else:
            self.turn = "black"
    
    def game_page(self) -> None:

        # show the board
        self.current_board.draw(self.screen)

        # show all pieces
        for row in self.current_board.board_for_display:
            for piece in row:
                if piece != None:
                    piece.draw(self.screen)


    def tick(self) -> None:

        for event in pg.event.get():
    
            if event.type == pg.QUIT:
                pg.quit()
                exit()

            if self.page == 1:
                if event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:

                        pos = event.pos # position of press

                        row = int((pos[0] - 43 + 122/7) // (244/7))
                        col = int((pos[1] - 73 + 122/7) // (244/7))

                        if 0 <= row < 15 and 0 <= col < 15: # check if click inside the board
                            self.current_board.add_piece(row, col, self.turn) # turn is the same as color and type of a piece

                            if not self.current_board.is_terminal():
                                self.change_turn()
                            else:
                                pg.quit()
                                exit()

        self.game_page()

        pg.display.update()