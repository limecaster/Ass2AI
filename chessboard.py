import tkinter as tk
from PIL import Image, ImageTk

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
        self.piece_images = self.load_piece_images()
        self.draw_pieces()
        
        self.drag_data = {"piece": None, "x": 0, "y": 0}
        self.canvas.bind("<Button-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.drag)
        self.canvas.bind("<ButtonRelease-1>", self.drop)
        
        self.current_board = current_board
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
        for row in range(self.rows):
            for col in range(self.columns):
                piece = starting_board[row][col]
                if piece != '':
                    piece_image = self.piece_images[piece]
                    self.canvas.create_image(col * self.size + self.size/2, row * self.size + self.size/2,
                                             image=piece_image)
    
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
            square_size = 50
            row = y // square_size
            col = x // square_size
            new_x = col * square_size + square_size // 2
            new_y = row * square_size + square_size // 2
            self.canvas.coords(self.drag_data["piece"], new_x - 25, new_y - 25)
            self.drag_data["piece"] = None
    
    def get_all_possible_moves(self):
        pass

if __name__ == "__main__":
    app = ChessBoard()
    app.mainloop()