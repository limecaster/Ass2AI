from chessboard import ChessBoard, Move
from minimax import Minimax
from agent import Agent

import time
import psutil

if __name__ == '__main__':
    start_time = time.time()
    start_memory = psutil.Process().memory_info().rss
    draw_game = [
        ['', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', ''],
        ['', '', '', '', '', 'white_king', 'white_queen', ''],
        ['', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', 'black_king']
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
    board = ChessBoard(check_board, 'white')

    agent = Agent(board, 'white')
    minimax = Minimax(3, board)
    count = 1
    while not board.is_game_over():
        agent_move = agent.get_random_move()
        if agent_move is None:
            print("Game over! White has no more moves.")
            break
        board.make_move(agent_move)     
        print(f"Move {count}: White moves {agent_move}")
        
        #[print(move) for move in board.get_all_possible_moves('black')]
        minimax_move = minimax.get_best_move_for_black()
        print(f"Move {count}: Black moves {minimax_move}")
        if minimax_move is None:
            print("Game over! Black has no more moves.")
            break
        board.make_move(minimax_move)
        
        count += 1
        
    if board.is_game_over():
        if board.get_winner() == 'black':
            print("Black wins!")
        elif board.get_winner() == 'white':
            print("White wins!")
        else:
            print("It's a draw!")
    end_time = time.time()
    end_memory = psutil.Process().memory_info().rss

    execution_time = end_time - start_time
    memory_consumption = end_memory - start_memory

    