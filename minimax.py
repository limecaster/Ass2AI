from chessboard import ChessBoard, Move
import time
import psutil

class Minimax:
    def __init__(self, depth, board):
        self.depth = depth
        self.board = board
        self.best_move = None
        # If the pawn is in the center of the board, it is worth more
        # If the pawn is on the edge of the board, it is worth less
        # If the pawn is on sixth or seventh row, it is worth more cause it is closer to promotion
        self.__white_pawn_value_by_position = [
        [0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0],
        [5.0,  5.0,  5.0,  5.0,  5.0,  5.0,  5.0,  5.0],
        [1.0,  1.0,  2.0,  3.0,  3.0,  2.0,  1.0,  1.0],
        [0.5,  0.5,  1.0,  2.5,  2.5,  1.0,  0.5,  0.5],
        [0.0,  0.0,  0.0,  2.0,  2.0,  0.0,  0.0,  0.0],
        [0.5,  0.5,  1.0,  0.0,  0.0,  1.0,  0.5,  0.5],
        [0.5,  1.0,  0.5, -1.0, -1.0,  0.5,  1.0,  0.5],
        [0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0]
    ]
        # Reverse the board to get the black pawn value by position
        self.__black_pawn_value_by_position = self.__white_pawn_value_by_position[::-1]
        
        # If the knight is in the center of the board, it is worth more cause it can move to more squares
        # If the knight is on the edge of the board, it is worth less cause it can move to less squares
        self.__white_knight_value_by_position = self.__black_knight_value_by_position = [
        [-5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0],
        [-4.0, -2.0,  0.0,  0.0,  0.0,  0.0, -2.0, -4.0],
        [-3.0,  0.0,  1.0,  1.5,  1.5,  1.0,  0.0, -3.0],
        [-3.0,  0.5,  1.5,  2.0,  2.0,  1.5,  0.5, -3.0],
        [-3.0,  0.0,  1.5,  2.0,  2.0,  1.5,  0.0, -3.0],
        [-3.0,  0.5,  1.0,  1.5,  1.5,  1.0,  0.5, -3.0],
        [-4.0, -2.0,  0.0,  0.5,  0.5,  0.0, -2.0, -4.0],
        [-5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0]
    ]
        
        # If the bishop is on main diagonals, it is worth more cause it can move to more squares
        # But if the bishop is in the corner, it is worth less cause it only moves to 7 squares 
        #                                      and cannot move to the other diagonals        
        self.__white_bishop_value_by_position = [
        [-2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0],
        [-1.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -1.0],
        [-1.0,  0.0,  0.5,  1.0,  1.0,  0.5,  0.0, -1.0],
        [-1.0,  0.5,  0.5,  1.0,  1.0,  0.5,  0.5, -1.0],
        [-1.0,  0.0,  1.0,  1.0,  1.0,  1.0,  0.0, -1.0],
        [-1.0,  1.0,  1.0,  1.0,  1.0,  1.0,  1.0, -1.0],
        [-1.0,  0.5,  0.0,  0.0,  0.0,  0.0,  0.5, -1.0],
        [-2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0]
    ]
        # Reverse the board to get the black bishop value by position
        self.__black_bishop_value_by_position = self.__white_bishop_value_by_position[::-1]
        
        # If the rook is on the edge of the board, it is worth less cause it can move to less squares
        # If the rook is on the seventh row, it is worth more cause it controls the seventh row, 
        #                               which makes it harder for the opponent's king to move to the center
        # If the rook is on d1 or e1, it is worth more cause it was already developed, and it can control the center
        self.__white_rook_value_by_position = [
        [ 0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0],
        [ 1.0,  1.0,  1.0,  1.0,  1.0,  1.0,  1.0,  1.0],
        [-0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5],
        [-0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5],
        [-0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5],
        [-0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5],
        [-0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5],
        [ 0.0,  0.0,  0.0,  0.5,  0.5,  0.0,  0.0,  0.0]
    ]
        # Reverse the board to get the black rook value by position
        self.__black_rook_value_by_position = self.__white_rook_value_by_position[::-1]
        
        self.__white_queen_value_by_position = self.__black_queen_value_by_position = [
        [-2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0],
        [-1.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -1.0],
        [-1.0,  0.0,  0.5,  0.5,  0.5,  0.5,  0.0, -1.0],
        [-0.5,  0.0,  0.5,  0.5,  0.5,  0.5,  0.0, -0.5],
        [ 0.0,  0.0,  0.5,  0.5,  0.5,  0.5,  0.0, -0.5],
        [-1.0,  0.5,  0.5,  0.5,  0.5,  0.5,  0.0, -1.0],
        [-1.0,  0.0,  0.5,  0.0,  0.0,  0.0,  0.0, -1.0],
        [-2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0]
    ]
        
        self.__white_king_value_by_position = [
        [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
        [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
        [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
        [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
        [-2.0, -3.0, -3.0, -4.0, -4.0, -3.0, -3.0, -2.0],
        [-1.0, -2.0, -2.0, -2.0, -2.0, -2.0, -2.0, -1.0],
        [ 2.0,  2.0,  0.0,  0.0,  0.0,  0.0,  2.0,  2.0 ],
        [ 2.0,  3.0,  1.0,  0.0,  0.0,  1.0,  3.0,  2.0 ]
    ]
        # Reverse the board to get the black king value by position
        self.__black_king_value_by_position = self.__white_king_value_by_position[::-1]
        
    def _get_piece_value_by_type(self, piece):
        _, piece_type = piece.split('_')
        
        if piece_type == 'pawn':
            return 10
        elif piece_type == 'knight' or piece_type == 'bishop':
            return 30
        elif piece_type == 'rook':
            return 50
        elif piece_type == 'queen':
            return 90
        elif piece_type == 'king':
            return 1000
       
    def _get_piece_value_by_position(self, piece, row, col):
        piece_color, piece_type = piece.split('_')
        
        
        if piece_type == 'pawn':
            if piece_color == 'white':
                return self.__white_pawn_value_by_position[col][row]
            else:
                return self.__black_pawn_value_by_position[col][row]
        elif piece_type == 'knight':
            if piece_color == 'white':
                return self.__white_knight_value_by_position[col][row]
            else:
                return self.__black_knight_value_by_position[col][row]
        elif piece_type == 'bishop':
            if piece_color == 'white':
                return self.__white_bishop_value_by_position[col][row]
            else:
                return self.__black_bishop_value_by_position[col][row]
        elif piece_type == 'rook':
            if piece_color == 'white':
                return self.__white_rook_value_by_position[col][row]
            else:
                return self.__black_rook_value_by_position[col][row]
        elif piece_type == 'queen':
            if piece_color == 'white':
                return self.__white_queen_value_by_position[col][row]
            else:
                return self.__black_queen_value_by_position[col][row]
        elif piece_type == 'king':
            if piece_color == 'white':
                return self.__white_king_value_by_position[col][row]
            else:
                return self.__black_king_value_by_position[col][row]
        return 0

    def _get_piece_value(self, piece, row, col):
        total_value = self._get_piece_value_by_type(piece) + self._get_piece_value_by_position(piece, row, col)
        piece_color, _ = piece.split('_')
        return total_value if piece_color == 'white' else -total_value

    def _evaluate_board(self, chess_board):
        total_score = 0
        for row in range(8):
            for col in range(8):
                piece = chess_board[row][col]
                if piece != '':
                    total_score += self._get_piece_value(piece, row, col)
        return total_score
    
    def _minimax(self, depth, chess_board, is_maximizing_player, alpha, beta):
        if depth == 0:
            return self._evaluate_board(chess_board)
        if is_maximizing_player:
            max_eval = float('-inf')
            for move in self.board.get_all_possible_moves('white'):
                self.board.make_move(move)
                eval = self._minimax(depth - 1, chess_board, False, alpha, beta)
                self.board.undo_move()
                if eval > max_eval:
                    max_eval = eval
                    self.best_move = move
                alpha = max(alpha, eval)
                if beta <= alpha:
                    self.best_move = move
                    return max_eval
            return max_eval
        else:
            min_eval = float('inf')
            for move in self.board.get_all_possible_moves('black'):
                self.board.make_move(move)
                eval = self._minimax(depth - 1, chess_board, True, alpha, beta)
                self.board.undo_move()
                if eval < min_eval:
                    min_eval = eval
                    self.best_move = move
                beta = min(beta, eval)
                if beta <= alpha:
                    self.best_move = move
                    return min_eval
            return min_eval
        
    # def get_best_move(self, is_maximizing_player: bool):
    #     """Returns the best move for the player with the given color.
    #     is_maximizing_player: True if the player is white, False if the player is black.
    #     """
    #     best_move = None
    #     best_eval = float('-inf') if is_maximizing_player else float('inf')
    #     alpha = float('-inf')
    #     beta = float('inf')
    #     number_possible_moves = len(self.board.get_all_possible_moves('white')) if is_maximizing_player else len(self.board.get_all_possible_moves('black'))
    #     print(f'Number of Possible moves for {"white" if is_maximizing_player else "black"}: {number_possible_moves}')
    #     if is_maximizing_player:
    #         for move in self.board.get_all_possible_moves('white'):
    #             self.board.make_move(move)
    #             eval = self._minimax(self.depth - 1, self.board.get_board()[0], False, alpha, beta)
    #             self.board.undo_move()
    #             if eval > best_eval:
    #                 best_eval = eval
    #                 best_move = move
    #     else:
    #         for move in self.board.get_all_possible_moves('black'):
    #             self.board.make_move(move)
    #             eval = self._minimax(self.depth - 1, self.board.get_board()[0], True, alpha, beta)
    #             self.board.undo_move()
    #             if eval < best_eval:
    #                 best_eval = eval
    #                 best_move = move
        
    #     return best_move, number_possible_moves
    
    def get_best_move(self, is_maximizing_player: bool):
        """Returns the best move for the player with the given color.
        is_maximizing_player: True if the player is white, False if the player is black.
        """
        self._minimax(self.depth, self.board.get_board()[0], is_maximizing_player, float('-inf'), float('inf'))
        return self.best_move
    
    def get_best_move_for_white(self):
        return self.get_best_move(True)
    
    def get_best_move_for_black(self):
        return self.get_best_move(False)


if __name__ == '__main__':
    start_time = time.time()
    start_memory = psutil.Process().memory_info().rss

    board = ChessBoard()    
    minimax = Minimax(3, board)
    
    for i in range(20):
        white_calculation_start = time.time()
        white_move, white_eval = minimax.get_best_move_for_white()
        white_calculation_end = time.time()
        board.make_move(white_move)
        print(i, white_move, white_eval)
        print(f'White move calculation time: {white_calculation_end - white_calculation_start} seconds')
        
        [print(move) for move in board.get_all_possible_moves('black')]
        black_calculation_start = time.time()
        black_move, black_eval = minimax.get_best_move_for_black()
        black_calculation_end = time.time()
        board.make_move(black_move)
        print(i, black_move, black_eval)
        print(f'Black move calculation time: {black_calculation_end - black_calculation_start} seconds')
        
    end_time = time.time()
    end_memory = psutil.Process().memory_info().rss

    execution_time = end_time - start_time
    memory_consumption = (end_memory - start_memory) / 1024 / 1024

    print(f"Execution time: {execution_time} seconds")
    print(f"Memory consumption: {memory_consumption} MB")