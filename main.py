from chessboard import ChessBoard, Move
from minimax import Minimax
from agent import Agent

import time
import psutil

if __name__ == '__main__':
    start_time = time.time()
    start_memory = psutil.Process().memory_info().rss
    game = [
        ['black_rook', '', '', '', 'black_king', '', '', 'black_rook'],
        ['black_pawn', 'black_pawn', 'black_pawn', '', '', 'black_pawn','black_pawn', 'black_pawn'],
        ['', '', '', '', 'black_pawn', 'black_knight', '', ''],
        ['', 'black_knight', '', 'black_pawn', '', 'black_bishop', '', ''],
        ['', '', '', '', '', 'white_pawn', 'white_pawn', ''], 
        ['', '', 'black_queen', 'white_pawn', '', '', '', 'white_pawn'],
        ['white_pawn', '', '', 'white_king', 'white_pawn', '', '', 'white_rook'],
        ['white_rook', '', '', '', '', 'white_bishop', 'white_knight', '']
        ]
    board = ChessBoard(game, 'white')    
    agent = Agent(board, 'white')
    minimax = Minimax(3, board)
    for i in range(20):
        [print(move) for move in board.get_all_possible_moves('white')]
        agent_move = agent.get_random_move()
        board.make_move(agent_move)
        print(i, agent_move)
        minimax_move, total_minimax_move = minimax.get_best_move_for_black()
        board.make_move(minimax_move)
        print(i, minimax_move, total_minimax_move)
    end_time = time.time()
    end_memory = psutil.Process().memory_info().rss

    execution_time = end_time - start_time
    memory_consumption = end_memory - start_memory