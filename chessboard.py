import tkinter as tk
from PIL import Image, ImageTk
import copy
import numpy as np
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
        self.click = False

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

        # tkinter
        self.oldPosX = None
        self.oldPosY = None
        self.type = None
        self.impactPos = None

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
                piece = self.current_board[row][col]
                if piece != '':
                    piece_image = self.piece_images[piece]
                    self.canvas.create_image(col * self.size + self.size/2, row * self.size + self.size/2,
                                             image=piece_image, tags=(piece, "piece"))
    
    def start_drag(self, event):
        x, y = event.x, event.y
        overlapping = self.canvas.find_overlapping(x, y, x, y)
        if overlapping:
            tags = self.canvas.gettags(overlapping[-1])
            # print(overlapping[-1])
            print(tags)
            self.oldPosX = x
            self.oldPosY = y
            row = (y) // self.size
            col = (x) // self.size
            # print(f'tag:{tags[0]}') # tag[0] -> unitType
            # print(self.impact_pos())
            if tags[0].find("white")==0:
                self.type = 0 
            else: self.type =1
            moves = self.impact_pos(tags[0],(row,col))
            # print(moves)
            for move in moves:
                row = (move[0])
                col = (move[1])
                x1 = col * self.size
                y1 = row * self.size
                x2 = x1 + self.size
                y2 = y1 + self.size
                # self.canvas.create_rectangle(x1, y1, x2, y2, fill="yellow")
            if "piece" in tags:
                self.drag_data["piece"] = overlapping[-1]
                self.drag_data["x"] = x
                self.drag_data["y"] = y
            self.impactPos = moves
    
    def drag(self, event):
        
        if self.drag_data["piece"]:
            dx = event.x - self.drag_data["x"]
            dy = event.y - self.drag_data["y"]
            self.canvas.move(self.drag_data["piece"], dx, dy)
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y
        
    
    def drop(self, event):

        row = (event.y) // self.size
        col = (event.x) // self.size
        if (row,col) not in self.impactPos:
            x = ((self.oldPosX)//self.size)*self.size + self.size / 2
            y = ((self.oldPosY)//self.size)*self.size+ self.size / 2
            self.canvas.coords(self.drag_data["piece"], x,y)
            return 
        
        if self.drag_data["piece"]:
            x, y = event.x, event.y
            a,b = self.oldPosX,self.oldPosY

            r = (b)//self.size
            c= (a)//self.size
            
            square_size = self.size
            #col * self.size + self.size/2, row * self.size + self.size/2,
            row = (y) // square_size
            col = (x) // square_size

            # if self.curr
            new_x = col * square_size + square_size / 2
            new_y = row * square_size + square_size / 2
            
            self.canvas.coords(self.drag_data["piece"], new_x , new_y)
            overlapping = self.canvas.find_overlapping(x, y, x, y)
        
            
            if (len(overlapping) ==3):
                if self.type ==0:
                    self.canvas.delete(overlapping[1])
                else: self.canvas.delete(overlapping[2])
            self.drag_data["piece"] = None
            # position, newPos, unitType, special_move = "", promoted = ""
            overlapping = self.canvas.find_overlapping(x, y, x, y)
            tags = self.canvas.gettags(overlapping[-1])                                                

            self.move_log.append(Move((r,c),(row,col),tags[0]))
            for ele in self.move_log:
                print(ele)
            self.previous_board.insert(0,copy.deepcopy(self.current_board))
            unit = self.current_board[self.move_log[-1].position[0]][self.move_log[-1].position[1]]
            self.current_board[self.move_log[-1].position[0]][self.move_log[-1].position[1]] = ""
            self.current_board[self.move_log[-1].new_pos[0]][self.move_log[-1].new_pos[1]] = unit
            if self.move_log[-1].special_move == "promote":
                self.current_board[self.move_log[-1].new_pos[0]][self.move_log[-1].new_pos[1]] = self.move_log[-1].promoted
            
        # self.make_move(self.move_log[-1])

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
    def get_all_impact(self, board):
        impactPos = ([],[]) #[0] is for black, [1] is for white (not racist)
        for i in range(8):
            for j in range(8):
                if board[i][j].find("black_pawn") == 0:
                    if i + 1 < 8 and board[i+1][j] == "":
                        impactPos[0].append((i+1,j))
                        if i == 1 and i + 2 < 8 and board[i+2][j] == "":
                            impactPos[0].append((i+2,j))
                    if i + 1 < 8 and j + 1 < 8 and board[i+1][j+1].find("white") == 0:
                            impactPos[0].append((i+1,j+1))
                    if i + 1 < 8 and j - 1 >= 0 and board[i+1][j-1].find("white") == 0:
                            impactPos[0].append((i+1,j-1))
                        

                elif board[i][j].find("black_rook") == 0:
                    k = 1
                    while j + k < 8:
                        if board[i][j+k] == "":
                            impactPos[0].append((i,j + k))
                        else:
                            if board[i][j+k].find("white")==0:
                                impactPos[0].append((i,j + k))
                            break
                        k+=1
                    k = 1
                    while i + k < 8:
                        if board[i+k][j] == "":
                            impactPos[0].append((i+k,j))
                        else:
                            if board[i+k][j].find("white")==0:
                                impactPos[0].append((i+k,j))
                            break
                        k+=1
                    k = 1
                    while i - k >= 0:
                        if board[i-k][j] == "":
                            impactPos[0].append((i-k,j))
                        else:
                            if board[i-k][j].find("white")==0:
                                impactPos[0].append((i-k,j))
                            break
                        k+=1
                    k = 1
                    while j - k >= 0:
                        if board[i][j-k] == "":
                            impactPos[0].append((i,j-k))
                        else:
                            if board[i][j-k].find("white")==0:
                                impactPos[0].append((i,j-k))
                            break
                        k+=1
                elif board[i][j].find("black_knight") == 0:
                    moves = [(-1,-2), (-1,2), (1,-2), (1,2), (-2,-1), (-2,1), (2,-1), (2,1)]
                    moves = list(filter(lambda x: i + x[0] in list(range(0,8))  and j + x[1] in list(range(0,8)),moves))
                    for m in moves:
                        if board[i + m[0]][j + m[1]] == "" or board[i + m[0]][j + m[1]].find("white")==0:
                            impactPos[0].append((i+m[0],j+m[1]))
                elif board[i][j].find("black_bishop") == 0:
                    k = 1
                    while i + k < 8 and j + k <8:
                        if board[i+k][j+k] == "":
                            impactPos[0].append((i+k,j+k))
                        else:
                            if board[i+k][j+k].find("white")==0:
                                impactPos[0].append((i+k,j+k))
                            break
                        k+=1

                    k = 1
                    while i - k >= 0  and j + k <8:
                        if board[i-k][j+k] == "":
                            impactPos[0].append((i-k,j+k))
                        else:
                            if board[i-k][j+k].find("white")==0:
                                impactPos[0].append((i-k,j+k))
                            break
                        k+=1
                    k = 1
                    while i + k < 8 and j - k >=0 :
                        if board[i+k][j-k] == "":
                            impactPos[0].append((i+k,j-k))
                        else:
                            if board[i+k][j-k].find("white")==0:
                                impactPos[0].append((i+k,j-k))
                            break
                        k+=1
                    k = 1
                    while i - k >= 0 and j - k >=0:
                        if board[i-k][j-k] == "":
                            impactPos[0].append((i-k,j-k))
                        else:
                            if board[i-k][j-k].find("white")==0:
                                impactPos[0].append((i-k,j-k))
                            break
                        k+=1
                elif board[i][j].find("black_queen") == 0:
                    k = 1
                    while j + k < 8:
                        if board[i][j+k] == "":
                            impactPos[0].append((i,j + k))
                        else:
                            if board[i][j+k].find("white")==0:
                                impactPos[0].append((i,j + k))
                            break
                        k+=1
                    k = 1
                    while i + k < 8:
                        if board[i+k][j] == "":
                            impactPos[0].append((i+k,j))
                        else:
                            if board[i+k][j].find("white")==0:
                                impactPos[0].append((i+k,j))
                            break
                        k+=1
                    k = 1
                    while i - k >= 0:
                        if board[i-k][j] == "":
                            impactPos[0].append((i-k,j))
                        else:
                            if board[i-k][j].find("white")==0:
                                impactPos[0].append((i-k,j))
                            break
                        k+=1
                    k = 1
                    while j - k >= 0:
                        if board[i][j-k] == "":
                            impactPos[0].append((i,j-k))
                        else:
                            if board[i][j-k].find("white")==0:
                                impactPos[0].append((i,j-k))
                            break
                        k+=1
                    k = 1
                    while i + k < 8 and j + k <8:
                        if board[i+k][j+k] == "":
                            impactPos[0].append((i+k,j+k))
                        else:
                            if board[i+k][j+k].find("white")==0:
                                impactPos[0].append((i+k,j+k))
                            break
                        k+=1

                    k = 1
                    while i - k >= 0  and j + k <8:
                        if board[i-k][j+k] == "":
                            impactPos[0].append((i-k,j+k))
                        else:
                            if board[i-k][j+k].find("white")==0:
                                impactPos[0].append((i-k,j+k))
                            break
                        k+=1
                    k = 1
                    while i + k < 8 and j - k >=0 :
                        if board[i+k][j-k] == "":
                            impactPos[0].append((i+k,j-k))
                        else:
                            if board[i+k][j-k].find("white")==0:
                                impactPos[0].append((i+k,j-k))
                            break
                        k+=1
                    k = 1
                    while i - k >= 0 and j - k >=0:
                        if board[i-k][j-k] == "":
                            impactPos[0].append((i-k,j-k))
                        else:
                            if board[i-k][j-k].find("white")==0:
                                impactPos[0].append((i-k,j-k))
                            break
                        k+=1
                elif board[i][j].find("black_king") == 0:
                    moves = [(1,0), (-1,0), (0,1), (0,-1), (1,1), (-1,-1), (1,-1), (-1,1)]
                    # moves = list(filter(lambda x: (originalPos[0] + x[0] in list(range(0,8)))  and (originalPos[1] + x[1] in list(range(0,8))) ))
                    moves = list(filter(lambda x: i + x[0] in list(range(0,8))  and j + x[1] in list(range(0,8)),moves))
                    for m in moves:
                        if board[i + m[0]][j + m[1]] == "" or board[i + m[0]][j + m[1]].find("white")==0:
                            impactPos[0].append((i+m[0],j+m[1]))
                elif board[i][j].find("white_pawn") == 0:
                    if i - 1 >= 0 and board[i-1][j] == "":
                        impactPos[1].append((i-1,j))
                        if i == 6 and i - 2 >=0 and board[i-2][j] == "":
                            impactPos[1].append((i-2,j))
                    if i - 1 >= 0 and j + 1 < 8 and board[i-1][j+1].find("black") == 0:
                            impactPos[1].append((i-1,j+1))
                    if i - 1 >= 0 and j - 1 >= 0 and board[i-1][j-1].find("black") == 0:
                            impactPos[1].append((i-1,j-1))
                elif board[i][j].find("white_rook") == 0:
                    k = 1
                    while j + k < 8:
                        if board[i][j+k] == "":
                            impactPos[1].append((i,j + k))
                        else:
                            if board[i][j+k].find("black")==0:
                                impactPos[1].append((i,j + k))
                            break
                        k+=1
                    k = 1
                    while i + k < 8:
                        if board[i+k][j] == "":
                            impactPos[1].append((i+k,j))
                        else:
                            if board[i+k][j].find("black")==0:
                                impactPos[1].append((i+k,j))
                            break
                        k+=1
                    k = 1
                    while i - k >= 0:
                        if board[i-k][j] == "":
                            impactPos[1].append((i-k,j))
                        else:
                            if board[i-k][j].find("black")==0:
                                impactPos[1].append((i-k,j))
                            break
                        k+=1
                    k = 1
                    while j - k >= 0:
                        if board[i][j-k] == "":
                            impactPos[1].append((i,j-k))
                        else:
                            if board[i][j-k].find("black")==0:
                                impactPos[1].append((i,j-k))
                            break
                        k+=1
                elif board[i][j].find("white_knight") == 0:
                    moves = [(-1,-2), (-1,2), (1,-2), (1,2), (-2,-1), (-2,1), (2,-1), (2,1)]
                    moves = list(filter(lambda x: i + x[0] in list(range(0,8))  and j + x[1] in list(range(0,8)),moves))
                    for m in moves:
                        if board[i + m[0]][j + m[1]] == "" or board[i + m[0]][j + m[1]].find("black")==0:
                            impactPos[1].append((i+m[0],j+m[1]))
                elif board[i][j].find("white_bishop") == 0:
                    k = 1
                    while i + k < 8 and j + k <8:
                        if board[i+k][j+k] == "":
                            impactPos[1].append((i+k,j+k))
                        else:
                            if board[i+k][j+k].find("black")==0:
                                impactPos[1].append((i+k,j+k))
                            break
                        k+=1

                    k = 1
                    while i - k >= 0  and j + k <8:
                        if board[i-k][j+k] == "":
                            impactPos[1].append((i-k,j+k))
                        else:
                            if board[i-k][j+k].find("black")==0:
                                impactPos[1].append((i-k,j+k))
                            break
                        k+=1
                    k = 1
                    while i + k < 8 and j - k >=0 :
                        if board[i+k][j-k] == "":
                            impactPos[1].append((i+k,j-k))
                        else:
                            if board[i+k][j-k].find("black")==0:
                                impactPos[1].append((i+k,j-k))
                            break
                        k+=1
                    k = 1
                    while i - k >= 0 and j - k >=0:
                        if board[i-k][j-k] == "":
                            impactPos[1].append((i-k,j-k))
                        else:
                            if board[i-k][j-k].find("black")==0:
                                impactPos[1].append((i-k,j-k))
                            break
                        k+=1
                elif board[i][j].find("white_queen") == 0:
                    k = 1
                    while j + k < 8:
                        if board[i][j+k] == "":
                            impactPos[1].append((i,j + k))
                        else:
                            if board[i][j+k].find("black")==0:
                                impactPos[1].append((i,j + k))
                            break
                        k+=1
                    k = 1
                    while i + k < 8:
                        if board[i+k][j] == "":
                            impactPos[1].append((i+k,j))
                        else:
                            if board[i+k][j].find("black")==0:
                                impactPos[1].append((i+k,j))
                            break
                        k+=1
                    k = 1
                    while i - k >= 0:
                        if board[i-k][j] == "":
                            impactPos[1].append((i-k,j))
                        else:
                            if board[i-k][j].find("black")==0:
                                impactPos[1].append((i-k,j))
                            break
                        k+=1
                    k = 1
                    while j - k >= 0:
                        if board[i][j-k] == "":
                            impactPos[1].append((i,j-k))
                        else:
                            if board[i][j-k].find("black")==0:
                                impactPos[1].append((i,j-k))
                            break
                        k+=1
                    k = 1
                    while i + k < 8 and j + k <8:
                        if board[i+k][j+k] == "":
                            impactPos[1].append((i+k,j+k))
                        else:
                            if board[i+k][j+k].find("black")==0:
                                impactPos[1].append((i+k,j+k))
                            break
                        k+=1

                    k = 1
                    while i - k >= 0  and j + k <8:
                        if board[i-k][j+k] == "":
                            impactPos[1].append((i-k,j+k))
                        else:
                            if board[i-k][j+k].find("black")==0:
                                impactPos[1].append((i-k,j+k))
                            break
                        k+=1
                    k = 1
                    while i + k < 8 and j - k >=0 :
                        if board[i+k][j-k] == "":
                            impactPos[1].append((i+k,j-k))
                        else:
                            if board[i+k][j-k].find("black")==0:
                                impactPos[1].append((i+k,j-k))
                            break
                        k+=1
                    k = 1
                    while i - k >= 0 and j - k >=0:
                        if board[i-k][j-k] == "":
                            impactPos[1].append((i-k,j-k))
                        else:
                            if board[i-k][j-k].find("black")==0:
                                impactPos[1].append((i-k,j-k))
                            break
                        k+=1
                elif board[i][j].find("white_king") == 0:
                    moves = [(1,0), (-1,0), (0,1), (0,-1), (1,1), (-1,-1), (1,-1), (-1,1)]
                    # moves = list(filter(lambda x: (originalPos[0] + x[0] in list(range(0,8)))  and (originalPos[1] + x[1] in list(range(0,8))) ))
                    moves = list(filter(lambda x: i + x[0] in list(range(0,8))  and j + x[1] in list(range(0,8)),moves))
                    for m in moves:
                        if board[i + m[0]][j + m[1]] == "" or board[i + m[0]][j + m[1]].find("black")==0:
                            impactPos[1].append((i+m[0],j+m[1]))
        return impactPos

    def get_all_possible_moves(self,player: str = ['white', 'black']):
        impactPos = self.get_all_impact(copy.deepcopy(self.current_board)) #[0] is for black, [1] is for white (not racist)
        movesList = []
        kingPos = (-1,-1)
        for i in range(8):
            for j in range(8):
                if self.current_board[i][j].find("pawn") >= 0 and self.current_board[i][j].find(player) >= 0:
                    direction = (1,0)
                    doubleDirection = (2,0)
                    attackDirections = [(1,1), (1,-1)]
                    promoteList = ['rook', 'knight', 'bishop', 'queen']
                    mList = []
                    if player == 'black':
                        if (i+direction[0],j+direction[1]) in impactPos[0] and self.current_board[i+direction[0]][j+direction[1]]=="":
                            mList.append(Move((i,j),(i+direction[0],j+direction[1]),self.current_board[i][j]))
                            if (i+direction[0]*2,j+direction[1]) in impactPos[0] and self.current_board[i+direction[0]*2][j+direction[1]]=="" and i==1:
                                mList.append(Move((i,j),(i+direction[0]*2,j+direction[1]),self.current_board[i][j]))
                        for dir in attackDirections:
                            if (i+dir[0],j+dir[1]) in impactPos[0] and self.current_board[i+dir[0]][j+dir[1]].find("white")>=0:
                                mList.append(Move((i,j),(i+dir[0],j+dir[1]),self.current_board[i][j]))
                        for m in mList:
                            if m.new_pos[0] == 7:
                                
                                for pr in promoteList:
                                    movesList.append(Move(m.position,m.new_pos,m.unit_type,special_move="promote",promoted = m.unit_type.replace("pawn",pr)))
                            else:
                                movesList.append(m)
        

                        
                    elif player == 'white':
                        if (i-direction[0],j-direction[1]) in impactPos[1] and self.current_board[i-direction[0]][j-direction[1]]=="":
                            mList.append(Move((i,j),(i-direction[0],j-direction[1]),self.current_board[i][j]))
                            if (i-direction[0]*2,j-direction[1]) in impactPos[1] and self.current_board[i-direction[0]*2][j-direction[1]]=="" and i==6:
                                mList.append(Move((i,j),(i-direction[0]*2,j-direction[1]),self.current_board[i][j]))
                        for dir in attackDirections:
                            if (i-dir[0],j-dir[1]) in impactPos[1] and self.current_board[i-dir[0]][j-dir[1]].find("black")>=0:
                                mList.append(Move((i,j),(i-dir[0],j-dir[1]),self.current_board[i][j]))
                        for m in mList:
                            if m.new_pos[0] == 0:
                                
                                for pr in promoteList:
                                    movesList.append(Move(m.position,m.new_pos,m.unit_type,special_move="promote",promoted = m.unit_type.replace("pawn",pr)))
                            else:
                                movesList.append(m)
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
                    
                elif self.current_board[i][j].find("queen") >= 0 and self.current_board[i][j].find(player) >= 0:
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
                    kingPos = (i,j)
                    side = 0
                    if player == "white":
                        side = 1
                    moves = [(1,0), (-1,0), (0,1), (0,-1), (1,1), (-1,-1), (1,-1), (-1,1)]
                    for m in moves:
                        if (i + m[0], j + m[1]) in impactPos[side]:
                            movesList.append(Move((i,j),(i+m[0],j+m[1]),self.current_board[i][j]))
        side = 0
        if player == "white":
            side = 1
        #print(kingPos)
        print(impactPos[1])
        if True:
            legalList = []

            for mv in movesList:
                temp_board = copy.deepcopy(self.current_board)
                unit = temp_board[mv.position[0]][mv.position[1]]
                temp_board[mv.position[0]][mv.position[1]] = ""
                temp_board[mv.new_pos[0]][mv.new_pos[1]] = unit
                #print(temp_board)

                if mv.special_move == "promote":
                    temp_board[mv.new_pos[0]][mv.new_pos[1]] = mv.promoted
                newImpact = self.get_all_impact(copy.deepcopy(temp_board))
                print(mv, mv.new_pos in newImpact[(side + 1)%2])

                #print(newImpact)
                if mv.unit_type.find("_king")>0:
                    #print(mv, mv.new_pos in newImpact[(side + 1)%2])
                    print(temp_board[7][2])
                    print(newImpact)
                    if mv.new_pos in newImpact[(side + 1)%2]:
                        continue
                else:

                    if kingPos in newImpact[(side + 1)%2]:
                        continue
                legalList.append(mv)

            return legalList
        else:
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
    def impact_pos(self,unitType,pos):
        impactPos = [] 
        i,j = pos
        if unitType == "black_pawn":
            if i + 1 < 8 and self.current_board[i+1][j] == "":
                impactPos.append((i+1,j))
                if i == 1 and i + 2 < 8 and self.current_board[i+2][j] == "":
                    impactPos.append((i+2,j))
            if i + 1 < 8 and j + 1 < 8 and self.current_board[i+1][j+1].find("white") == 0:
                    impactPos.append((i+1,j+1))
            if i + 1 < 8 and j - 1 >= 0 and self.current_board[i+1][j-1].find("white") == 0:
                    impactPos.append((i+1,j-1))
        elif unitType == "black_rook":
            k = 1
            while j + k < 8:
                if self.current_board[i][j+k] == "":
                    impactPos.append((i,j + k))
                else:
                    if self.current_board[i][j+k].find("white")==0:
                        impactPos.append((i,j + k))
                    break
                k+=1
            k = 1
            while i + k < 8:
                if self.current_board[i+k][j] == "":
                    impactPos.append((i+k,j))
                else:
                    if self.current_board[i+k][j].find("white")==0:
                        impactPos.append((i+k,j))
                    break
                k+=1
            k = 1
            while i - k >= 0:
                if self.current_board[i-k][j] == "":
                    impactPos.append((i-k,j))
                else:
                    if self.current_board[i-k][j].find("white")==0:
                        impactPos.append((i-k,j))
                    break
                k+=1
            k = 1
            while j - k >= 0:
                if self.current_board[i][j-k] == "":
                    impactPos.append((i,j-k))
                else:
                    if self.current_board[i][j-k].find("white")==0:
                        impactPos.append((i,j-k))
                    break
                k+=1
        
        elif unitType == "black_knight":
            moves = [(-1,-2), (-1,2), (1,-2), (1,2), (-2,-1), (-2,1), (2,-1), (2,1)]
            moves = list(filter(lambda x: i + x[0] in list(range(0,8))  and j + x[1] in list(range(0,8)),moves))
            for m in moves:
                if self.current_board[i + m[0]][j + m[1]] == "" or self.current_board[i + m[0]][j + m[1]].find("white")==0:
                    impactPos.append((i+m[0],j+m[1]))

        elif unitType == "black_bishop":
            k = 1
            while i + k < 8 and j + k <8:
                if self.current_board[i+k][j+k] == "":
                    impactPos.append((i+k,j+k))
                else:
                    if self.current_board[i+k][j+k].find("white")==0:
                        impactPos.append((i+k,j+k))
                    break
                k+=1

            k = 1
            while i - k >= 0  and j + k <8:
                if self.current_board[i-k][j+k] == "":
                    impactPos.append((i-k,j+k))
                else:
                    if self.current_board[i-k][j+k].find("white")==0:
                        impactPos.append((i-k,j+k))
                    break
                k+=1
            k = 1
            while i + k < 8 and j - k >=0 :
                if self.current_board[i+k][j-k] == "":
                    impactPos.append((i+k,j-k))
                else:
                    if self.current_board[i+k][j-k].find("white")==0:
                        impactPos.append((i+k,j-k))
                    break
                k+=1
            k = 1
            while i - k >= 0 and j - k >=0:
                if self.current_board[i-k][j-k] == "":
                    impactPos.append((i-k,j-k))
                else:
                    if self.current_board[i-k][j-k].find("white")==0:
                        impactPos.append((i-k,j-k))
                    break
                k+=1    
        elif unitType == "black_queen":
            k = 1
            while j + k < 8:
                if self.current_board[i][j+k] == "":
                    impactPos.append((i,j + k))
                else:
                    if self.current_board[i][j+k].find("white")==0:
                        impactPos.append((i,j + k))
                    break
                k+=1
            k = 1
            while i + k < 8:
                if self.current_board[i+k][j] == "":
                    impactPos.append((i+k,j))
                else:
                    if self.current_board[i+k][j].find("white")==0:
                        impactPos.append((i+k,j))
                    break
                k+=1
            k = 1
            while i - k >= 0:
                if self.current_board[i-k][j] == "":
                    impactPos.append((i-k,j))
                else:
                    if self.current_board[i-k][j].find("white")==0:
                        impactPos.append((i-k,j))
                    break
                k+=1
            k = 1
            while j - k >= 0:
                if self.current_board[i][j-k] == "":
                    impactPos.append((i,j-k))
                else:
                    if self.current_board[i][j-k].find("white")==0:
                        impactPos.append((i,j-k))
                    break
                k+=1
            k = 1
            while i + k < 8 and j + k <8:
                if self.current_board[i+k][j+k] == "":
                    impactPos.append((i+k,j+k))
                else:
                    if self.current_board[i+k][j+k].find("white")==0:
                        impactPos.append((i+k,j+k))
                    break
                k+=1

            k = 1
            while i - k >= 0  and j + k <8:
                if self.current_board[i-k][j+k] == "":
                    impactPos.append((i-k,j+k))
                else:
                    if self.current_board[i-k][j+k].find("white")==0:
                        impactPos.append((i-k,j+k))
                    break
                k+=1
            k = 1
            while i + k < 8 and j - k >=0 :
                if self.current_board[i+k][j-k] == "":
                    impactPos.append((i+k,j-k))
                else:
                    if self.current_board[i+k][j-k].find("white")==0:
                        impactPos.append((i+k,j-k))
                    break
                k+=1
            k = 1
            while i - k >= 0 and j - k >=0:
                if self.current_board[i-k][j-k] == "":
                    impactPos.append((i-k,j-k))
                else:
                    if self.current_board[i-k][j-k].find("white")==0:
                        impactPos.append((i-k,j-k))
                    break
                k+=1
        elif unitType == "black_king":
            moves = [(1,0), (-1,0), (0,1), (0,-1), (1,1), (-1,-1), (1,-1), (-1,1)]
            # moves = list(filter(lambda x: (originalPos[0] + x[0] in list(range(0,8)))  and (originalPos[1] + x[1] in list(range(0,8))) ))
            moves = list(filter(lambda x: i + x[0] in list(range(0,8))  and j + x[1] in list(range(0,8)),moves))
            for m in moves:
                if self.current_board[i + m[0]][j + m[1]] == "" or self.current_board[i + m[0]][j + m[1]].find("white")==0:
                    impactPos.append((i+m[0],j+m[1]))
                    
        elif unitType =="white_pawn":
            if i - 1 >= 0 and self.current_board[i-1][j] == "":
                impactPos.append((i-1,j))
                if i == 6 and i - 2 >=0 and self.current_board[i-2][j] == "":
                    impactPos.append((i-2,j))
            if i - 1 >= 0 and j + 1 < 8 and self.current_board[i-1][j+1].find("black") == 0:
                    impactPos.append((i-1,j+1))
            if i - 1 >= 0 and j - 1 >= 0 and self.current_board[i-1][j-1].find("black") == 0:
                    impactPos.append((i-1,j-1))   
        elif unitType == "white_rook":
            k = 1
            while j + k < 8:
                if self.current_board[i][j+k] == "":
                    impactPos.append((i,j + k))
                else:
                    if self.current_board[i][j+k].find("black")==0:
                        impactPos.append((i,j + k))
                    break
                k+=1
            k = 1
            while i + k < 8:
                if self.current_board[i+k][j] == "":
                    impactPos.append((i+k,j))
                else:
                    if self.current_board[i+k][j].find("black")==0:
                        impactPos.append((i+k,j))
                    break
                k+=1
            k = 1
            while i - k >= 0:
                if self.current_board[i-k][j] == "":
                    impactPos.append((i-k,j))
                else:
                    if self.current_board[i-k][j].find("black")==0:
                        impactPos.append((i-k,j))
                    break
                k+=1
            k = 1
            while j - k >= 0:
                if self.current_board[i][j-k] == "":
                    impactPos.append((i,j-k))
                else:
                    if self.current_board[i][j-k].find("black")==0:
                        impactPos.append((i,j-k))
                    break
                k+=1   
        elif unitType =="white_knight":
            moves = [(-1,-2), (-1,2), (1,-2), (1,2), (-2,-1), (-2,1), (2,-1), (2,1)]
            moves = list(filter(lambda x: i + x[0] in list(range(0,8))  and j + x[1] in list(range(0,8)),moves))
            for m in moves:
                if self.current_board[i + m[0]][j + m[1]] == "" or self.current_board[i + m[0]][j + m[1]].find("black")==0:
                    impactPos.append((i+m[0],j+m[1]))    

        elif unitType == "white_bishop":
            k = 1
            while i + k < 8 and j + k <8:
                if self.current_board[i+k][j+k] == "":
                    impactPos.append((i+k,j+k))
                else:
                    if self.current_board[i+k][j+k].find("black")==0:
                        impactPos.append((i+k,j+k))
                    break
                k+=1

            k = 1
            while i - k >= 0  and j + k <8:
                if self.current_board[i-k][j+k] == "":
                    impactPos.append((i-k,j+k))
                else:
                    if self.current_board[i-k][j+k].find("black")==0:
                        impactPos.append((i-k,j+k))
                    break
                k+=1
            k = 1
            while i + k < 8 and j - k >=0 :
                if self.current_board[i+k][j-k] == "":
                    impactPos.append((i+k,j-k))
                else:
                    if self.current_board[i+k][j-k].find("black")==0:
                        impactPos.append((i+k,j-k))
                    break
                k+=1
            k = 1
            while i - k >= 0 and j - k >=0:
                if self.current_board[i-k][j-k] == "":
                    impactPos.append((i-k,j-k))
                else:
                    if self.current_board[i-k][j-k].find("black")==0:
                        impactPos.append((i-k,j-k))
                    break
                k+=1

            
        elif unitType == "white_queen":
            k = 1
            while j + k < 8:
                if self.current_board[i][j+k] == "":
                    impactPos.append((i,j + k))
                else:
                    if self.current_board[i][j+k].find("black")==0:
                        impactPos.append((i,j + k))
                    break
                k+=1
            k = 1
            while i + k < 8:
                if self.current_board[i+k][j] == "":
                    impactPos.append((i+k,j))
                else:
                    if self.current_board[i+k][j].find("black")==0:
                        impactPos.append((i+k,j))
                    break
                k+=1
            k = 1
            while i - k >= 0:
                if self.current_board[i-k][j] == "":
                    impactPos.append((i-k,j))
                else:
                    if self.current_board[i-k][j].find("black")==0:
                        impactPos.append((i-k,j))
                    break
                k+=1
            k = 1
            while j - k >= 0:
                if self.current_board[i][j-k] == "":
                    impactPos.append((i,j-k))
                else:
                    if self.current_board[i][j-k].find("black")==0:
                        impactPos.append((i,j-k))
                    break
                k+=1
            k = 1
            while i + k < 8 and j + k <8:
                if self.current_board[i+k][j+k] == "":
                    impactPos.append((i+k,j+k))
                else:
                    if self.current_board[i+k][j+k].find("black")==0:
                        impactPos.append((i+k,j+k))
                    break
                k+=1

            k = 1
            while i - k >= 0  and j + k <8:
                if self.current_board[i-k][j+k] == "":
                    impactPos.append((i-k,j+k))
                else:
                    if self.current_board[i-k][j+k].find("black")==0:
                        impactPos.append((i-k,j+k))
                    break
                k+=1
            k = 1
            while i + k < 8 and j - k >=0 :
                if self.current_board[i+k][j-k] == "":
                    impactPos.append((i+k,j-k))
                else:
                    if self.current_board[i+k][j-k].find("black")==0:
                        impactPos.append((i+k,j-k))
                    break
                k+=1
            k = 1
            while i - k >= 0 and j - k >=0:
                if self.current_board[i-k][j-k] == "":
                    impactPos.append((i-k,j-k))
                else:
                    if self.current_board[i-k][j-k].find("black")==0:
                        impactPos.append((i-k,j-k))
                    break
                k+=1   

        elif unitType =="white_king":
            moves = [(1,0), (-1,0), (0,1), (0,-1), (1,1), (-1,-1), (1,-1), (-1,1)]
            # moves = list(filter(lambda x: (originalPos[0] + x[0] in list(range(0,8)))  and (originalPos[1] + x[1] in list(range(0,8))) ))
            moves = list(filter(lambda x: i + x[0] in list(range(0,8))  and j + x[1] in list(range(0,8)),moves))
            for m in moves:
                if self.current_board[i + m[0]][j + m[1]] == "" or self.current_board[i + m[0]][j + m[1]].find("black")==0:
                    impactPos.append((i+m[0],j+m[1]))    
                    
        return impactPos
        
    def read_move(self,move:Move):
      # position, newPos, unitType, special_move = "", promoted = "" 
        
        oldPosX = move.position[1]*self.size + self.size / 2
        oldPosY = move.position[0]*self.size+ self.size / 2
        newPosX = move.new_pos[1]*self.size+ self.size / 2
        newPosY = move.new_pos[0]*self.size+ self.size / 2

        oldX = move.position[1]
        oldY = move.position[0]
        newX = move.new_pos[1]
        newY = move.new_pos[0]

        overlapping = self.canvas.find_overlapping(oldPosX, oldPosY, oldPosX, oldPosY)
        moves = self.impact_pos(move.unit_type,(oldY,oldX))
        print(f"{move.unit_type} {moves}")
        if (newY,newX) not in moves:
            print("error")
            return
        else:
            self.previous_board.insert(0,copy.deepcopy(self.current_board))

            a,b = oldPosX,oldPosY
            x,y = newPosX,newPosY
            r = int((b)//self.size)
            c= int((a)//self.size)
            
            square_size = self.size
            #col * self.size + self.size/2, row * self.size + self.size/2,
            row = int((y) // square_size)
            col = int((x) // square_size)

            # if self.curr
            new_x = col * square_size + square_size / 2
            new_y = row * square_size + square_size / 2
            # overlapping = self.canvas.find_overlapping(x, y, x, y)
            # print(overlapping[-1])
            
            self.canvas.coords(overlapping[-1], new_x , new_y)
            overlapping = self.canvas.find_overlapping(x, y, x, y)
        
            if move.unit_type.find("white")==0:
                self.type = 0 
            else: self.type =1
            if (len(overlapping) ==3):
                if self.type ==0:
                    self.canvas.delete(overlapping[1])
                else: self.canvas.delete(overlapping[2])
            self.drag_data["piece"] = None
            # position, newPos, unitType, special_move = "", promoted = ""
            overlapping = self.canvas.find_overlapping(x, y, x, y)
            tags = self.canvas.gettags(overlapping[-1])             
            self.move_log.append(Move((r,c),(row,col),tags[0]))
            for ele in self.move_log:
                print(ele)
            self.previous_board.insert(0,copy.deepcopy(self.current_board))
            self.current_board[self.move_log[-1].position[0]][self.move_log[-1].position[1]] = ""
            self.current_board[self.move_log[-1].new_pos[0]][self.move_log[-1].new_pos[1]] = move.unit_type
            if self.move_log[-1].special_move == "promote":
                self.current_board[self.move_log[-1].new_pos[0]][self.move_log[-1].new_pos[1]] = self.move_log[-1].promoted
    def isCheck(self, board=None, player:str =['white','black'], ):

        # player nguoi 
        originalPos = None
        for i in range(8):
            for j in range(8):
                if self.current_board[i][j].find("king") >= 0 and self.current_board[i][j].find(player) >= 0:
                    originalPos=[i,j]
        if player == "black":
            i = 1
            #check diag
            flag =False
            while originalPos[0] - i > 0 and originalPos[1] - i > 0 and not flag:
                if  self.current_board[originalPos[0]-i][originalPos[1]-i] == "white_king" and i==1:
                    flag= True
                    break
                
                if self.current_board[originalPos[0]-i][originalPos[1]-i]  not in ["white_queen","white_bishop"]:
                    flag =False
                    break
                if self.current_board[originalPos[0]-i][originalPos[1]-i] == "white_queen" or self.current_board[originalPos[0]-i][originalPos[1]-i] == "white_bishop":
                    flag= True
                    break
                i+=1
            i = 1
            
            while originalPos[0] - i > 0 and originalPos[1] + i < 8 and not flag:
                if self.current_board[originalPos[0]-i][originalPos[1]+i] == "white_king" and i==1:
                    flag= True
                    break
                
                if self.current_board[originalPos[0]-i][originalPos[1]+i]  not in ["white_queen","white_bishop"]:
                    flag =False
                    break

                if self.current_board[originalPos[0]-i][originalPos[1]+i] == "white_queen" or self.current_board[originalPos[0]-i][originalPos[1]+i] == "white_bishop":
                    flag= True
                    break
                i+=1
            i = 1

            while originalPos[0] + i < 8 and originalPos[1] - i > 0 and not flag:
                if (self.current_board[originalPos[0]+i][originalPos[1]-i] == "white_pawn" or self.current_board[originalPos[0]+i][originalPos[1]-i] == "white_king") and i==1:
                    flag= True
                    break
                if self.current_board[originalPos[0]+i][originalPos[1]-i]  not in ["white_queen","white_bishop"]:
                    flag =False
                    break
                if self.current_board[originalPos[0]+i][originalPos[1]-i] == "white_queen" or self.current_board[originalPos[0]+i][originalPos[1]-i] == "white_bishop":
                    flag= True
                    break
                i+=1
            i = 1

            while originalPos[0] + i < 8 and originalPos[1] + i <8 and not flag:
                if (self.current_board[originalPos[0]+i][originalPos[1]+i] == "white_pawn" or self.current_board[originalPos[0]+i][originalPos[1]+i] == "white_king") and i==1:
                    flag= True
                    break
                if self.current_board[originalPos[0]+i][originalPos[1]+i]  not in ["white_queen","white_bishop"]:
                    flag =False
                    break
                if self.current_board[originalPos[0]+i][originalPos[1]+i] == "white_queen" or self.current_board[originalPos[0]+i][originalPos[1]+i] == "white_bishop":
                    flag= True
                    break
                i+=1
            i = 1
            # check cross:
            while originalPos[1] + i <8 and not flag:
                if self.current_board[originalPos[0]][originalPos[1]+i] == "white_king"  and i==1:
                    flag= True
                    break
                if self.current_board[originalPos[0]][originalPos[1]+i]  not in ["white_queen","white_rook"]:
                    flag =False
                    break
                if self.current_board[originalPos[0]][originalPos[1]+i] == "white_queen" or self.current_board[originalPos[0]][originalPos[1]+i] == "white_rook":
                    flag= True
                    break
                i+=1
            i = 1
            while originalPos[0] + i <8 and not flag:
                if self.current_board[originalPos[0]+i][originalPos[1]] == "white_king"  and i==1:
                    flag= True
                    break
                if self.current_board[originalPos[0]+i][originalPos[1]]  not in ["white_queen","white_rook"]:
                    flag =False
                    break
                if self.current_board[originalPos[0]+i][originalPos[1]] == "white_queen" or self.current_board[originalPos[0]+i][originalPos[1]] == "white_rook":
                    flag= True
                    break
                i+=1
            i = 1
            while originalPos[1] - i >8 and not flag:
                if self.current_board[originalPos[0]][originalPos[1]-i] == "white_king"  and i==1:
                    flag= True
                    break
                if self.current_board[originalPos[0]][originalPos[1]-i]  not in ["white_queen","white_rook"]:
                    flag =False
                    break
                if self.current_board[originalPos[0]][originalPos[1]-i] == "white_queen" or self.current_board[originalPos[0]][originalPos[1]-i] == "white_rook":
                    flag= True
                    break
                i+=1
            i = 1
            while originalPos[0] - i >8 and not flag:
                if self.current_board[originalPos[0]-i][originalPos[1]] == "white_king"  and i==1:
                    flag= True
                    break
                if self.current_board[originalPos[0]-i][originalPos[1]]  not in ["white_queen","white_rook"]:
                    flag =False
                    break
                if self.current_board[originalPos[0]-i][originalPos[1]] == "white_queen" or self.current_board[originalPos[0]-i][originalPos[1]] == "white_rook":
                    flag= True
                    break
                i+=1
            i = 1
            # check knight:
            if not flag:
                moves = [(-1,-2), (-1,2), (1,-2), (1,2), (-2,-1), (-2,1), (2,-1), (2,1)]
                for move in moves:
                    new_row = originalPos[0] + move[0]
                    new_col = originalPos[1] + move[1]
                    if 0 <= new_row < 8 and 0 <= new_col < 8:
                        if self.current_board[new_row][new_col] == 'white_knight':
                            flag =True
            return flag
        if player == "white":
            
            i = 1
            #check diag
            flag =False
            while originalPos[0] - i > 0 and originalPos[1] - i > 0 and not flag:
                
                if (self.current_board[originalPos[0]-i][originalPos[1]-i] == "black_pawn" or self.current_board[originalPos[0]-i][originalPos[1]-i] == "black_king") and i==1:
                    flag= True
                    break
                
                if self.current_board[originalPos[0]-i][originalPos[1]-i]  not in ["black_queen","black_bishop"]:
                    flag =False
                    break
                if self.current_board[originalPos[0]-i][originalPos[1]-i] == "black_queen" or self.current_board[originalPos[0]-i][originalPos[1]-i] == "black_bishop":
                    flag= True
                    break
                i+=1
            i = 1
            
            while originalPos[0] - i > 0 and originalPos[1] + i < 8 and not flag:
                
                if (self.current_board[originalPos[0]-i][originalPos[1]+i] == "black_pawn" or self.current_board[originalPos[0]-i][originalPos[1]+i] == "black_king") and i==1:
                    flag= True
                    break
                
                if self.current_board[originalPos[0]-i][originalPos[1]+i]  not in ["black_queen","black_bishop"]:
                    flag =False
                    break

                if self.current_board[originalPos[0]-i][originalPos[1]+i] == "black_queen" or self.current_board[originalPos[0]-i][originalPos[1]+i] == "black_bishop":
                    flag= True
                    break
                i+=1
            i = 1
            
            while originalPos[0] + i < 8 and originalPos[1] - i > 0 and not flag:
                
                if  self.current_board[originalPos[0]+i][originalPos[1]-i] == "black_king" and i==1:
                    flag= True
                    break
                if self.current_board[originalPos[0]+i][originalPos[1]-i]  not in ["black_queen","black_bishop"]:
                    flag =False
                    break
                if self.current_board[originalPos[0]+i][originalPos[1]-i] == "black_queen" or self.current_board[originalPos[0]+i][originalPos[1]-i] == "black_bishop":
                    flag= True
                    break
                i+=1
            i = 1

            while originalPos[0] + i < 8 and originalPos[1] + i <8 and not flag:
                
                if self.current_board[originalPos[0]+i][originalPos[1]+i] == "black_king" and i==1:
                    flag= True
                    break
                if self.current_board[originalPos[0]+i][originalPos[1]+i]  not in ["black_queen","black_bishop"]:
                    flag =False
                    break
                if self.current_board[originalPos[0]+i][originalPos[1]+i] == "black_queen" or self.current_board[originalPos[0]+i][originalPos[1]+i] == "black_bishop":
                    flag= True
                    break
                i+=1
            i = 1
            # check cross:
            while originalPos[1] + i <8 and not flag:
                
                if self.current_board[originalPos[0]][originalPos[1]+i] == "black_king"  and i==1:
                    flag= True
                    break
                if self.current_board[originalPos[0]][originalPos[1]+i]  not in ["black_queen","black_rook"]:
                    flag =False
                    break
                if self.current_board[originalPos[0]][originalPos[1]+i] == "black_queen" or self.current_board[originalPos[0]][originalPos[1]+i] == "black_rook":
                    flag= True
                    break
                i+=1
            i = 1
            while originalPos[0] + i <8 and not flag:
                
                if self.current_board[originalPos[0]+i][originalPos[1]] == "black_king"  and i==1:
                    flag= True
                    break
                if self.current_board[originalPos[0]+i][originalPos[1]]  not in ["black_queen","black_rook"]:
                    flag =False
                    break
                if self.current_board[originalPos[0]+i][originalPos[1]] == "black_queen" or self.current_board[originalPos[0]+i][originalPos[1]] == "black_rook":
                    flag= True
                    break
                i+=1
            i = 1
            
            while originalPos[1] - i >0 and not flag:
                
                if self.current_board[originalPos[0]][originalPos[1]-i] == "black_king"  and i==1:
                    flag= True
                    break
                if self.current_board[originalPos[0]][originalPos[1]-i]  not in ["black_queen","black_rook"]:
                    flag =False
                    break
                if self.current_board[originalPos[0]][originalPos[1]-i] == "black_queen" or self.current_board[originalPos[0]][originalPos[1]-i] == "black_rook":
                    flag= True
                    break
                i+=1
            i = 1
            while originalPos[0] - i >0 and not flag:
                
                if self.current_board[originalPos[0]-i][originalPos[1]] == "black_king"  and i==1:
                    flag= True
                    break
                if self.current_board[originalPos[0]-i][originalPos[1]]  not in ["black_queen","black_rook"]:
                    flag =False
                    break
                if self.current_board[originalPos[0]-i][originalPos[1]] == "black_queen" or self.current_board[originalPos[0]-i][originalPos[1]] == "black_rook":
                    flag= True
                    break
                i+=1
            i = 1
            # check knight:
            if not flag:
                moves = [(-1,-2), (-1,2), (1,-2), (1,2), (-2,-1), (-2,1), (2,-1), (2,1)]
                for move in moves:
                    new_row = originalPos[0] + move[0]
                    new_col = originalPos[1] + move[1]
                    if 0 <= new_row < 8 and 0 <= new_col < 8:
                        if self.current_board[new_row][new_col] == 'black_knight':
                            flag =True
            return flag
       
    def isCheckMate(self,player:str=['white','black']):
        if not self.isCheck(None, player):
            print("nngoo")
            return False
        moves = self.get_all_possible_moves(player)
        board = self.current_board
        for move in moves:
            unit = board[move.position[0]][move.position[1]]
            board[move.position[0]][move.position[1]] = ""
            board[move.new_pos[0]][move.new_pos[1]] = unit
            if move.special_move == "promote":
                board[move.new_pos[0]][move.new_pos[1]] = move.promoted
            if not self.isCheck(board,player):
                return False
        
        return True


    def is_draw(self,player: str = ['white', 'black']):
        if player =="white":
            res = self.get_all_possible_moves("white")
            return True if len(res) == 0 else False
        if player == "black":
            res = self.get_all_possible_moves("black")
            return True if len(res) == 0 else False



if __name__ == "__main__":
    # game = [
    #     ['black_rook', '', '', '', 'black_king', '', '', 'black_rook'],
    #     ['black_pawn', 'black_pawn', 'black_pawn', '', '', 'black_pawn','black_pawn', 'black_pawn'],
    #     ['', '', '', '', 'black_pawn', 'black_knight', '', ''],
    #     ['', 'black_knight', '', 'black_pawn', '', 'black_bishop', '', ''],
    #     ['', '', '', '', '', 'white_pawn', 'white_pawn', ''], 
    #     ['', '', 'black_queen', 'white_pawn', '', '', '', 'white_pawn'],
    #     ['white_pawn', '', '', 'white_king', 'white_pawn', '', '', 'white_rook'],
    #     ['white_rook', '', '', '', '', 'white_bishop', 'white_knight', '']
    #     ]
    # test checkmate
    game = [
        ['black_rook', '', '', '', 'black_king', '', '', 'black_rook'],
        ['black_pawn', 'black_pawn', 'black_pawn', '', '', 'black_pawn','black_pawn', 'black_pawn'],
        ['', '', '', '', 'black_pawn', 'black_knight', '', ''],
        ['', 'black_knight', '', 'black_pawn', '', 'black_bishop', '', ''],
        ['', '', '', '', '', 'white_pawn', 'white_pawn', ''], 
        ['', '', '', 'white_pawn', '', '', '', 'white_pawn'],
        ['white_pawn', '', '', 'black_queen', 'white_pawn', '', '', 'white_rook'],
        ['white_rook', '', '', 'white_king', '', 'white_bishop', 'white_knight', '']
        ]
    app = ChessBoard(game, 'white')
    for i in app.get_all_possible_moves("white"):
        print(i)
    print(app.isCheckMate(player ="white"))
    app.mainloop()