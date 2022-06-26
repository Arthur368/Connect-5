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
        
        self.cached_columns = []
        self.cached_diags = []

        self.is_terminal = False
        self.is_evaluated = False

        #self.lowerbound = 100000
        #self.upperbound = -100000
        self.eval_for_prop = 0

        if self.player == "black":
            self.eval_for_prop = -100000
        else:
            self.eval_for_prop = 100000

        self.opponent = ""
        
        if self.player == "black":
            self.opponent = "white"
        else:
            self.opponect = "black"

    def add_child(self, node):
        self.children.append(node)
    
    def set_parent(self, node):
        self.parent = node

    def evaluation(self):
        return self.score("black") - self.score("white")
    

    def score(self, player):
        value = 10 * self.num_in_a_row(2, player) + 100 * self.num_in_a_row(3, player) + 1000 * self.num_in_a_row(4, player)
        
        return value
  
    def check_terminal(self):
        if self.num_in_a_row(4, "red") > 0:
            self.is_terminal = True
            self.eval += 10000
            self.eval_for_prop = 10000
        
        if self.num_in_a_row(4, "yellow") > 0:
            self.is_terminal = True
            self.eval -= 10000
            self.eval_for_prop = -10000
    
    def num_in_a_row(self, rows: list, num: int, player: str) -> int:

        num_in_a_row = sum([len(re.findall(player[0]*num, row)) for row in rows]) 
        
        return num_in_a_row

    def Check_terminal(self):

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

        is_terminal = self.num_in_a_row(rows, 5, "black") + self.num_in_a_row(cols, 5, "black") + self.num_in_a_row(diags, 5, "black") + self.num_in_a_row(rows, 5, "white") + self.num_in_a_row(cols, 5, "white") + self.num_in_a_row(diags, 5, "white")
        
        return is_terminal > 0

class Game_Tree:

    def __init__(self, root):
        self.root = root
        self.evaluated_node_size = 0

    def generate_game_tree(self, player, current_depth, max_depth):

        if current_depth < max_depth and not self.root.is_terminal:
        
            rows = self.root.state.split(",")
            cpy_rows = deepcopy(rows)
            
            num_of_rows = len(rows)
            num_of_columns = len(rows[0])
            p = player[0]

            
            new_player = ''
            if player == "red":
                new_player = "yellow"
            else:
                new_player = "red"
        
            
            #opt_state = ''
            first_node = True

            if self.root.parent != None:
                for child in self.root.parent.children:

                    if child.state == "illegal":
                        pass
                    else:
                        if child.state == self.root.state:
                            first_node = True
                        else:
                            first_node = False
                        
                        break

            for i in range(num_of_columns):
                
                opt_state = ''

                # find a place for legal move
                for j in range(num_of_rows):
                    score = 0
                    new_state = ''
                    if cpy_rows[j][i] == ".":
                        cpy_rows[j] = cpy_rows[j][0:i] + p + cpy_rows[j][i+1:]
                        new_state = ",".join(cpy_rows)

                        #print(new_state)
                        
                        temp_node = Node(new_state, new_player)
                        score = temp_node.evaluation()


                        opt_state = new_state
                        cpy_rows = deepcopy(rows)

                        break

                if opt_state != '':

                    new_game_node = Node(opt_state, new_player)
                    self.root.add_child(new_game_node)
                    new_game_node.set_parent(self.root)                    
                    #print(new_game_node.state)

                    new_game_node.check_terminal()
                    subtree = Game_Tree(new_game_node)

                    #if not new_game_node.is_terminal:
                    subtree.generate_game_tree(new_player, current_depth + 1, max_depth)

                    if first_node and current_depth == max_depth - 1:
                        pass                      
                    else:
                        
                        if self.root.player == "red":
                            
                            if self.root.parent != None:
                                if self.root.eval_for_prop >= self.root.parent.eval_for_prop:
                                    break
                            
                                #if self.root.parent.parent != None:
                                #    if self.root.eval_for_prop <= self.root.parent.parent.eval_for_prop:
                                #        break
                        else:
                            
                            if self.root.parent != None:
                                if self.root.eval_for_prop <= self.root.parent.eval_for_prop:
                                    break

                                #if self.root.parent.parent != None:
                                #    if self.root.eval_for_prop >= self.root.parent.parent.eval_for_prop:
                                #        break          
                               
                        if max_depth == 4 and self.root.count_token("red") + self.root.count_token("yellow") == 1:
                            if self.root.eval_for_prop == -10:
                                break
                else:
                    new_game_node = Node("illegal", new_player)
                    self.root.add_child(new_game_node)
                    new_game_node.set_parent(self.root)
            """
            if self.root.state != "illegal":
                self.root.is_evaluated = True

                if self.root.parent != None:

                    if self.root.player == "red":
                        if self.root.eval_for_prop < self.root.parent.eval_for_prop:
                            self.root.parent.eval_for_prop = self.root.eval_for_prop
                    else:
                        if self.root.eval_for_prop > self.root.parent.eval_for_prop:
                            self.root.parent.eval_for_prop = self.root.eval_for_prop   
            """
            if self.root.state != "illegal":
                self.root.is_evaluated = True
                        
        
        
        elif current_depth == max_depth or self.root.is_terminal:
            
            if self.root.eval == 0 and self.root.state != "illegal":
                self.root.eval = self.root.evaluation()
                self.root.eval_for_prop = self.root.eval
                #print(self.root.evaluation())
                self.root.is_evaluated = True
                #print("T")
            elif self.root.eval == 10000 or self.root.eval == -10000:
                self.root.eval_for_prop = self.root.eval
                self.root.is_evaluated = True

            
        if self.root.state != "illegal" and self.root.parent != None:

            if self.root.player == "red":
                if self.root.eval_for_prop < self.root.parent.eval_for_prop:
                    self.root.parent.eval_for_prop = self.root.eval_for_prop
                    
                                   
            else:
                if self.root.eval_for_prop > self.root.parent.eval_for_prop:
                    self.root.parent.eval_for_prop = self.root.eval_for_prop

            """
            if self.root.parent.parent != None:
                
                if self.root.player == "red":
                    if self.root.eval_for_prop > self.root.parent.parent.eval_for_prop:
                        self.root.parent.parent.eval_for_prop = self.root.eval_for_prop

                    
                else:
                    if self.root.eval_for_prop < self.root.parent.parent.eval_for_prop:
                        self.root.parent.parent.eval_for_prop = self.root.eval_for_prop
            """
    
            #print("T")
        
            

    def choose(self):
        for child in self.root.children:
            #print(child.eval)
            if child.state != "illegal":
                #print(child.eval_for_prop)
                if child.eval_for_prop == self.root.eval_for_prop:
                    return self.root.children.index(child)
    
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
    #game_tree = Game_Tree(Node(contents, turn))

    #game_tree.generate_game_tree(turn, 0, int(max_depth))

    #action = game_tree.choose()
    
    #game_tree.evaluated_node_size += game_tree.count_evaluated_nodes()
    #return str(action) + "\n" + str(game_tree.evaluated_node_size)
    
    node = Node(contents, turn)

    return node.evaluation()

if __name__ == '__main__':
    # Example function call below, you can add your own to test the connect_four_mm function
    board = np.empty((15, 15), dtype = str)
    board[:] = "n"
    board[0][1:6] = "b"
    board[3][3:5] = "w"
    
    print(connect_four_ab(board, "black", 5))
    

    
    
