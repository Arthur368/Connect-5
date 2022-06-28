from copy import deepcopy
import numpy as np
import re

class Node:
    def __init__(self, state: np.array, player: str) -> None:
        self.state = state
        self.player = player 
        self.eval = 0
        
        self.parent = None
        self.children = []
        
        #self.is_terminal = False
        self.is_evaluated = False
              
        self.eval_for_prop = 0

        if self.player == "black":
            self.eval_for_prop = -100000
        else:
            self.eval_for_prop = 100000

        self.bound = 0

        self.opponent = ""
        
        if self.player == "black":
            self.opponent = "white"
        else:
            self.opponent = "black"

        self.rows = ["".join(row) for row in self.state] # get rows

        state_T = self.state.transpose()
        self.cols = ["".join(col) for col in state_T] # get cols

        """
        seems there is a little bit weird about which one is row and which one is col
        """
        #print(rows)

        self.diags = ["".join(self.state.diagonal(i)) for i in range(-14, 15)]

        state_filped = np.fliplr(self.state)

        self.diags.extend(["".join(state_filped.diagonal(i)) for i in range(-14, 15)])
    
        self.is_terminal = self.Check_terminal()

        self.newest_pos = (-1, -1) # denote the newest move
    
    def add_child(self, node) -> None:
        self.children.append(node)
    
    def set_parent(self, node) -> None:
        self.parent = node

    def set_newest_pos(self, pos: tuple) -> None:
        self.newest_pos = pos

    def evaluation(self) -> None:

        self.eval = self.score("black") - self.score("white")
    

    def score(self, player: str) -> int:

        p = player[0]

        if player == "black":
            o = "w" # o for opponent
        else:
            o = "b" 

        value = 10000* self.detect_pattern(p*5) + 8000*self.detect_pattern("n{}n".format(p*4))
        value += 4000* (self.detect_pattern("{}{}n".format(o, p*4)) + self.detect_pattern("n{}{}".format(p*4, o)))  
        value += 4000* sum([self.detect_pattern("{}n{}".format(p*i, p*(4 - i))) for i in range(1, 4)])
        value += 4000* (self.detect_pattern("n{}$".format(p*4)) + self.detect_pattern("^{}n".format(p*4)))
        value += 2500* self.detect_pattern("n{}n".format(p*3))
        value += 1000* sum([self.detect_pattern("n{}n{}n".format(p*i, p*(3 - i))) for i in range(1, 3)])
        value += 100 * (self.detect_pattern("nn{}n".format(p*2)) + self.detect_pattern("n{}nn".format(p*2)))        
        value += sum([self.detect_pattern("{}{}{}".format("n"*i, p, "n"*(4 - i))) for i in range(1, 4)])
        
        return value
   
    # find patterns for the whole board by reuse
    def detect_pattern(self, pattern: str) -> int:

        return self.num_in_a_row(self.rows, pattern) + self.num_in_a_row(self.cols, pattern) + self.num_in_a_row(self.diags, pattern)

    # find patterns for rows
    def num_in_a_row(self, rows: list, pattern: str) -> int:

        num_in_a_row = sum([len(re.findall(pattern, row)) for row in rows]) 
        
        return num_in_a_row

    def Check_terminal(self):

        five_in_a_row = self.detect_pattern("b"*5) + self.detect_pattern("w"*5)
        
        return five_in_a_row > 0

class Game_Tree:

    def __init__(self, root) -> None:
        self.root = root
        self.evaluated_node_size = 0

    def generate_game_tree(self, current_depth, max_depth):

        if current_depth < max_depth and not self.root.is_terminal:

            state = deepcopy(self.root.state)

            # loop over and find all possible places for pieces.
            for i in range(len(state)):

                for j in range(len(state[0])):

                    if state[i][j] == "n":
                        
                        #print(self.root.opponent)
                        state[i][j] = self.root.player[0]
                        child = Node(state, self.root.opponent)
                        #print(child.opponent == "")
                        child.set_newest_pos((i, j)) # for return best move

                        self.root.add_child(child)
                        child.set_parent(self.root)

                        subtree = Game_Tree(child)
                        subtree.generate_game_tree(current_depth + 1, max_depth)

                        state[i][j] = "n" # need to change board back before next iteration.


    def evaluate_game_tree(self) -> int:

        if len(self.root.children) == 0: # leaf node, need to be evaluated
            
            self.root.evaluation()

        else:
            
            evals = []

            for child in self.root.children:

                if self.root.children.index(child) == 0: # we have to evaluate every thing for first child so we get something to compare.

                    if len(child.children) == 0:
                        
                        evals.append(Game_Tree(child).evaluate_game_tree())
                    
                    else:
                
                        evals_for_child = [Game_Tree(grandchild).evaluate_game_tree() for grandchild in child.children]

                        if child.player == "black":
                            
                            evals.append(max(evals_for_child))

                        else:   
                            
                            evals.append(min(evals_for_child))

                     # keep bounds not exact values for the sake of pruning.

                    self.root.bound = evals[0]
                
                else:
                    # condition for pruning
                    if self.root.parent != None and ((self.root.player == "black" and self.root.parent.bound <= self.root.bound) or (self.root.player == "white" and self.root.parent.bound >= self.root.bound)):
                        break
                    
                    child_value = Game_Tree(child).evaluate_game_tree()

                    evals.append(Game_Tree(child).evaluate_game_tree())
                    
            if self.root.player == "black":
                self.root.eval = max(evals)
            else:
                self.root.eval = min(evals)

        return self.root.eval

    def choose(self):
        
        best_move = (-1, -1)
        best_value = 0.5

        for child in self.root.children:
            
            if best_value == 0.5:
               
                best_value = child.eval
                best_move = child.newest_pos
            else:
                
                if (self.root.player == "black" and child.eval > best_value) or (self.root.player == "white" and child.eval < best_value):

                    best_value = child.eval
                    best_move = child.newest_pos

        return best_move

    
    def count_evaluated_nodes(self):

        #print(self.root.is_evaluated)
        if len(self.root.children) == 0:
            if self.root.is_evaluated:
                #self.evaluated_node_size += 1
                #print("HI")
                return 1
            else:
                return 0
        else:
            cumulated_size = 0
            for child in self.root.children:
                subtree = Game_Tree(child)
                cumulated_size += subtree.count_evaluated_nodes()
                
            #print(cumulated_size)
            if self.root.is_evaluated:
                return 1 + cumulated_size
            else:
                return cumulated_size



  
def connect_four_ab(contents, turn, max_depth):
    game_tree = Game_Tree(Node(contents, turn))

    game_tree.generate_game_tree(0, int(max_depth))

    game_tree.evaluate_game_tree()

    action = game_tree.choose()
    
    #game_tree.evaluated_node_size += game_tree.count_evaluated_nodes()
    #return str(action) + "\n" + str(game_tree.evaluated_node_size)
    
    node = Node(contents, turn)

    #print(node.rows)

    return action

if __name__ == '__main__':
    # Example function call below, you can add your own to test the connect_four_mm function
    board = np.empty((15, 15), dtype = str)
    board[:] = "n"
    #board[0][1:6] = "b"
    #board[3][3:5] = "w"
    
    print(connect_four_ab(board, "black", 2))
    

    
    