import tkinter as tk
from PIL import Image, ImageTk

class GiveAwayChess(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Give-Away Chess")
        self.geometry("400x400")
        
        self.board = tk.Canvas(self, width=400, height=400)
        self.board.pack()
        
        self.piece_images = {}
        self.load_all_piece_images()

        self.draw_board()
        self.draw_pieces()
        
        self.drag_data = {"piece": None, "x": 0, "y": 0}
        
        self.board.bind("<Button-1>", self.start_drag)
        self.board.bind("<B1-Motion>", self.drag)
        self.board.bind("<ButtonRelease-1>", self.drop)
    
    def draw_board(self):
        dark_color = "#769656"
        light_color = "#eeeed2"
        square_size = 50
        
        for row in range(8):
            for col in range(8):
                x1 = col * square_size
                y1 = row * square_size
                x2 = x1 + square_size
                y2 = y1 + square_size
                
                color = dark_color if (row + col) % 2 == 0 else light_color
                self.board.create_rectangle(x1, y1, x2, y2, fill=color)
    
    def load_all_piece_images(self):
        piece_names = ["white_pawn", "white_rook", "white_knight", "white_bishop", "white_queen", "white_king",
                       "black_pawn", "black_rook", "black_knight", "black_bishop", "black_queen", "black_king"]
        for piece_name in piece_names:
            image_path = f"images/{piece_name}.png"
            self.piece_images[piece_name] = self.load_png_image(image_path, 50, 50)

    def draw_pieces(self):
        piece_size = 50
        piece_positions = {
            "black_pawn": [(0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1)],
            "black_rook": [(0, 0), (7, 0)],
            "black_knight": [(1, 0), (6, 0)],
            "black_bishop": [(2, 0), (5, 0)],
            "black_queen": [(3, 0)],
            "black_king": [(4, 0)],
            "white_pawn": [(0, 6), (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6)],
            "white_rook": [(0, 7), (7, 7)],
            "white_knight": [(1, 7), (6, 7)],
            "white_bishop": [(2, 7), (5, 7)],
            "white_queen": [(3, 7)],
            "white_king": [(4, 7)]
        }
        
        for piece, positions in piece_positions.items():
            for pos in positions:
                x = pos[0] * piece_size
                y = pos[1] * piece_size
                self.board.create_image(x, y, image=self.piece_images[piece], anchor='nw', tags=(piece, "piece"))
        
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
      
    def start_drag(self, event):
        x, y = event.x, event.y
        overlapping = self.board.find_overlapping(x, y, x, y)
        if overlapping:
            tags = self.board.gettags(overlapping[-1])
            print(tags)
            if "piece" in tags:
                self.drag_data["piece"] = overlapping[-1]
                self.drag_data["x"] = x
                self.drag_data["y"] = y
    
    def drag(self, event):
        if self.drag_data["piece"]:
            dx = event.x - self.drag_data["x"]
            dy = event.y - self.drag_data["y"]
            self.board.move(self.drag_data["piece"], dx, dy)
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y
    
    def drop(self, event):
        if self.drag_data["piece"]:
            x, y = event.x, event.y
            square_size = 50
            row = y // square_size
            col = x // square_size
            new_x = col * square_size + square_size // 2
            new_y = row * square_size + square_size // 2
            self.board.coords(self.drag_data["piece"], new_x - 25, new_y - 25)
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

    def is_valid_move(self, piece, start_row, start_col, end_row, end_col):
        piece_tags = self.board.gettags(piece)
        piece_type = piece_tags[0]
        if not self.is_capture_move(piece, start_row, start_col, end_row, end_col):
            return False
        if piece_type in ("white_pawn", "black_pawn"):
            return self.is_valid_pawn_move(piece_type, start_row, start_col, end_row, end_col)
        elif piece_type in ("white_rook", "black_rook"):
            return self.is_valid_rook_move(start_row, start_col, end_row, end_col)
        elif piece_type in ("white_knight", "black_knight"):
            return self.is_valid_knight_move(start_row, start_col, end_row, end_col)
        elif piece_type in ("white_bishop", "black_bishop"):
            return self.is_valid_bishop_move(start_row, start_col, end_row, end_col)
        elif piece_type in ("white_queen", "black_queen"):
            return self.is_valid_queen_move(start_row, start_col, end_row, end_col)
        elif piece_type in ("white_king", "black_king"):
            return self.is_valid_king_move(start_row, start_col, end_row, end_col)
        else:
            return False

    def is_capture_move(self, piece, start_row, start_col, end_row, end_col):
        end_piece = self.get_piece_at_position(end_row, end_col)
        if end_piece:
            piece_tags = self.board.gettags(piece)
            end_piece_tags = self.board.gettags(end_piece)
            if piece_tags[0] != end_piece_tags[0]:
                return True
        return False

    def is_valid_pawn_move(self, piece_type, start_row, start_col, end_row, end_col):
        # Add logic for pawn movement validation here
        pass
    
    def is_valid_rook_move(self, start_row, start_col, end_row, end_col):
        # Add logic for rook movement validation here
        pass
    
    def is_valid_knight_move(self, start_row, start_col, end_row, end_col):
        # Add logic for knight movement validation here
        pass
    
    def is_valid_bishop_move(self, start_row, start_col, end_row, end_col):
        # Add logic for bishop movement validation here
        pass
    
    def is_valid_queen_move(self, start_row, start_col, end_row, end_col):
        # Add logic for queen movement validation here
        pass
    
    def is_valid_king_move(self, start_row, start_col, end_row, end_col):
        # Add logic for king movement validation here
        pass

if __name__ == "__main__":
    app = GiveAwayChess()
    app.mainloop()
