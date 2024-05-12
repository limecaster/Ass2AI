from chessboard import ChessBoard, Move
from minimax import Minimax
from agent import Agent
import tkinter as tk


import time
import psutil
import threading
import time
import json
import copy

class thread(threading.Thread): 
    def __init__(self, thread_name, thread_ID, board): 
        threading.Thread.__init__(self) 
        self.thread_name = thread_name 
        self.thread_ID = thread_ID 
        self.board = board
        # helper function to execute the threads
    def time_convert(self,sec):
        sec = int(sec)
        mins = sec // 60
        sec = sec % 60
        hours = mins // 60
        mins = mins % 60
    def run(self): 
        agent = Agent(board, 'white')
        minimax = Minimax(3, board)
        count = 1
        while not board.is_game_over():
            time.sleep(1)

            agent_move = agent.get_random_move()
            if agent_move is None:
                print("Game over! White has no more moves.")
                break
            board.make_move(agent_move)     
            print(f"Move {count}: White moves {agent_move}")
        
            #[print(move) for move in board.get_all_possible_moves('black')]
            board.boardDisplay()
            minimax_move = minimax.get_best_move_for_black()
            print(f"Move {count}: Black moves {minimax_move}")
            if minimax_move is None:
                print("Game over! Black has no more moves.")
                break
            board.make_move(minimax_move)
            board.boardDisplay()

        
            count += 1
        
            if board.is_game_over():
                if board.get_winner() == 'black':
                    print("Black wins!")
                elif board.get_winner() == 'white':
                    print("White wins!")
                else:
                    print("It's a draw!")
    
        print(minimax.get_moves_time())
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss

        execution_time = end_time - start_time
        memory_consumption = end_memory - start_memory
        
if __name__ == '__main__':
    start_time = time.time()
    start_memory = psutil.Process().memory_info().rss
    draw_game = [
        ['black_rook', '', 'black_bishop', 'black_queen', 'black_king', 'black_bishop', '', 'black_rook'],
        ['black_pawn', 'black_pawn', 'black_pawn', '', 'black_pawn', 'black_pawn', 'black_pawn', 'black_pawn'],
        ['', '', '', '', '', 'black_knight', '', ''],
        ['', '', '', '', '', '', 'white_bishop', ''],
        ['', '', 'black_pawn', '', '', '', '', ''],
        ['white_knight', '', '', '', '', 'black_knight', '', ''],
        ['white_pawn', 'white_pawn', '', '', 'white_pawn', 'white_pawn', 'white_pawn', 'white_pawn'],
        ['white_rook', '', '', 'white_queen', 'white_king', 'white_bishop', 'white_rook', ''],
        ]
    
    check_board = [
        ['black_rook', '', 'black_bishop', '', 'black_king', 'black_bishop', '', 'black_rook'],
        ['black_pawn', '', 'black_pawn', 'black_pawn', 'black_pawn', 'black_pawn', 'black_pawn', 'black_pawn'],
        ['', '', '', '', '', '', 'black_knight', ''],
        ['', '', '', '', '', '', '', ''],
        ['', 'black_knight', '', '', '', '', '', ''],
        ['white_knight', '', 'black_queen', 'white_pawn', '', '', '', 'white_pawn'],    
        ['', '', 'white_pawn', '', 'white_pawn', 'white_pawn', '', ''],
        ['white_rook', '', '', 'white_queen', 'white_king', 'white_bishop', 'white_knight', 'white_rook']
    ]
    board = ChessBoard(draw_game, "white")
    [print(mv) for mv in board.get_all_possible_moves("white")]

    thread1 = thread("GFG", 1000,board) 
    thread1.start()
    board.mainloop()
    

    