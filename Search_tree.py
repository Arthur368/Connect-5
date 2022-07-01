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
        self.bound = self.eval
    
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

    # Too much successors for a node, we only need to search places 
    def get_searchable_places(self):
        
        matrix_state = [[1 if (0 < i < 16 and 0 < j < 16 and self.state[i - 1, j - 1] != "n") else 0 for j in range(17)] for i in range(17)]

        matrix_state = np.asarray(matrix_state)

        kernal = np.ones((3, 3))
        kernal[1][1] = 10

       # check if searchable
        is_searchable = [[True if matrix_state[i+1][j+1] == 0 and matrix_state[i: i + 3, j: j + 3].sum() > 0 else False for j in range(15)] for i in range(15)]

        searchable_places = [(i, j) for i in range(15) for j in range(15) if is_searchable[i][j]]

        return searchable_places

class Game_Tree:

    def __init__(self, root: Node) -> None:
        self.root = root
        self.evaluated_node_size = 0

    def generate_game_tree(self, current_depth, max_depth):

        if self.root.is_terminal:

            if self.root.player == "black":

                # when white wins
                self.bound = -1000000
            else:
                self.bound = 1000000

            return

        if current_depth < max_depth and not self.root.is_terminal:

            searchable_places = self.root.get_searchable_places()

            state_c = deepcopy(self.root.state)
            
            if len(searchable_places) == 0:
                return
            # loop over and find all possible places for pieces
            for pos in searchable_places:


                if state_c[pos[0]][pos[1]] == "n":
                    
                    state_c[pos[0]][pos[1]] = self.root.player[0]
                    child = Node(state_c, self.root.opponent)
                    child.set_newest_pos((pos[0], pos[1])) # for return best move

                    self.root.add_child(child)
                    child.set_parent(self.root)

                    subtree = Game_Tree(child)
                    subtree.generate_game_tree(current_depth + 1, max_depth)

                    state_c[pos[0]][pos[1]] = "n" # need to change board back before next iteration.


    def evaluate_game_tree(self) -> int:

        if len(self.root.children) == 0: # leaf node, need to be evaluated
            
            self.root.evaluation()

        else:
            
            evals = []

            for child in self.root.children:

                if self.root.children.index(child) == 0: # we have to evaluate every thing for first child so we get something to compare.

                    if len(child.children) == 0:
                        
                       self.root.bound = Game_Tree(child).evaluate_game_tree()
                    
                    else:
                
                        evals_for_child = [Game_Tree(grandchild).evaluate_game_tree() for grandchild in child.children]

                        if child.player == "black":
                            
                            self.root.bound = max(evals_for_child)
                        else:   
                            
                            self.root.bound = min(evals_for_child)


                
                else:
                    # condition for pruning
                    if self.root.parent != None and ((self.root.player == "black" and self.root.parent.bound >= self.root.bound) or (self.root.player == "white" and self.root.parent.bound <= self.root.bound)):
                        break
                    
                    child_value = Game_Tree(child).evaluate_game_tree()

                    if (self.root.player == "black" and child_value > self.root.bound) or (self.root.player == "white" and child_value < self.root.bound):

                        self.root.bound = child_value

        return self.root.bound

    def choose(self):

        if len(self.root.children) == 0:

            return (7, 7)
        
        best_move = (-1, -1)
        best_value = 0.5

        for child in self.root.children:
            

            if best_value == 0.5:
               
                best_value = child.bound
                best_move = child.newest_pos
            else:
                
                if (self.root.player == "black" and child.bound > best_value) or (self.root.player == "white" and child.bound < best_value):

                    best_value = child.bound
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
    board[3][3] = "w"
    board[4][3] = "b"
    
    print(connect_four_ab(board, "black", 3))
    

    
    
