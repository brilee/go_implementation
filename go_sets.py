import copy
from collections import namedtuple
N = 19
NN = N ** 2
WHITE, BLACK, EMPTY = 'O', 'X', '.'

def swap_colors(color):
    if color == BLACK:
        return WHITE
    elif color == WHITE:
        return BLACK
    else:
        return color

EMPTY_BOARD = EMPTY * NN

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

def find_reached(board, fc):
    color = board[fc]
    chain = set([fc])
    reached = set()
    frontier = [fc]
    while frontier:
        current_fc = frontier.pop()
        chain.add(current_fc)
        for fn in NEIGHBORS[current_fc]:
            if board[fn] == color and not fn in chain:
                frontier.append(fn)
            elif board[fn] != color:
                reached.add(fn)
    return chain, reached

class IllegalMove(Exception): pass

def place_stone(color, board, fc):
    return board[:fc] + color + board[fc+1:]

def bulk_place_stones(color, board, stones):
    byteboard = bytearray(board, encoding='ascii') # create mutable version of board
    color = ord(color)
    for fstone in stones:
        byteboard[fstone] = color
    return byteboard.decode('ascii') # and cast back to string when done

def maybe_capture_stones(board, fc):
    chain, reached = find_reached(board, fc)
    if not any(board[fr] == EMPTY for fr in reached):
        board = bulk_place_stones(EMPTY, board, chain)
        return board, chain
    else:
        return board, []

class Group(namedtuple('Group', ['id', 'stones', 'liberties', 'color'])):
    '''
    stones: a set of Coordinates belonging to this group
    liberties: a set of Coordinates that are empty and adjacent to this group.
    color: color of this group
    '''
    pass

class LibertyTracker():
    @staticmethod
    def from_board(board):
        curr_group_id = 0
        lib_tracker = LibertyTracker([None] * NN, {})
        for color in (WHITE, BLACK):
            while color in board:
                curr_group_id += 1
                coord = board.index(color)
                chain, reached = find_reached(board, coord)
                liberties = set(fr for fr in reached if board[fr] == EMPTY)
                new_group = Group(curr_group_id, chain, liberties, color)
                lib_tracker.groups[curr_group_id] = new_group
                for fs in chain:
                    lib_tracker.group_index[fs] = curr_group_id
                board = bulk_place_stones('?', board, chain)

        lib_tracker.max_group_id = curr_group_id

        liberty_counts = [0] * NN
        for group in lib_tracker.groups.values():
            num_libs = len(group.liberties)
            for fs in group.stones:
                liberty_counts[fs] = num_libs
        lib_tracker.liberty_cache = liberty_counts

        return lib_tracker

    def __init__(self, group_index, groups, liberty_cache=None, max_group_id=1):
        # group_index: a NN-length array of None/group_ids
        # groups: a dict of group_id to groups
        self.group_index = group_index
        self.groups = groups
        if liberty_cache is not None:
            self.liberty_cache = liberty_cache
        else:
            self.liberty_cache = [0]*NN
        self.max_group_id = max_group_id

    def __deepcopy__(self, memodict={}):
        new_group_index = self.group_index[:]
        new_lib_cache = self.liberty_cache[:]
        new_groups = {
            group.id: Group(group.id, set(group.stones), set(group.liberties), group.color)
            for group in self.groups.values()
        }
        return LibertyTracker(new_group_index, new_groups, liberty_cache=new_lib_cache, max_group_id=self.max_group_id)

    def get_liberties(self):
        return self.liberty_cache

    def add_stone(self, color, fc):
        new_lib_tracker = copy.deepcopy(self)
        captured_stones = new_lib_tracker._add_stone(color, fc)
        return new_lib_tracker, captured_stones

    def _add_stone(self, color, fc):
        assert self.group_index[fc] == None
        captured_stones = set()
        opponent_neighboring_group_ids = set()
        friendly_neighboring_group_ids = set()
        empty_neighbors = set()

        new_group = self._create_group(color, fc)


        for fn in NEIGHBORS[fc]:
            neighbor_group_id = self.group_index[fn]
            if neighbor_group_id is not None:
                neighbor_group = self.groups[neighbor_group_id]
                if neighbor_group.color == color:
                    friendly_neighboring_group_ids.add(neighbor_group_id)
                elif neighbor_group.color == swap_colors(color):
                    opponent_neighboring_group_ids.add(neighbor_group_id)
            else:
                empty_neighbors.add(fn)

        # initialize liberties for the newly created group
        self._update_liberties(new_group.id, add=empty_neighbors)

        for group_id in friendly_neighboring_group_ids:
            new_group = self._merge_groups(group_id, new_group.id)

        for group_id in opponent_neighboring_group_ids:
            neighbor_group = self.groups[group_id]
            if len(neighbor_group.liberties) == 1:
                captured = self._remove_group(group_id)
                captured_stones.update(captured)
            else:
                self._update_liberties(group_id, remove={fc})

        self._add_liberties(captured_stones)

        return captured_stones

    def _create_group(self, color, fc):
        self.max_group_id += 1
        new_group = Group(self.max_group_id, set([fc]), set(), color)
        self.groups[new_group.id] = new_group
        self.group_index[fc] = new_group.id
        return new_group

    def _merge_groups(self, group1_id, group2_id):
        group1 = self.groups[group1_id]
        group2 = self.groups[group2_id]
        group1.stones.update(group2.stones)
        self._update_liberties(group1_id, add=group2.liberties, remove=(group2.stones | group1.stones))
        del self.groups[group2_id]
        for fs in group2.stones:
            self.group_index[fs] = group1_id

        return group1

    def _remove_group(self, group_id):
        dead_group = self.groups[group_id]
        for fs in dead_group.stones:
            self.group_index[fs] = None
            self.liberty_cache[fs] = 0
        del self.groups[group_id]
        return dead_group.stones

    def _update_liberties(self, group_id, add=None, remove=None):
        group = self.groups[group_id]
        if add:
            group.liberties.update(add)
        if remove:
            group.liberties.difference_update(remove)

        new_lib_count = len(group.liberties)
        for fs in group.stones:
            self.liberty_cache[fs] = new_lib_count

    def _add_liberties(self, captured_stones):
        for fstone in captured_stones:
            for fn in NEIGHBORS[fstone]:
                group_id = self.group_index[fn]
                if group_id is not None:
                    self._update_liberties(group_id, add={fstone})
        

def is_koish(board, fc):
    'Check if fc is surrounded on all sides by 1 color, and return that color'
    if board[fc] != EMPTY: return None
    neighbor_colors = {board[fn] for fn in NEIGHBORS[fc]}
    if len(neighbor_colors) == 1 and not EMPTY in neighbor_colors:
        return list(neighbor_colors)[0]
    else:
        return None

class Position(namedtuple('Position', ['board', 'ko', 'liberty_tracker'])):
    @staticmethod
    def initial_state():
        return Position(board=EMPTY_BOARD, ko=None, liberty_tracker=LibertyTracker.from_board(EMPTY_BOARD))

    def get_board(self):
        return self.board

    def __str__(self):
        import textwrap
        return '\n'.join(textwrap.wrap(self.board, N))

    def play_move(self, fc, color):
        board, ko, liberty_tracker = self
        if fc == ko or board[fc] != EMPTY:
            raise IllegalMove

        possible_ko_color = is_koish(board, fc)
        new_board = place_stone(color, board, fc)
        new_liberty_tracker, captured_stones = liberty_tracker.add_stone(color, fc)
        new_board = bulk_place_stones(EMPTY, new_board, captured_stones)

        opp_color = swap_colors(color)

        if len(captured_stones) == 1 and possible_ko_color == opp_color:
            new_ko = list(captured_stones)[0]
        else:
            new_ko = None

        return Position(new_board, new_ko, new_liberty_tracker)

    def score(self):
        board = self.board
        while EMPTY in board:
            fempty = board.index(EMPTY)
            empties, borders = find_reached(board, fempty)
            possible_border_color = board[list(borders)[0]]
            if all(board[fb] == possible_border_color for fb in borders):
                board = bulk_place_stones(possible_border_color, board, empties)
            else:
                # if an empty intersection reaches both white and black,
                # then it belongs to neither player. 
                board = bulk_place_stones('?', board, empties)
        return board.count(BLACK) - board.count(WHITE)

    def get_liberties(self):
        return self.liberty_tracker.get_liberties()

