import unittest
from block_game import Player, Board, rotate_shape, flip_shape, PIECE_COLORS
from game_logic import GameLogic

class TestGameLogic(unittest.TestCase):
    def setUp(self):
        self.logic = GameLogic(["Player1", "Player2"], PIECE_COLORS, width=5, height=5)

    def test_initial_player(self):
        player = self.logic.get_current_player()
        self.assertEqual(player.name, "Player1")

    def test_rotation_and_flip(self):
        original_shape = self.logic.get_current_piece().shape.copy()
        self.logic.rotate_current_piece()
        self.assertNotEqual(self.logic.get_current_piece().shape, original_shape)
        self.logic.flip_current_piece()
        self.assertNotEqual(self.logic.get_current_piece().shape, original_shape)

    def test_place_piece_success(self):
        success = self.logic.place_piece(0, 0)
        self.assertTrue(success)
        self.assertEqual(self.logic.current_turn, 1)  # next player's turn

    def test_place_piece_failure_then_retry(self):
        self.logic.place_piece(0, 0)
        # Try placing again on the same occupied position
        success = self.logic.place_piece(0, 0)
        self.assertFalse(success)

    def test_skip_turn_marks_eliminated(self):
        self.logic.skip_turn()
        self.assertTrue(self.logic.players[0].eliminated)
        self.assertEqual(self.logic.current_turn, 1)

    def test_game_over_condition(self):
        for p in self.logic.players:
            p.eliminated = True
        self.assertTrue(self.logic.is_game_over())

    def test_get_game_status(self):
        status = self.logic.get_game_status()
        self.assertIn("Player1", status)

    def test_computer_auto_move(self):
        logic = GameLogic(["CPU", "Player"], PIECE_COLORS, width=5, height=5)
        logic.compute_computer_move()
        self.assertIn(logic.current_turn, [0, 1])  # CPU may place or skip

if __name__ == '__main__':
    unittest.main()
