import tkinter as tk
import random
import copy

CELL_SIZE = 40
BOARD_WIDTH = 10
BOARD_HEIGHT = 10
PIECE_COLORS = ["red", "blue", "green", "orange"]
PREVIEW_SIZE = 4


def rotate_shape(shape):
    return [(-dy, dx) for dx, dy in shape]

def flip_shape(shape):
    return [(-dx, dy) for dx, dy in shape]

class Piece:
    def __init__(self, shape, color, id):
        self.original_shape = shape
        self.shape = shape.copy()
        self.color = color
        self.id = id

    def rotate(self):
        self.shape = rotate_shape(self.shape)

    def flip(self):
        self.shape = flip_shape(self.shape)

    def reset(self):
        self.shape = self.original_shape.copy()

class Player:
    def __init__(self, name, color, is_computer=False):
        self.name = name
        self.color = color
        self.pieces = self.create_pieces()
        self.is_computer = is_computer
        self.eliminated = False

    def create_pieces(self):
        base_shapes = [
            [(0, 0), (1, 0), (0, 1)],
            [(0, 0), (0, 1), (1, 1)],
            [(0, 0), (1, 0), (1, 1)],
            [(0, 0), (1, 0), (2, 0)],
            [(0, 0), (0, 1), (-1, 1)],
        ]
        pieces = []
        for i in range(2):
            for j, shape in enumerate(base_shapes):
                pieces.append(Piece(shape, self.color, id=i * len(base_shapes) + j))
        return pieces

    def has_pieces(self):
        return len(self.pieces) > 0 and not self.eliminated

class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[None for _ in range(width)] for _ in range(height)]

    def can_place(self, x, y, shape):
        for dx, dy in shape:
            nx, ny = x + dx, y + dy
            if not (0 <= nx < self.width and 0 <= ny < self.height):
                return False
            if self.grid[ny][nx] is not None:
                return False
        return True

    def place_piece(self, x, y, piece, player_name):
        if self.can_place(x, y, piece.shape):
            for dx, dy in piece.shape:
                nx, ny = x + dx, y + dy
                self.grid[ny][nx] = (player_name, piece.color)
            return True
        return False

class GameGUI:
    def __init__(self, root, player_names):
        self.root = root
        self.board = Board(BOARD_WIDTH, BOARD_HEIGHT)
        self.players = [Player(name, PIECE_COLORS[i], is_computer=(name.startswith("CPU"))) for i, name in enumerate(player_names)]
        self.current_turn = 0
        self.selected_piece_index = 0

        self.canvas = tk.Canvas(root, width=CELL_SIZE * BOARD_WIDTH, height=CELL_SIZE * BOARD_HEIGHT)
        self.canvas.grid(row=0, column=0, rowspan=3)
        self.canvas.bind("<Button-1>", self.on_click)

        self.status = tk.Label(root, text="", font=("Arial", 14))
        self.status.grid(row=3, column=0, sticky="w")

        self.controls = tk.Frame(root)
        self.controls.grid(row=0, column=1, sticky="n")

        tk.Button(self.controls, text="回転", command=self.rotate_piece).pack(pady=5)
        tk.Button(self.controls, text="反転", command=self.flip_piece).pack(pady=5)
        tk.Button(self.controls, text="スキップ", command=self.skip_turn).pack(pady=5)

        self.preview_frames = []
        for i, player in enumerate(self.players):
            frame = tk.LabelFrame(self.controls, text=player.name, padx=5, pady=5)
            frame.pack(pady=5)
            canvas = tk.Canvas(frame, width=PREVIEW_SIZE * CELL_SIZE, height=150, bg="white")
            canvas.pack()
            canvas.bind("<Button-1>", lambda e, idx=i: self.on_piece_click(e, idx))
            self.preview_frames.append((frame, canvas))

        self.draw_board()
        self.update_status()
        self.update_piece_list()
        self.root.after(100, self.check_computer_turn)

    def draw_board(self):
        self.canvas.delete("all")
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                x0, y0 = x * CELL_SIZE, y * CELL_SIZE
                x1, y1 = x0 + CELL_SIZE, y0 + CELL_SIZE
                self.canvas.create_rectangle(x0, y0, x1, y1, outline="black")
                cell = self.board.grid[y][x]
                if cell:
                    _, color = cell
                    self.canvas.create_rectangle(x0+4, y0+4, x1-4, y1-4, fill=color)
        self.update_piece_list()

    def update_piece_list(self):
        for i, player in enumerate(self.players):
            canvas = self.preview_frames[i][1]
            canvas.delete("all")
            for idx, piece in enumerate(player.pieces):
                offset_x = 0
                offset_y = idx * (CELL_SIZE * PREVIEW_SIZE // 4)
                for dx, dy in piece.shape:
                    px = offset_x + (dx + 1) * (CELL_SIZE // 2)
                    py = offset_y + (dy + 1) * (CELL_SIZE // 2)
                    canvas.create_rectangle(px, py, px+CELL_SIZE//2, py+CELL_SIZE//2, fill=piece.color, outline="black")
                if i == self.current_turn and idx == self.selected_piece_index:
                    canvas.create_rectangle(offset_x, offset_y, offset_x + PREVIEW_SIZE*CELL_SIZE, offset_y + CELL_SIZE, outline="blue", width=2)

    def on_click(self, event):
        x = event.x // CELL_SIZE
        y = event.y // CELL_SIZE
        self.try_place_piece(x, y)

    def on_piece_click(self, event, player_idx):
        if player_idx == self.current_turn and not self.players[player_idx].eliminated:
            index = event.y // (CELL_SIZE * PREVIEW_SIZE // 4)
            if index < len(self.players[player_idx].pieces):
                self.selected_piece_index = index
                self.draw_board()

    def get_current_piece(self):
        player = self.players[self.current_turn]
        if player.pieces and not player.eliminated:
            return player.pieces[self.selected_piece_index]
        return None

    def try_place_piece(self, x, y):
        player = self.players[self.current_turn]
        if player.eliminated:
            return
        piece = self.get_current_piece()
        if not piece:
            return
        if self.board.place_piece(x, y, piece, player.name):
            player.pieces.pop(self.selected_piece_index)
            self.selected_piece_index = 0
            self.next_turn()
        self.draw_board()
        self.update_status()

    def rotate_piece(self):
        piece = self.get_current_piece()
        if piece:
            piece.rotate()
            self.draw_board()

    def flip_piece(self):
        piece = self.get_current_piece()
        if piece:
            piece.flip()
            self.draw_board()

    def skip_turn(self):
        self.players[self.current_turn].eliminated = True
        self.next_turn()
        self.draw_board()
        self.update_status()

    def next_turn(self):
        for _ in range(len(self.players)):
            self.current_turn = (self.current_turn + 1) % len(self.players)
            if not self.players[self.current_turn].eliminated:
                break
        self.selected_piece_index = 0

    def update_status(self):
        if all(p.eliminated or not p.has_pieces() for p in self.players):
            self.status.config(text="全員のピースが配置されました、または敗北しました。ゲーム終了！")
            self.canvas.unbind("<Button-1>")
        else:
            player = self.players[self.current_turn]
            self.status.config(text=f"{player.name} のターン（残り {len(player.pieces)} ピース）")

    def check_computer_turn(self):
        player = self.players[self.current_turn]
        if player.is_computer and player.has_pieces():
            self.execute_computer_move(player)
        self.root.after(500, self.check_computer_turn)

    def execute_computer_move(self, player):
        for index, piece in enumerate(player.pieces):
            for rotation in range(4):
                for flip in [False, True]:
                    test_piece = copy.deepcopy(piece)
                    for _ in range(rotation):
                        test_piece.rotate()
                    if flip:
                        test_piece.flip()
                    for y in range(BOARD_HEIGHT):
                        for x in range(BOARD_WIDTH):
                            if self.board.can_place(x, y, test_piece.shape):
                                player.pieces[index] = test_piece
                                self.selected_piece_index = index
                                self.try_place_piece(x, y)
                                return
        self.skip_turn()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("ブロック型ボードゲーム - 全員のピース表示付き")
    # game = GameGUI(root, ["Alice", "CPU", "Charlie", "Diana"])
    game = GameGUI(root, ["Alice", "CPU1", "CPU2", "CPU3"])
    root.mainloop()
