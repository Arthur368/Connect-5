from tkinter import SINGLE
import pygame as pg
from pygame.locals import *
from game_object import *
from enum import Enum
from Search_tree import Node, Game_Tree

#screen = pg.display.set_mode((800, 600))

# a enumeration for game pages.
class Game_pages(Enum):
    START_PAGE = 0
    MULTI_PLAYER = 1
    SINGLE_PLAYER = 2
    END_PAGE = 3

class Game_manager:

    def __init__(self) -> None:
        self.screen = pg.display.set_mode((800, 600))
        self.running = True
        self.current_board = Board(20, 50, "images/board.jpg", 535, 535)
        self.turn = "black"
        self.page = Game_pages.START_PAGE # page 1 for game page
        self.winner = "None"
        self.AI_turn = False

    def change_turn(self):

        if self.turn == "black":
            self.turn = "white"
        else:
            self.turn = "black"

    def add_piece_to_board(self, row, col):

        self.current_board.add_piece(row, col, self.turn) # turn is the same as color and type of a piece

        sound = mixer.Sound("Sound/sound_effect.wav")
        sound.play() # sound when a player place a piece

        if not self.current_board.is_terminal():
            self.change_turn()
        else:
            self.winner = self.turn
            self.page = Game_pages.END_PAGE # switch to end page

    def show_text(self, font:str, text: str, size: int, color: str, x: float, y: float) -> None:

        # size for font size
        font = pg.font.SysFont(font, size)
        img = font.render(text, True, color)
        self.screen.blit(img,(x, y))

    def start_page(self) -> None:
        
        self.show_text("calibri", "GOMOKU", 72, "black", 259.5, 150)
        self.show_text("calibri", "Multi Player(m)", 40, "black", 50, 450)
        self.show_text("calibri", "Single Player(s)", 40, "black", 240, 450)
        self.show_text("calibri", "Press m or s to start", 36, "black", 250, 300)


    
    def game_page(self) -> None:

        # show the board
        self.current_board.draw(self.screen)

        # show all pieces
        for row in self.current_board.board_for_display:
            for piece in row:
                if piece != None:
                    piece.draw(self.screen)
    
    def end_page(self) -> None:

        self.show_text("calibri", "{} wins".format(self.winner), 144, "black", 76, 100)
        self.show_text("calibri", "Press e to exit", 36, "black", 300, 400)


    def tick(self) -> None:

        # background color
        self.screen.fill((255, 255, 255))

        # background image
        background = pg.image.load("Images/background.png")
        background = pg.transform.scale(background, (800, 600))
        self.screen.blit(background, (0, 0))

        for event in pg.event.get():
    
            if event.type == pg.QUIT:
                pg.quit()
                exit()

            if self.page == Game_pages.START_PAGE:

                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_s:
                        #print("s")
                        self.page = Game_pages.SINGLE_PLAYER # switch page
                
                    if event.key == pg.K_m:

                        self.page = Game_pages.MULTI_PLAYER

            if self.page == Game_pages.MULTI_PLAYER or self.page == Game_pages.SINGLE_PLAYER:

                if self.page == Game_pages.SINGLE_PLAYER:
                    if self.turn == "black":
                        self.AI_turn = True
                    else:
                        self.AI_turn = False

                if event.type == MOUSEBUTTONDOWN and not self.AI_turn: # player can not move under AI's turn in single player mode
                    if event.button == 1:

                        pos = event.pos # position of press

                        row = int((pos[0] - 43 + 122/7) // (244/7))
                        col = int((pos[1] - 73 + 122/7) // (244/7))

                        if 0 <= row < 15 and 0 <= col < 15: # check if click inside the board
                            self.add_piece_to_board(row, col)

                if self.AI_turn:

                    root = Node(self.current_board.state, self.turn)

                    tree = Game_Tree(root)
                    tree.generate_game_tree(0, 3) # max depth equals 3 for now
                    tree.evaluate_game_tree()

                    action = tree.choose()

                    self.add_piece_to_board(action[0], action[1])


                    

            if self.page == Game_pages.END_PAGE:

                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_e:
                        pg.quit()
                        exit()

                

        if self.page == Game_pages.START_PAGE:

            self.start_page()
        
        elif self.page == Game_pages.MULTI_PLAYER or self.page == Game_pages.SINGLE_PLAYER:

            self.game_page()

        elif self.page == Game_pages.END_PAGE:

            self.end_page()

        pg.display.update()
