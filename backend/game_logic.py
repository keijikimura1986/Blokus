import copy
from block_game import Player, Board, rotate_shape, flip_shape

class GameLogic:
    def __init__(self, player_names, colors, width=10, height=10):
        self.board = Board(width, height)
        self.players = [Player(name, colors[i], is_computer=("CPU" in name)) for i, name in enumerate(player_names)]
        self.current_turn = 0
        self.selected_piece_index = 0

    def get_current_player(self):
        return self.players[self.current_turn]

    def get_current_piece(self):
        player = self.get_current_player()
        if player.has_pieces():
            return player.pieces[self.selected_piece_index]
        return None

    def rotate_current_piece(self):
        piece = self.get_current_piece()
        if piece:
            piece.rotate()

    def flip_current_piece(self):
        piece = self.get_current_piece()
        if piece:
            piece.flip()

    def place_piece(self, x, y):
        player = self.get_current_player()
        piece = self.get_current_piece()
        if piece and self.board.place_piece(x, y, piece, player.name):
            player.pieces.pop(self.selected_piece_index)
            self.selected_piece_index = 0
            self.advance_turn()
            return True
        return False

    def skip_turn(self):
        self.players[self.current_turn].eliminated = True
        self.advance_turn()

    def advance_turn(self):
        for _ in range(len(self.players)):
            self.current_turn = (self.current_turn + 1) % len(self.players)
            if not self.players[self.current_turn].eliminated:
                break
        self.selected_piece_index = 0

    def is_game_over(self):
        return all(p.eliminated or not p.has_pieces() for p in self.players)

    def get_game_status(self):
        if self.is_game_over():
            return "ゲーム終了！"
        p = self.get_current_player()
        return f"{p.name} のターン（残り {len(p.pieces)} ピース）"

    def compute_computer_move(self):
        player = self.get_current_player()
        if not player.is_computer or player.eliminated:
            return
        for index, piece in enumerate(player.pieces):
            for r in range(4):
                for f in [False, True]:
                    test_piece = copy.deepcopy(piece)
                    for _ in range(r):
                        test_piece.rotate()
                    if f:
                        test_piece.flip()
                    for y in range(self.board.height):
                        for x in range(self.board.width):
                            if self.board.can_place(x, y, test_piece.shape):
                                player.pieces[index] = test_piece
                                self.selected_piece_index = index
                                self.place_piece(x, y)
                                return
        self.skip_turn()
