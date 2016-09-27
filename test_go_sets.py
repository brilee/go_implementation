import re
import unittest
from go_sets import Position, LibertyTracker, N, NN, WHITE, BLACK, EMPTY

def load_board(string):
    return re.sub(r'[^XO\.]+', '', string)

EMPTY_ROW = EMPTY * 19

class TestLibertyTracker(unittest.TestCase):
    def test_lib_tracker_init(self):
        board = load_board(BLACK + EMPTY*18 + EMPTY_ROW * 18)

        libtracker = LibertyTracker.from_board(board)
        self.assertEqual(len(libtracker.groups), 1)
        self.assertNotEqual(libtracker.group_index[0], None)
        self.assertEqual(libtracker.get_liberties(), [2] + [0] * (NN - 1))
        sole_group = libtracker.groups[libtracker.group_index[0]]
        self.assertEqual(sole_group.stones, {0})
        self.assertEqual(sole_group.liberties, {1, N})
        self.assertEqual(sole_group.color, BLACK)

    def test_place_stone(self):
        board = load_board(BLACK + EMPTY * 18 + EMPTY_ROW * 18)
        libtracker = LibertyTracker.from_board(board)
        new_lib_tracker, _ = libtracker.add_stone(BLACK, 1)
        self.assertEqual(len(new_lib_tracker.groups), 1)
        self.assertNotEqual(new_lib_tracker.group_index[0], None)
        self.assertEqual(new_lib_tracker.get_liberties(), [3, 3] + [0] * (NN - 2))
        sole_group = new_lib_tracker.groups[new_lib_tracker.group_index[0]]
        self.assertEqual(sole_group.stones, {0, 1})
        self.assertEqual(sole_group.liberties, {2, N, N+1})
        self.assertEqual(sole_group.color, BLACK)

    def test_place_stone_opposite_color(self):
        board = load_board(BLACK + EMPTY * 18 + EMPTY_ROW * 18)
        libtracker = LibertyTracker.from_board(board)
        new_lib_tracker, _ = libtracker.add_stone(WHITE, 1)
        self.assertEqual(len(new_lib_tracker.groups), 2)
        self.assertNotEqual(new_lib_tracker.group_index[0], None)
        self.assertNotEqual(new_lib_tracker.group_index[1], None)
        self.assertEqual(new_lib_tracker.get_liberties(), [1, 2] + [0] * (NN - 2))
        black_group = new_lib_tracker.groups[new_lib_tracker.group_index[0]]
        white_group = new_lib_tracker.groups[new_lib_tracker.group_index[1]]
        self.assertEqual(black_group.stones, {0})
        self.assertEqual(black_group.liberties, {N})
        self.assertEqual(black_group.color, BLACK)
        self.assertEqual(white_group.stones, {1})
        self.assertEqual(white_group.liberties, {2, N+1})
        self.assertEqual(white_group.color, WHITE)

    def test_merge_multiple_groups(self):
        board = load_board('''
        .X.................
        X.X................
        .X.................
        ''' + EMPTY_ROW * 16)
        libtracker = LibertyTracker.from_board(board)
        new_lib_tracker, _ = libtracker.add_stone(BLACK, N+1)
        self.assertEqual(len(new_lib_tracker.groups), 1)
        self.assertNotEqual(new_lib_tracker.group_index[N+1], None)
        sole_group = new_lib_tracker.groups[new_lib_tracker.group_index[N+1]]
        self.assertEqual(sole_group.stones, {1, N, N+1, N+2, 2*N+1})
        self.assertEqual(sole_group.liberties, {0, 2, N+3, 2*N, 2*N+2, 3*N+1})
        self.assertEqual(sole_group.color, BLACK)

        new_lib_cache = new_lib_tracker.get_liberties()
        for stone in sole_group.stones:
            self.assertEqual(new_lib_cache[stone], 6)

    def test_capture_stone(self):
        board = load_board('''
        .X.................
        XO.................
        .X.................
        ''' + EMPTY_ROW * 16)
        libtracker = LibertyTracker.from_board(board)
        new_lib_tracker, captured = libtracker.add_stone(BLACK, N+2)
        self.assertEqual(len(new_lib_tracker.groups), 4)
        self.assertEqual(new_lib_tracker.group_index[N+1], None)
        self.assertEqual(captured, {N+1})

    def test_capture_many(self):
        board = load_board('''
        .XX................
        XOO................
        .XX................
        ''' + EMPTY_ROW * 16)
        libtracker = LibertyTracker.from_board(board)
        new_lib_tracker, captured = libtracker.add_stone(BLACK, N+3)
        self.assertEqual(len(new_lib_tracker.groups), 4)
        self.assertEqual(new_lib_tracker.group_index[N+1], None)
        self.assertEqual(captured, {N+1, N+2})

        left_group = new_lib_tracker.groups[new_lib_tracker.group_index[N]]
        self.assertEqual(left_group.stones, {N})
        self.assertEqual(left_group.liberties, {0, N+1, 2*N})

        right_group = new_lib_tracker.groups[new_lib_tracker.group_index[N+3]]
        self.assertEqual(right_group.stones, {N+3})
        self.assertEqual(right_group.liberties, {3, N+2, N+4, 2*N+3})

        top_group = new_lib_tracker.groups[new_lib_tracker.group_index[1]]
        self.assertEqual(top_group.stones, {1, 2})
        self.assertEqual(top_group.liberties, {0, 3, N+1, N+2})

        bottom_group = new_lib_tracker.groups[new_lib_tracker.group_index[2*N+1]]
        self.assertEqual(bottom_group.stones, {2*N+1, 2*N+2})
        self.assertEqual(bottom_group.liberties, {N+1, N+2, 2*N, 2*N+3, 3*N+1, 3*N+2})

        new_lib_cache = new_lib_tracker.get_liberties()
        for stone in top_group.stones:
            self.assertEqual(new_lib_cache[stone], 4)
        for stone in left_group.stones:
            self.assertEqual(new_lib_cache[stone], 3)
        for stone in right_group.stones:
            self.assertEqual(new_lib_cache[stone], 4)
        for stone in bottom_group.stones:
            self.assertEqual(new_lib_cache[stone], 6)
        for stone in captured:
            self.assertEqual(new_lib_cache[stone], 0)

    def test_capture_multiple_groups(self):
        board = load_board('''
        .OX................
        OXX................
        XX.................
        ''' + EMPTY_ROW * 16)
        libtracker = LibertyTracker.from_board(board)
        new_lib_tracker, captured = libtracker.add_stone(BLACK, 0)
        self.assertEqual(len(new_lib_tracker.groups), 2)
        self.assertEqual(captured, {1, N})

        corner_stone = new_lib_tracker.groups[new_lib_tracker.group_index[0]]
        self.assertEqual(corner_stone.stones, {0})
        self.assertEqual(corner_stone.liberties, {1, N})

        surrounding_stones = new_lib_tracker.groups[new_lib_tracker.group_index[2]]
        self.assertEqual(surrounding_stones.stones, {2, N+1, N+2, 2*N, 2*N+1})
        self.assertEqual(surrounding_stones.liberties, {1, 3, N, N+3, 2*N+2, 3*N, 3*N+1})

        new_lib_cache = new_lib_tracker.get_liberties()
        for stone in corner_stone.stones:
            self.assertEqual(new_lib_cache[stone], 2)
        for stone in surrounding_stones.stones:
            self.assertEqual(new_lib_cache[stone], 7)


    def test_same_friendly_group_neighboring_twice(self):
        board = load_board('''
        XX.................
        X..................
        ''' + EMPTY_ROW * 17)

        libtracker = LibertyTracker.from_board(board)
        new_lib_tracker, captured = libtracker.add_stone(BLACK, N+1)
        self.assertEqual(len(new_lib_tracker.groups), 1)
        sole_group_id = new_lib_tracker.group_index[0]
        sole_group = new_lib_tracker.groups[sole_group_id]
        self.assertEqual(sole_group.stones, {0, 1, N, N+1})
        self.assertEqual(sole_group.liberties, {2, N+2, 2*N, 2*N+1})
        self.assertEqual(captured, set())

    def test_same_opponent_group_neighboring_twice(self):
        board = load_board('''
        XX.................
        X..................
        ''' + EMPTY_ROW * 17)

        libtracker = LibertyTracker.from_board(board)
        new_lib_tracker, captured = libtracker.add_stone(WHITE, N+1)
        self.assertEqual(len(new_lib_tracker.groups), 2)
        black_group = new_lib_tracker.groups[new_lib_tracker.group_index[0]]
        self.assertEqual(black_group.stones, {0, 1, N})
        self.assertEqual(black_group.liberties, {2, 2*N})

        white_group = new_lib_tracker.groups[new_lib_tracker.group_index[N+1]]
        self.assertEqual(white_group.stones, {N+1})
        self.assertEqual(white_group.liberties, {N+2, 2*N+1})

        self.assertEqual(captured, set())


class TestPosition(unittest.TestCase):
    def test_capture_and_play(self):
        board = load_board('''
        OX.................
        ''' + EMPTY_ROW * 18)
        position = Position(board, None, LibertyTracker.from_board(board))

        captured_position = position.play_move(N, BLACK)
        captured_board = load_board('''
        .X.................
        X..................
        ''' + EMPTY_ROW * 17)
        self.assertEqual(captured_position.board, captured_board)

        filled_in_position = captured_position.play_move(0, BLACK)
        filled_in_board = load_board('''
        XX.................
        X..................
        ''' + EMPTY_ROW * 17)
        self.assertEqual(filled_in_position.board, filled_in_board)



if __name__ == '__main__':
    unittest.main()