import tkinter as tk
from game_logic import GameLogic
from block_game import CELL_SIZE, PREVIEW_SIZE, PIECE_COLORS, BOARD_WIDTH, BOARD_HEIGHT

class GameGUI:
    def __init__(self, root, player_names):
        self.root = root
        self.logic = GameLogic(player_names, PIECE_COLORS, BOARD_WIDTH, BOARD_HEIGHT)

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
        for i, player in enumerate(self.logic.players):
            frame = tk.LabelFrame(self.controls, text=player.name, padx=5, pady=5)
            frame.pack(pady=5)
            canvas = tk.Canvas(frame, width=PREVIEW_SIZE * CELL_SIZE, height=150, bg="white")
            canvas.pack()
            canvas.bind("<Button-1>", lambda e, idx=i: self.on_piece_click(e, idx))
            self.preview_frames.append((frame, canvas))

        self.draw_board()
        self.update_status()
        self.root.after(100, self.check_computer_turn)

    def draw_board(self):
        self.canvas.delete("all")
        for y in range(self.logic.board.height):
            for x in range(self.logic.board.width):
                x0, y0 = x * CELL_SIZE, y * CELL_SIZE
                x1, y1 = x0 + CELL_SIZE, y0 + CELL_SIZE
                self.canvas.create_rectangle(x0, y0, x1, y1, outline="black")
                cell = self.logic.board.grid[y][x]
                if cell:
                    _, color = cell
                    self.canvas.create_rectangle(x0+4, y0+4, x1-4, y1-4, fill=color)
        self.update_piece_list()

    def update_piece_list(self):
        for i, player in enumerate(self.logic.players):
            canvas = self.preview_frames[i][1]
            canvas.delete("all")
            for idx, piece in enumerate(player.pieces):
                offset_x = 0
                offset_y = idx * (CELL_SIZE * PREVIEW_SIZE // 4)
                for dx, dy in piece.shape:
                    px = offset_x + (dx + 1) * (CELL_SIZE // 2)
                    py = offset_y + (dy + 1) * (CELL_SIZE // 2)
                    canvas.create_rectangle(px, py, px+CELL_SIZE//2, py+CELL_SIZE//2, fill=piece.color, outline="black")
                if i == self.logic.current_turn and idx == self.logic.selected_piece_index:
                    canvas.create_rectangle(offset_x, offset_y, offset_x + PREVIEW_SIZE*CELL_SIZE, offset_y + CELL_SIZE, outline="blue", width=2)

    def on_click(self, event):
        x = event.x // CELL_SIZE
        y = event.y // CELL_SIZE
        self.logic.place_piece(x, y)
        self.draw_board()
        self.update_status()

    def on_piece_click(self, event, player_idx):
        if player_idx == self.logic.current_turn and not self.logic.players[player_idx].eliminated:
            index = event.y // (CELL_SIZE * PREVIEW_SIZE // 4)
            if index < len(self.logic.players[player_idx].pieces):
                self.logic.selected_piece_index = index
                self.draw_board()

    def rotate_piece(self):
        self.logic.rotate_current_piece()
        self.draw_board()

    def flip_piece(self):
        self.logic.flip_current_piece()
        self.draw_board()

    def skip_turn(self):
        self.logic.skip_turn()
        self.draw_board()
        self.update_status()

    def update_status(self):
        status = self.logic.get_game_status()
        self.status.config(text=status)
        if "終了" in status:
            self.canvas.unbind("<Button-1>")

    def check_computer_turn(self):
        self.logic.compute_computer_move()
        self.draw_board()
        self.update_status()
        self.root.after(500, self.check_computer_turn)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("ブロック型ボードゲーム - リファクタ済み")
    game = GameGUI(root, ["Alice", "CPU", "Charlie", "Diana"])
    root.mainloop()
