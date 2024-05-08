import tkinter as tk
from PIL import Image, ImageTk
import copy
class Move():
    def __init__(self, position, newPos, unitType, special_move = "", promoted = "") -> None:
        self.position = position
        self.unit_type = unitType
        self.new_pos = newPos
        self.side = ""
        if unitType.find('black')>=0:
            self.side = 'black'
        else:
            self.side = 'white'
        self.special_move = special_move
        self.promoted = promoted
    def __str__(self) -> str:
        return self.unit_type + ': ' +str(self.position) + "->" +  str(self.new_pos) + " - " + self.special_move + " - " + self.promoted
class ChessBoard(tk.Tk):
    def __init__(self, current_board=None, current_player='white', move_log=[]):
        super().__init__()
        self.rows = 8
        self.columns = 8
        self.size = 64
        
        self.title("Chess game")  
        self.canvas = tk.Canvas(self, width=self.columns*self.size, height=self.rows*self.size)
        self.canvas.pack(fill="both", expand=True)
        self.draw_board()


        self.current_board = current_board
        self.blackCastled = False
        self.whiteCastled = False
        self.piece_images = self.load_piece_images()
        self.draw_pieces()
        self.previous_board = []
        self.drag_data = {"piece": None, "x": 0, "y": 0}
        self.canvas.bind("<Button-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.drag)
        self.canvas.bind("<ButtonRelease-1>", self.drop)
        
        self.current_player = current_player
        self.move_log = move_log
        

    def draw_board(self):
        color = ["#EBECD0", "#739552"]
        for row in range(self.rows):
            for col in range(self.columns):
                color_index = (row + col) % 2
                x1 = col * self.size
                y1 = row * self.size
                x2 = x1 + self.size
                y2 = y1 + self.size
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color[color_index])

    def load_piece_images(self):
        pieces = {}
        for piece_name in ['king', 'queen', 'rook', 'bishop', 'knight', 'pawn']:
            pieces['white_' + piece_name] = self.load_png_image('images/white_' + piece_name + '.png', 60, 60)
            pieces['black_' + piece_name] = self.load_png_image('images/black_' + piece_name + '.png', 60, 60)
        return pieces
    
    def load_png_image(self, filename, width, height):
        try:
            original_image = Image.open(filename)
            aspect_ratio = original_image.width / original_image.height
            new_width = width
            new_height = int(width / aspect_ratio)
            if new_height > height:
                new_height = height
                new_width = int(height * aspect_ratio)
            resized_image = original_image.resize((new_width, new_height), Image.LANCZOS)
            rgba_image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            x_offset = (width - resized_image.width) // 2
            y_offset = (height - resized_image.height) // 2
            rgba_image.paste(resized_image, (x_offset, y_offset))
            return ImageTk.PhotoImage(rgba_image)
        except Exception as e:
            print(f"Error loading image: {e}")

    def draw_pieces(self):
        starting_board = [
            ['black_rook', 'black_knight', 'black_bishop', 'black_queen', 'black_king', 'black_bishop', 'black_knight', 'black_rook'],
            ['black_pawn'] * 8,
            [''] * 8,
            [''] * 8,
            [''] * 8,
            [''] * 8,
            ['white_pawn'] * 8,
            ['white_rook', 'white_knight', 'white_bishop', 'white_queen', 'white_king', 'white_bishop', 'white_knight', 'white_rook']
        ]
        if self.current_board is None:
            self.current_board = starting_board
        for row in range(self.rows):
            for col in range(self.columns):
                piece = starting_board[row][col]
                if piece != '':
                    piece_image = self.piece_images[piece]
                    self.canvas.create_image(col * self.size + self.size/2, row * self.size + self.size/2,
                                             image=piece_image, tags=(piece, "piece"))
    
    def start_drag(self, event):
        x, y = event.x, event.y
        overlapping = self.canvas.find_overlapping(x, y, x, y)
        if overlapping:
            tags = self.canvas.gettags(overlapping[-1])
            print(tags)
            if "piece" in tags:
                self.drag_data["piece"] = overlapping[-1]
                self.drag_data["x"] = x
                self.drag_data["y"] = y
    
    def drag(self, event):
        if self.drag_data["piece"]:
            dx = event.x - self.drag_data["x"]
            dy = event.y - self.drag_data["y"]
            self.canvas.move(self.drag_data["piece"], dx, dy)
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y
    
    def drop(self, event):
        if self.drag_data["piece"]:
            x, y = event.x, event.y
            square_size = self.size
            #col * self.size + self.size/2, row * self.size + self.size/2,
            row = (y) // square_size
            col = (x) // square_size
            print(row,col)
            new_x = col * square_size + square_size / 2
            new_y = row * square_size + square_size / 2
            self.canvas.coords(self.drag_data["piece"], new_x , new_y)
            self.drag_data["piece"] = None
    def translate_algebraic_notation(self, notation):
        notation = notation.strip().replace(" ", "").replace("\n", "")
        if len(notation) < 2 or len(notation) > 4:
            print("Invalid notation length.")
            return None
        start_square = notation[:2]
        end_square = notation[2:]
        start_col = ord(start_square[0]) - ord('a')
        start_row = 8 - int(start_square[1])
        end_col = ord(end_square[0]) - ord('a')
        end_row = 8 - int(end_square[1])
        return start_row, start_col, end_row, end_col

    def make_move_from_algebraic_notation(self, notation):
        """Make a move on the board using algebraic notation (e.g. e2e4)."""
        move = self.translate_algebraic_notation(notation)
        if move:
            start_row, start_col, end_row, end_col = move
            piece = self.get_piece_at_position(start_row, start_col)
            if piece and self.is_valid_move(piece, start_row, start_col, end_row, end_col):
                self.board.delete(self.get_piece_at_position(end_row, end_col))  # Remove the captured piece
                self.board.move(piece, (end_col - start_col) * 50, (end_row - start_row) * 50)

    def get_piece_at_position(self, row, col):
        overlapping = self.board.find_overlapping(col * 50, row * 50, col * 50, row * 50)
        if overlapping:
            for item in overlapping:
                tags = self.board.gettags(item)
                if "piece" in tags:
                    return item
        return None
    def get_board(self):
        return (copy.deepcopy(self.current_board),self.blackCastled, self.whiteCastled)
    def get_all_impact(self):
        impactPos = ([],[]) #[0] is for black, [1] is for white (not racist)
        for i in range(8):
            for j in range(8):
                if self.current_board[i][j].find("black_pawn") == 0:
                    if i + 1 < 8 and self.current_board[i+1][j] == "":
                        impactPos[0].append((i+1,j))
                        if i == 1 and i + 2 < 8 and self.current_board[i+2][j] == "":
                            impactPos[0].append((i+2,j))
                    if i + 1 < 8 and j + 1 < 8 and self.current_board[i+1][j+1].find("white") == 0:
                            impactPos[0].append((i+1,j+1))
                    if i + 1 < 8 and j - 1 >= 0 and self.current_board[i+1][j-1].find("white") == 0:
                            impactPos[0].append((i+1,j-1))
                        

                elif self.current_board[i][j].find("black_rook") == 0:
                    k = 1
                    while j + k < 8:
                        if self.current_board[i][j+k] == "":
                            impactPos[0].append((i,j + k))
                        else:
                            if self.current_board[i][j+k].find("white")==0:
                                impactPos[0].append((i,j + k))
                            break
                        k+=1
                    k = 1
                    while i + k < 8:
                        if self.current_board[i+k][j] == "":
                            impactPos[0].append((i+k,j))
                        else:
                            if self.current_board[i+k][j].find("white")==0:
                                impactPos[0].append((i+k,j))
                            break
                        k+=1
                    k = 1
                    while i - k >= 0:
                        if self.current_board[i-k][j] == "":
                            impactPos[0].append((i-k,j))
                        else:
                            if self.current_board[i-k][j].find("white")==0:
                                impactPos[0].append((i-k,j))
                            break
                        k+=1
                    k = 1
                    while j - k >= 0:
                        if self.current_board[i][j-k] == "":
                            impactPos[0].append((i,j-k))
                        else:
                            if self.current_board[i][j-k].find("white")==0:
                                impactPos[0].append((i,j-k))
                            break
                        k+=1
                elif self.current_board[i][j].find("black_knight") == 0:
                    moves = [(-1,-2), (-1,2), (1,-2), (1,2), (-2,-1), (-2,1), (2,-1), (2,1)]
                    moves = list(filter(lambda x: i + x[0] in list(range(0,8))  and j + x[1] in list(range(0,8)),moves))
                    for m in moves:
                        if self.current_board[i + m[0]][j + m[1]] == "" or self.current_board[i + m[0]][j + m[1]].find("white")==0:
                            impactPos[0].append((i+m[0],j+m[1]))
                elif self.current_board[i][j].find("black_bishop") == 0:
                    k = 1
                    while i + k < 8 and j + k <8:
                        if self.current_board[i+k][j+k] == "":
                            impactPos[0].append((i+k,j+k))
                        else:
                            if self.current_board[i+k][j+k].find("white")==0:
                                impactPos[0].append((i+k,j+k))
                            break
                        k+=1

                    k = 1
                    while i - k >= 0  and j + k <8:
                        if self.current_board[i-k][j+k] == "":
                            impactPos[0].append((i-k,j+k))
                        else:
                            if self.current_board[i-k][j+k].find("white")==0:
                                impactPos[0].append((i-k,j+k))
                            break
                        k+=1
                    k = 1
                    while i + k < 8 and j - k >=0 :
                        if self.current_board[i+k][j-k] == "":
                            impactPos[0].append((i+k,j-k))
                        else:
                            if self.current_board[i+k][j-k].find("white")==0:
                                impactPos[0].append((i+k,j-k))
                            break
                        k+=1
                    k = 1
                    while i - k >= 0 and j - k >=0:
                        if self.current_board[i-k][j-k] == "":
                            impactPos[0].append((i-k,j-k))
                        else:
                            if self.current_board[i-k][j-k].find("white")==0:
                                impactPos[0].append((i-k,j-k))
                            break
                        k+=1
                elif self.current_board[i][j].find("black_queen") == 0:
                    k = 1
                    while j + k < 8:
                        if self.current_board[i][j+k] == "":
                            impactPos[0].append((i,j + k))
                        else:
                            if self.current_board[i][j+k].find("white")==0:
                                impactPos[0].append((i,j + k))
                            break
                        k+=1
                    k = 1
                    while i + k < 8:
                        if self.current_board[i+k][j] == "":
                            impactPos[0].append((i+k,j))
                        else:
                            if self.current_board[i+k][j].find("white")==0:
                                impactPos[0].append((i+k,j))
                            break
                        k+=1
                    k = 1
                    while i - k >= 0:
                        if self.current_board[i-k][j] == "":
                            impactPos[0].append((i-k,j))
                        else:
                            if self.current_board[i-k][j].find("white")==0:
                                impactPos[0].append((i-k,j))
                            break
                        k+=1
                    k = 1
                    while j - k >= 0:
                        if self.current_board[i][j-k] == "":
                            impactPos[0].append((i,j-k))
                        else:
                            if self.current_board[i][j-k].find("white")==0:
                                impactPos[0].append((i,j-k))
                            break
                        k+=1
                    k = 1
                    while i + k < 8 and j + k <8:
                        if self.current_board[i+k][j+k] == "":
                            impactPos[0].append((i+k,j+k))
                        else:
                            if self.current_board[i+k][j+k].find("white")==0:
                                impactPos[0].append((i+k,j+k))
                            break
                        k+=1

                    k = 1
                    while i - k >= 0  and j + k <8:
                        if self.current_board[i-k][j+k] == "":
                            impactPos[0].append((i-k,j+k))
                        else:
                            if self.current_board[i-k][j+k].find("white")==0:
                                impactPos[0].append((i-k,j+k))
                            break
                        k+=1
                    k = 1
                    while i + k < 8 and j - k >=0 :
                        if self.current_board[i+k][j-k] == "":
                            impactPos[0].append((i+k,j-k))
                        else:
                            if self.current_board[i+k][j-k].find("white")==0:
                                impactPos[0].append((i+k,j-k))
                            break
                        k+=1
                    k = 1
                    while i - k >= 0 and j - k >=0:
                        if self.current_board[i-k][j-k] == "":
                            impactPos[0].append((i-k,j-k))
                        else:
                            if self.current_board[i-k][j-k].find("white")==0:
                                impactPos[0].append((i-k,j-k))
                            break
                        k+=1
                elif self.current_board[i][j].find("black_king") == 0:
                    moves = [(1,0), (-1,0), (0,1), (0,-1), (1,1), (-1,-1), (1,-1), (-1,1)]
                    # moves = list(filter(lambda x: (originalPos[0] + x[0] in list(range(0,8)))  and (originalPos[1] + x[1] in list(range(0,8))) ))
                    moves = list(filter(lambda x: i + x[0] in list(range(0,8))  and j + x[1] in list(range(0,8)),moves))
                    for m in moves:
                        if self.current_board[i + m[0]][j + m[1]] == "" or self.current_board[i + m[0]][j + m[1]].find("white")==0:
                            impactPos[0].append((i+m[0],j+m[1]))
                elif self.current_board[i][j].find("white_pawn") == 0:
                    if i - 1 >= 0 and self.current_board[i-1][j] == "":
                        impactPos[1].append((i-1,j))
                        if i == 6 and i - 2 >=0 and self.current_board[i-2][j] == "":
                            impactPos[1].append((i-2,j))
                    if i - 1 >= 0 and j + 1 < 8 and self.current_board[i-1][j+1].find("black") == 0:
                            impactPos[1].append((i-1,j+1))
                    if i - 1 >= 0 and j - 1 >= 0 and self.current_board[i-1][j-1].find("black") == 0:
                            impactPos[1].append((i-1,j-1))
                elif self.current_board[i][j].find("white_rook") == 0:
                    k = 1
                    while j + k < 8:
                        if self.current_board[i][j+k] == "":
                            impactPos[1].append((i,j + k))
                        else:
                            if self.current_board[i][j+k].find("black")==0:
                                impactPos[1].append((i,j + k))
                            break
                        k+=1
                    k = 1
                    while i + k < 8:
                        if self.current_board[i+k][j] == "":
                            impactPos[1].append((i+k,j))
                        else:
                            if self.current_board[i+k][j].find("black")==0:
                                impactPos[1].append((i+k,j))
                            break
                        k+=1
                    k = 1
                    while i - k >= 0:
                        if self.current_board[i-k][j] == "":
                            impactPos[1].append((i-k,j))
                        else:
                            if self.current_board[i-k][j].find("black")==0:
                                impactPos[1].append((i-k,j))
                            break
                        k+=1
                    k = 1
                    while j - k >= 0:
                        if self.current_board[i][j-k] == "":
                            impactPos[1].append((i,j-k))
                        else:
                            if self.current_board[i][j-k].find("black")==0:
                                impactPos[1].append((i,j-k))
                            break
                        k+=1
                elif self.current_board[i][j].find("white_knight") == 0:
                    moves = [(-1,-2), (-1,2), (1,-2), (1,2), (-2,-1), (-2,1), (2,-1), (2,1)]
                    moves = list(filter(lambda x: i + x[0] in list(range(0,8))  and j + x[1] in list(range(0,8)),moves))
                    for m in moves:
                        if self.current_board[i + m[0]][j + m[1]] == "" or self.current_board[i + m[0]][j + m[1]].find("black")==0:
                            impactPos[1].append((i+m[0],j+m[1]))
                elif self.current_board[i][j].find("white_bishop") == 0:
                    k = 1
                    while i + k < 8 and j + k <8:
                        if self.current_board[i+k][j+k] == "":
                            impactPos[1].append((i+k,j+k))
                        else:
                            if self.current_board[i+k][j+k].find("black")==0:
                                impactPos[1].append((i+k,j+k))
                            break
                        k+=1

                    k = 1
                    while i - k >= 0  and j + k <8:
                        if self.current_board[i-k][j+k] == "":
                            impactPos[1].append((i-k,j+k))
                        else:
                            if self.current_board[i-k][j+k].find("black")==0:
                                impactPos[1].append((i-k,j+k))
                            break
                        k+=1
                    k = 1
                    while i + k < 8 and j - k >=0 :
                        if self.current_board[i+k][j-k] == "":
                            impactPos[1].append((i+k,j-k))
                        else:
                            if self.current_board[i+k][j-k].find("black")==0:
                                impactPos[1].append((i+k,j-k))
                            break
                        k+=1
                    k = 1
                    while i - k >= 0 and j - k >=0:
                        if self.current_board[i-k][j-k] == "":
                            impactPos[1].append((i-k,j-k))
                        else:
                            if self.current_board[i-k][j-k].find("black")==0:
                                impactPos[1].append((i-k,j-k))
                            break
                        k+=1
                elif self.current_board[i][j].find("white_queen") == 0:
                    k = 1
                    while j + k < 8:
                        if self.current_board[i][j+k] == "":
                            impactPos[1].append((i,j + k))
                        else:
                            if self.current_board[i][j+k].find("black")==0:
                                impactPos[1].append((i,j + k))
                            break
                        k+=1
                    k = 1
                    while i + k < 8:
                        if self.current_board[i+k][j] == "":
                            impactPos[1].append((i+k,j))
                        else:
                            if self.current_board[i+k][j].find("black")==0:
                                impactPos[1].append((i+k,j))
                            break
                        k+=1
                    k = 1
                    while i - k >= 0:
                        if self.current_board[i-k][j] == "":
                            impactPos[1].append((i-k,j))
                        else:
                            if self.current_board[i-k][j].find("black")==0:
                                impactPos[1].append((i-k,j))
                            break
                        k+=1
                    k = 1
                    while j - k >= 0:
                        if self.current_board[i][j-k] == "":
                            impactPos[1].append((i,j-k))
                        else:
                            if self.current_board[i][j-k].find("black")==0:
                                impactPos[1].append((i,j-k))
                            break
                        k+=1
                    k = 1
                    while i + k < 8 and j + k <8:
                        if self.current_board[i+k][j+k] == "":
                            impactPos[1].append((i+k,j+k))
                        else:
                            if self.current_board[i+k][j+k].find("black")==0:
                                impactPos[1].append((i+k,j+k))
                            break
                        k+=1

                    k = 1
                    while i - k >= 0  and j + k <8:
                        if self.current_board[i-k][j+k] == "":
                            impactPos[1].append((i-k,j+k))
                        else:
                            if self.current_board[i-k][j+k].find("black")==0:
                                impactPos[1].append((i-k,j+k))
                            break
                        k+=1
                    k = 1
                    while i + k < 8 and j - k >=0 :
                        if self.current_board[i+k][j-k] == "":
                            impactPos[1].append((i+k,j-k))
                        else:
                            if self.current_board[i+k][j-k].find("black")==0:
                                impactPos[1].append((i+k,j-k))
                            break
                        k+=1
                    k = 1
                    while i - k >= 0 and j - k >=0:
                        if self.current_board[i-k][j-k] == "":
                            impactPos[1].append((i-k,j-k))
                        else:
                            if self.current_board[i-k][j-k].find("black")==0:
                                impactPos[1].append((i-k,j-k))
                            break
                        k+=1
                elif self.current_board[i][j].find("white_king") == 0:
                    moves = [(1,0), (-1,0), (0,1), (0,-1), (1,1), (-1,-1), (1,-1), (-1,1)]
                    # moves = list(filter(lambda x: (originalPos[0] + x[0] in list(range(0,8)))  and (originalPos[1] + x[1] in list(range(0,8))) ))
                    moves = list(filter(lambda x: i + x[0] in list(range(0,8))  and j + x[1] in list(range(0,8)),moves))
                    for m in moves:
                        if self.current_board[i + m[0]][j + m[1]] == "" or self.current_board[i + m[0]][j + m[1]].find("black")==0:
                            impactPos[0].append((i+m[0],j+m[1]))
        return impactPos

            
       


    def get_all_possible_moves(self,player: str = ['white', 'black']):
        impactPos = self.get_all_impact() #[0] is for black, [1] is for white (not racist)
        movesList = []
        for i in range(8):
            for j in range(8):
                if self.current_board[i][j].find("pawn") >= 0 and self.current_board[i][j].find(player) >= 0:
                    directions = [(1,0),(2,0),(1,1),(1,-1)]
                    promoteList = ['rook', 'knight', 'bishop', 'queen']

                    if player == 'black':
                        for direction in list(filter(lambda x: (i+x[0],j+x[1]) in impactPos[0],directions)):
                            if i + direction[0] == 7:
                                for pr in promoteList:
                                    movesList.append(Move((i,j),(i+direction[0],j+direction[1]),self.current_board[i][j],special_move="promote",promoted = self.current_board[i][j].replace("pawn",pr)))
                            else:
                                movesList.append(Move((i,j),(i+direction[0],j+direction[1]),self.current_board[i][j]))
                    elif player == 'white':
                        for direction in list(filter(lambda x: (i-x[0],j-x[1]) in impactPos[1],directions)):
                            if i - direction[0] == 0:
                                for pr in promoteList:
                                    movesList.append(Move((i,j),(i+direction[0],j-direction[1]),self.current_board[i][j],special_move="promote",promoted = self.current_board[i][j].replace("pawn",pr)))
                            else:
                                movesList.append(Move((i,j),(i-direction[0],j-direction[1]),self.current_board[i][j]))
                elif self.current_board[i][j].find("rook") >= 0 and self.current_board[i][j].find(player) >= 0:
                    side = 0
                    if player == "white":
                        side = 1
                    k = 1
                    while j + k < 8:
                        if (i,j+k) in impactPos[side]:
                            movesList.append(Move((i,j),(i,j+k),self.current_board[i][j]))
                        else:
                            break
                        k+=1
                    k = 1
                    while j - k >= 0:
                        if (i,j-k) in impactPos[side]:
                            movesList.append(Move((i,j),(i,j-k),self.current_board[i][j]))
                        else:
                            break
                        k+=1
                    k = 1
                    while i + k < 8:
                        if (i+k,j) in impactPos[side]:
                            movesList.append(Move((i,j),(i+k,j),self.current_board[i][j]))
                        else:
                            break
                        k+=1
                    k = 1
                    while i - k >= 0:
                        if (i - k,j) in impactPos[side]:
                            movesList.append(Move((i,j),(i-k,j),self.current_board[i][j]))
                        else:
                            break
                        k+=1
                    
                    #castling (not completed)
                    if not self.current_board[i][j].endswith("_"):
                        #finding king
                        kingInd = -1
                        for k in range(8):
                            if self.current_board[i][k].find(player+"_king")>=0:
                                kingInd = k
                        if k>=0 and not self.current_board[i][kingInd].endswith("_"):
                            if not (i,kingInd) in impactPos[abs(side-1)]:
                                pass

                         
                elif self.current_board[i][j].find("knight") >= 0 and self.current_board[i][j].find(player) >= 0:
                    side = 0
                    if player == "white":
                        side = 1
                    moves = [(-1,-2), (-1,2), (1,-2), (1,2), (-2,-1), (-2,1), (2,-1), (2,1)]
                    for m in moves:
                        if (i + m[0], j + m[1]) in impactPos[side]:
                            movesList.append(Move((i,j),(i+m[0],j+m[1]),self.current_board[i][j]))



                elif self.current_board[i][j].find("bishop") >= 0 and self.current_board[i][j].find(player) >= 0:
                    side = 0
                    if player == "white":
                        side = 1
                    k = 1
                    while i + k < 8 and j + k <8:
                        if (i+k,j+k) in impactPos[side]:
                            movesList.append(Move((i,j),(i+k,j+k),self.current_board[i][j]))
                        else:
                            break
                        k+=1
                    k = 1
                    while i - k >= 0 and j + k <8:
                        if (i-k,j+k) in impactPos[side]:
                            movesList.append(Move((i,j),(i-k,j+k),self.current_board[i][j]))
                        else:
                            break
                        k+=1
                    k = 1
                    while i + k < 8 and j - k >= 0:
                        if (i+k,j-k) in impactPos[side]:
                            movesList.append(Move((i,j),(i+k,j-k),self.current_board[i][j]))
                        else:
                            break
                        k+=1
                    k = 1
                    while i - k >=0 and j - k >= 0:
                        if (i-k,j-k) in impactPos[side]:
                            movesList.append(Move((i,j),(i-k,j-k),self.current_board[i][j]))
                        else:
                            break
                        k+=1
                    
                elif self.current_board[i][j].find("queen") >= 0:
                    side = 0
                    if player == "white":
                        side = 1
                    k = 1
                    while j + k < 8:
                        if (i,j+k) in impactPos[side]:
                            movesList.append(Move((i,j),(i,j+k),self.current_board[i][j]))
                        else:
                            break
                        k+=1
                    k = 1
                    while j - k >= 0:
                        if (i,j-k) in impactPos[side]:
                            movesList.append(Move((i,j),(i,j-k),self.current_board[i][j]))
                        else:
                            break
                        k+=1
                    k = 1
                    while i + k < 8:
                        if (i+k,j) in impactPos[side]:
                            movesList.append(Move((i,j),(i+k,j),self.current_board[i][j]))
                        else:
                            break
                        k+=1
                    k = 1
                    while i - k >=0:
                        if (i+k,j) in impactPos[side]:
                            movesList.append(Move((i,j),(i-k,j),self.current_board[i][j]))
                        else:
                            break
                        k+=1
                    k = 1
                    while i + k < 8 and j + k <8:
                        if (i+k,j+k) in impactPos[side]:
                            movesList.append(Move((i,j),(i+k,j+k),self.current_board[i][j]))
                        else:
                            break
                        k+=1
                    k = 1
                    while i - k >= 0 and j + k <8:
                        if (i-k,j+k) in impactPos[side]:
                            movesList.append(Move((i,j),(i-k,j+k),self.current_board[i][j]))
                        else:
                            break
                        k+=1
                    k = 1
                    while i + k < 8 and j - k >= 0:
                        if (i+k,j-k) in impactPos[side]:
                            movesList.append(Move((i,j),(i+k,j-k),self.current_board[i][j]))
                        else:
                            break
                        k+=1
                    k = 1
                    while i - k >=0 and j - k >= 0:
                        if (i-k,j-k) in impactPos[side]:
                            movesList.append(Move((i,j),(i-k,j-k),self.current_board[i][j]))
                        else:
                            break
                        k+=1
                elif self.current_board[i][j].find("king") >= 0 and self.current_board[i][j].find(player) >= 0:
                    side = 0
                    if player == "white":
                        side = 1
                    moves = [(1,0), (-1,0), (0,1), (0,-1), (1,1), (-1,-1), (1,-1), (-1,1)]
                    for m in moves:
                        if (i + m[0], j + m[1]) in impactPos[side]:
                            movesList.append(Move((i,j),(i+m[0],j+m[1]),self.current_board[i][j]))
        return movesList
    def make_move(self,move: Move):
        self.previous_board.insert(0,copy.deepcopy(self.current_board))
        unit = self.current_board[move.position[0]][move.position[1]]
        self.current_board[move.position[0]][move.position[1]] = ""
        self.current_board[move.new_pos[0]][move.new_pos[1]] = unit
        if move.special_move == "promote":
            self.current_board[move.new_pos[0]][move.new_pos[1]] = move.promoted
        self.canvas.delete("all")
        self.draw_board()
        self.draw_pieces()
    def undo_move(self):
        if len(self.previous_board)==0:
            return
        self.current_board = copy.deepcopy(self.previous_board[0])
        self.previous_board.pop(0)
        self.canvas.delete("all")
        self.draw_board()
        self.draw_pieces()

        




            

                    
           
            

                    




if __name__ == "__main__":
    app = ChessBoard()
    print(app.get_all_impact())
    for i in app.get_all_possible_moves("black"):
        print(i)
    app.mainloop()