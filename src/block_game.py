CELL_SIZE = 40
PREVIEW_SIZE = 4
BOARD_WIDTH = 10
BOARD_HEIGHT = 10
PIECE_COLORS = ["red", "blue", "green", "orange"]

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
