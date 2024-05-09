import random

class Agent:
    def __init__(self, board, player:str = 'black'):
        self.player = player
        self.board = board
        self.log_moves = []
    
    def get_player(self):
        return self.player
    
    def get_random_move(self):
        move_list = self.board.get_all_possible_moves(self.player)
        return random.choice(move_list)
    
    
    