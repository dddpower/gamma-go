from typing import Iterable, Union
import copy
from dlgo.gotypes import Player, Point


class Move():
    def __init__(self, point: Union[Point, None]=None, is_pass=False, is_resign=False):
        assert (point is not None) ^ is_pass ^ is_resign
        self.point = point
        self.is_play = (self.point is not None)
        self.is_pass = is_pass
        self.is_resign = is_resign
    
    @classmethod
    def play(cls, point: Point):
        return Move(point=point)

    @classmethod
    def pass_turn(cls):
        return Move(is_pass=True)

    @classmethod
    def resign(cls):
        return Move(is_resign=True)


class GoString():
    def __init__(self, color: Player, stones: Iterable[Point], liberties: Iterable[Point]):
        self.color = color
        self.stones = set(stones)
        self.liberties = set(liberties)

    def remove_liberty(self, point: Point):
        self.liberties.remove(point)
    
    def add_liberty(self, point: Point):
        self.liberties.add(point)
    
    def merged_with(self, go_string: 'GoString'):
        assert go_string.color == self.color
        combined_stones = self.stones | go_string.stones
        return GoString(
            self.color,
            combined_stones,
            (self.liberties | go_string.liberties) - combined_stones
        )

    @property
    def num_liberties(self):
        return len(self.liberties)
    
    def __eq__(self, other: 'GoString'):
        return isinstance(other, GoString) and \
            self.color == other.color and \
            self.stones == other.stones and \
            self.liberties == other.liberties


class Board():
    def __init__(self, num_rows: int, num_cols: int) -> None:
        self.num_rows = num_rows
        self.num_cols = num_cols
        self._grid: dict[Point, GoString] = {}

    def place_stone(self, player: Player, point: Point):
        assert self.is_on_grid(point)
        assert self._grid.get(point) is None

        # Compute the configuration of adjacent strings
        adjacent_same_color: list[GoString] = []
        adjacent_opposite_color: list[GoString] = []
        liberties: list[Point] = []
        for neighbor in point.neighbors():
            if not self.is_on_grid(neighbor):
                continue
            neighbor_string = self._grid.get(neighbor)
            if neighbor_string is None:
                liberties.append(neighbor)
            elif neighbor_string.color == player:
                if neighbor_string not in adjacent_same_color:
                    adjacent_same_color.append(neighbor_string)
            elif neighbor_string not in adjacent_opposite_color:
                adjacent_opposite_color.append(neighbor_string)
        new_string = GoString(player, [point], liberties)

        # Merge any adjacent strings of the same color
        for same_color_string in adjacent_same_color:
            new_string = new_string.merged_with(same_color_string)
        for new_string_point in new_string.stones:
            self._grid[new_string_point] = new_string
        
        # Reduce liberties from adjacent strings of the opposite color
        for other_color_string in adjacent_opposite_color:
            other_color_string.remove_liberty(point)
            if other_color_string.num_liberties == 0:
                self._remove_string(other_color_string)
    
    # utilities
    def is_on_grid(self, point: Point) -> bool:
        return 1 <= point.row <= self.num_rows and \
            1 <= point.col <= self.num_cols
    
    def get(self, point: Point):
        string = self._grid.get(point)
        return None if string is None else string.color
    
    def get_go_string(self, point: Point):
        return self._grid.get(point)
    
    def _remove_string(self, string: GoString):
        for point in string.stones:
            for neighbor in point.neighbors():
                neighbor_string = self._grid.get(neighbor)
                if neighbor_string is None:
                    continue
                if neighbor_string is not string:
                    neighbor_string.add_liberty(point)
            self._grid[point] = None


class GameState():
    def __init__(self, board: Board, next_player: Player, previous: Union['GameState', None], move: Union[Move, None]):
        self.board = board
        self.next_player = next_player
        self.previous_state = previous
        self.last_move = move
    
    def apply_move(self, move: Move):
        if move.is_play:
            next_board = copy.deepcopy(self.board)
            next_board.place_stone(self.next_player, move.point)
        else:
            next_board = self.board
        return GameState(next_board, self.next_player.other, self, move)

    @classmethod
    def new_game(cls, board_size: Union[int, tuple[int, int]]):
        if isinstance(board_size, int):
            board_size = (board_size, board_size)
        board = Board(*board_size)
        return GameState(board, Player.black, None, None)

    def is_over(self):
        if self.last_move is None:
            return False
        if self.last_move.is_resign:
            return True
        
        second_last_move = self.previous_state.last_move
        if second_last_move is None:
            return False
        return self.last_move.is_pass and second_last_move.is_pass

    def is_move_self_capture(self, player: Player, move: Move):
        if not move.is_play:
            return False
        next_board = copy.deepcopy(self.board)
        next_board.place_stone(player, move.point)
        new_string = next_board.get_go_string(move.point)
        return new_string.num_liberties == 0
    
    @property
    def situation(self):
        return (self.next_player, self.board)
    
    def does_move_violate_ko(self, player: Player, move: Move):
        if not move.is_play:
            return False
        next_board = copy.deepcopy(self.board)
        next_board.place_stone(player, move.point)
        next_situation = (player.other, next_board)
        past_state = self.previous_state
        while past_state is not None:
            if past_state.situation == next_situation:
                return True
            past_state = past_state.previous_state
        return False

    def ins_valid_move(self, move: Move):
        if self.is_over():
            return False
        if move.is_pass or move.is_resign:
            return True
        return self.board.get(move.point) is None and \
            not self.is_move_self_capture(self.next_player, move) and \
            not self.does_move_violate_ko(self.next_player, move)