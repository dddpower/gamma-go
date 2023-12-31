import enum
from typing import NamedTuple
from typing import Literal

color = Literal["black", "white"]

class Player(enum.Enum):
    black = 1
    white = 2

    @property
    def other(self) -> 'Player':
        return Player.black if self == Player.white else Player.white

class Point(NamedTuple):
    row: int
    col: int
    
    def neighbors(self):
        return [
            Point(self.row - 1, self.col),
            Point(self.row + 1, self.col),
            Point(self.row, self.col - 1),
            Point(self.row, self.col + 1)
        ]