import itertools
N = 19
NN = N ** 2
WHITE, BLACK, EMPTY = ord('O'), ord('X'), ord('.')

def swap_colors(color):
    if color == BLACK:
        return WHITE
    elif color == WHITE:
        return BLACK
    else:
        return color

EMPTY_BOARD = bytearray(chr(EMPTY) * NN, encoding='ascii')

def flatten(c):
    return N * c[0] + c[1]

# Convention: coords that have been flattened have a "f" prefix
def unflatten(fc):
    return divmod(fc, N)

def is_on_board(c):
    return c[0] % N == c[0] and c[1] % N == c[1]

def get_valid_neighbors(fc):
    x, y = unflatten(fc)
    possible_neighbors = ((x+1, y), (x-1, y), (x, y+1), (x, y-1))
    return [flatten(n) for n in possible_neighbors if is_on_board(n)]

# Neighbors are indexed by flat coordinates
NEIGHBORS = [get_valid_neighbors(fc) for fc in range(NN)]

def unpack_bools(bool_array):
    return list(itertools.compress(range(NN), bool_array))

def find_reached(board, fc):
    color = board[fc]
    chain = bytearray(NN); chain[fc] = 1
    reached = bytearray(NN)
    frontier = [fc]
    while frontier:
        current_fc = frontier.pop()
        chain[current_fc] = 1
        for fn in NEIGHBORS[current_fc]:
            if board[fn] == color and not chain[fn]:
                frontier.append(fn)
            elif board[fn] != color:
                reached[fn] = 1
    return unpack_bools(chain), unpack_bools(reached)

class IllegalMove(Exception): pass

def bulk_place_stones(color, board, stones):
    for fstone in stones:
        board[fstone] = color

def maybe_capture_stones(board, fc):
    chain, reached = find_reached(board, fc)
    if not any(board[fr] == EMPTY for fr in reached):
        bulk_place_stones(EMPTY, board, chain)
        return chain
    else:
        return []

def play_move_incomplete(board, fc, color):
    if board[fc] != EMPTY:
        raise IllegalMove
    board[fc] = color

    opp_color = swap_colors(color)
    opp_stones = []
    my_stones = []
    for fn in NEIGHBORS[fc]:
        if board[fn] == color:
            my_stones.append(fn)
        elif board[fn] == opp_color:
            opp_stones.append(fn)

    for fs in opp_stones:
        maybe_capture_stones(board, fs)

    for fs in my_stones:
        maybe_capture_stones(board, fs)

    return board


def is_koish(board, fc):
    'Check if fc is surrounded on all sides by 1 color, and return that color'
    if board[fc] != EMPTY: return None
    neighbor_colors = {board[fn] for fn in NEIGHBORS[fc]}
    if len(neighbor_colors) == 1 and not EMPTY in neighbor_colors:
        return list(neighbor_colors)[0]
    else:
        return None

class Position():
    def __init__(self, board, ko):
        self.board = board
        self.ko = ko

    @staticmethod
    def initial_state():
        return Position(board=EMPTY_BOARD[:], ko=None)

    def get_board(self):
        return self.board.decode('ascii')

    def __str__(self):
        import textwrap
        return '\n'.join(textwrap.wrap(self.get_board(), N))
    
    def play_move(self, fc, color):
        color = ord(color)
        board, ko = self.board, self.ko

        if fc == ko or board[fc] != EMPTY:
            raise IllegalMove

        board[fc] = color

        opp_color = swap_colors(color)
        opp_stones = []
        my_stones = []
        for fn in NEIGHBORS[fc]:
            if board[fn] == color:
                my_stones.append(fn)
            elif board[fn] == opp_color:
                opp_stones.append(fn)

        opp_captured = 0
        for fs in opp_stones:
            captured = maybe_capture_stones(board, fs)
            opp_captured += len(captured)

        for fs in my_stones:
            captured = maybe_capture_stones(board, fs)

        if opp_captured == 1 and is_koish(board, fc) == opp_color:
            new_ko = fc
        else:
            new_ko = None

        return Position(board, new_ko)

    def score(self):
        board = self.board[:] # copy board so we don't mutate it
        while EMPTY in board:
            fempty = board.index(EMPTY)
            empties, borders = find_reached(board, fempty)
            possible_border_color = board[borders[0]]
            if all(board[fb] == possible_border_color for fb in borders):
                bulk_place_stones(possible_border_color, board, empties)
            else:
                # if an empty intersection reaches both white and black,
                # then it belongs to neither player. 
                bulk_place_stones(ord('?'), board, empties)
        return board.count(BLACK) - board.count(WHITE)

    def get_liberties(self):
        board = self.board[:]
        liberties = bytearray(NN)
        for color in (WHITE, BLACK):
            while color in board:
                fc = board.index(color)
                stones, borders = find_reached(board, fc)
                num_libs = len([fb for fb in borders if board[fb] == EMPTY])
                for fs in stones:
                    liberties[fs] = num_libs
                bulk_place_stones(ord('?'), board, stones)
        return list(liberties)
