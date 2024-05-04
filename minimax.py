class Minimax:
    def __init__(self, depth, board):
        self.depth = depth
        self.board = board
        
        # If the pawn is in the center of the board, it is worth more
        # If the pawn is on the edge of the board, it is worth less
        # If the pawn is on sixth or seventh row, it is worth more cause it is closer to promotion
        self.__white_pawn_value_by_position = [
        [0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0],
        [5.0,  5.0,  5.0,  5.0,  5.0,  5.0,  5.0,  5.0],
        [1.0,  1.0,  2.0,  3.0,  3.0,  2.0,  1.0,  1.0],
        [0.5,  0.5,  1.0,  2.5,  2.5,  1.0,  0.5,  0.5],
        [0.0,  0.0,  0.0,  2.0,  2.0,  0.0,  0.0,  0.0],
        [0.5, -0.5, -1.0,  0.0,  0.0, -1.0, -0.5,  0.5],
        [0.5,  1.0,  1.0, -2.0, -2.0,  1.0,  1.0,  0.5],
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
        [ 0.5,  1.0,  1.0,  1.0,  1.0,  1.0,  1.0,  0.5],
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
        piece_color, piece_type = piece.split('_')
        value = 0
        
        if piece_type == 'pawn':
            value = 1
        elif piece_type == 'knight' or piece_type == 'bishop':
            value = 3
        elif piece_type == 'rook':
            value = 5
        elif piece_type == 'queen':
            value = 9
        elif piece_type == 'king':
            value = 100
    
        if piece_color == 'black':
            value = -value
            
        return value

    def _get_piece_value_by_position(self, piece, row, col):
        piece_color, piece_type = piece.split('_')
        value = 0
        
        if piece_type == 'pawn':
            if piece_color == 'white':
                value = self.__white_pawn_value_by_position[row][col]
            else:
                value = self.__black_pawn_value_by_position[row][col]
        elif piece_type == 'knight':
            if piece_color == 'white':
                value = self.__white_knight_value_by_position[row][col]
            else:
                value = self.__black_knight_value_by_position[row][col]
        elif piece_type == 'bishop':
            if piece_color == 'white':
                value = self.__white_bishop_value_by_position[row][col]
            else:
                value = self.__black_bishop_value_by_position[row][col]
        elif piece_type == 'rook':
            if piece_color == 'white':
                value = self.__white_rook_value_by_position[row][col]
            else:
                value = self.__black_rook_value_by_position[row][col]
        elif piece_type == 'queen':
            if piece_color == 'white':
                value = self.__white_queen_value_by_position[row][col]
            else:
                value = self.__black_queen_value_by_position[row][col]
        elif piece_type == 'king':
            if piece_color == 'white':
                value = self.__white_king_value_by_position[row][col]
            else:
                value = self.__black_king_value_by_position[row][col]
        
        return value

    def _get_piece_value(self, piece, row, col):
        return self._get_piece_value_by_type(piece) + self._get_piece_value_by_position(piece, row, col)

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
                eval = self._minimax(depth - 1, self.board.get_board(), False, alpha, beta)
                self.board.undo_move()
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in self.board.get_all_possible_moves('black'):
                self.board.make_move(move)
                eval = self._minimax(depth - 1, self.board.get_board(), True, alpha, beta)
                self.board.undo_move()
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval
        
    def get_best_move(self, is_maximizing_player: bool):
        """Returns the best move for the player with the given color.
        is_maximizing_player: True if the player is white, False if the player is black.
        """
        best_move = None
        best_eval = float('-inf') if is_maximizing_player else float('inf')
        alpha = float('-inf')
        beta = float('inf')
        
        if is_maximizing_player:
            for move in self.board.get_all_possible_moves('white'):
                self.board.make_move(move)
                eval = self._minimax(self.depth - 1, self.board.get_board(), False, alpha, beta)
                self.board.undo_move()
                if eval > best_eval:
                    best_eval = eval
                    best_move = move
        else:
            for move in self.board.get_all_possible_moves('black'):
                self.board.make_move(move)
                eval = self._minimax(self.depth - 1, self.board.get_board(), True, alpha, beta)
                self.board.undo_move()
                if eval < best_eval:
                    best_eval = eval
                    best_move = move
        
        return best_move
    
    def get_best_move_for_white(self):
        return self.get_best_move(True)
    
    def get_best_move_for_black(self):
        return self.get_best_move(False)


    