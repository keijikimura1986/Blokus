import unittest
from copy import deepcopy

from main7 import Piece, Player, Board, rotate_shape, flip_shape


class TestBlockGame(unittest.TestCase):

    def setUp(self):
        self.board = Board(10, 10)
        self.player = Player("TestPlayer", "red")

    def test_piece_rotation(self):
        shape = [(0, 0), (1, 0)]
        rotated = rotate_shape(shape)
        self.assertEqual(rotated, [(0, 0), (0, 1)])

    def test_piece_flip(self):
        shape = [(0, 0), (1, 0)]
        flipped = flip_shape(shape)
        self.assertEqual(flipped, [(0, 0), (-1, 0)])

    def test_board_can_place_valid(self):
        shape = [(0, 0), (1, 0)]
        self.assertTrue(self.board.can_place(0, 0, shape))

    def test_board_can_place_out_of_bounds(self):
        shape = [(0, 0), (1, 0)]
        self.assertFalse(self.board.can_place(9, 0, shape))  # はみ出す

    def test_board_place_piece(self):
        piece = self.player.pieces[0]
        success = self.board.place_piece(0, 0, piece, self.player.name)
        self.assertTrue(success)
        self.assertIsNotNone(self.board.grid[0][0])

    def test_board_prevent_overlap(self):
        piece = self.player.pieces[0]
        self.board.place_piece(0, 0, piece, self.player.name)
        overlap = self.board.place_piece(0, 0, piece, self.player.name)
        self.assertFalse(overlap)

    def test_player_elimination(self):
        self.player.eliminated = True
        self.assertFalse(self.player.has_pieces())

    def test_player_has_pieces(self):
        self.assertTrue(self.player.has_pieces())
        self.player.pieces = []
        self.assertFalse(self.player.has_pieces())

if __name__ == "__main__":
    unittest.main()
