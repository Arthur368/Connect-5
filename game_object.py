import imp
from multiprocessing import Condition
from typing import Optional
from xmlrpc.client import Boolean
import pygame as pg
from pygame.locals import *
from pygame import mixer
import numpy as np
import re

class Game_object:

    def __init__(self, x : int, y : int, image_path: str, length: int, width: int) -> None:

        self.x = x
        self.y = y
        self.image_path = image_path
        self.length = length
        self.width = width
        self.image = pg.image.load(image_path)
        self.image = pg.transform.scale(self.image, (self.length, self.width))
        
    def draw(self, screen: pg.surface) -> None:

        screen.blit(self.image, (self.x, self.y))

class Board(Game_object):

    def __init__(self, x: int, y: int, image_path: str, length: int, width: int) -> None:
        super().__init__(x, y, image_path, length, width)
        self.board_for_display = np.empty((15, 15), dtype=Piece)
        self.state = np.empty((15, 15), dtype=str)
        self.state[:] = "n"

    # add a piece with a color(black or white into a board), only when there is a position
    def add_piece(self, row: int, col: int, color: str) -> None:
        
        # color for the type of piece

        if self.board_for_display[row][col] == None:

            self.board_for_display[row][col] = Piece(43 + (row - 1/2)*(244/7), 73 + (col - 1/2)*(244/7), "Images/{}_piece.png".format(color), 244/7, 244/7, color)
            self.state[row][col] = color[0]

    def is_five_in_a_row(self, rows: list) -> Boolean:

        num_of_five_in_a_row = sum([len(re.findall("b"*5, row)) for row in rows]) + sum([len(re.findall("w"*5, row)) for row in rows])

        if num_of_five_in_a_row > 0:
            return True
        else:
            return False

    def is_terminal(self) -> Boolean:

        rows = ["".join(row) for row in self.state] # get rows

        state_T = self.state.transpose()
        cols = ["".join(col) for col in state_T] # get cols

        """
        seems there is a little bit weird about which one is row and which one is col
        """
        #print(rows)

        diags = ["".join(self.state.diagonal(i)) for i in range(-14, 15)]

        state_filped = np.fliplr(self.state)

        diags.extend(["".join(state_filped.diagonal(i)) for i in range(-14, 15)])

        is_terminal = self.is_five_in_a_row(rows) or self.is_five_in_a_row(cols) or self.is_five_in_a_row(diags)

        return is_terminal




class Piece(Game_object):

    def __init__(self, x: int, y: int, image_path: str, length: int, width: int, piece_type: str) -> None:
        super().__init__(x, y, image_path, length, width)
        self.piece_type = piece_type
