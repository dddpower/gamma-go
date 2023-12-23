import importlib

from dlgo.goboard import Point, GameState
from numpy import float64
from numpy.typing import NDArray

class Encoder:
    def name(self) -> str:
        raise NotImplementedError()
    
    def encode(self, game_state: GameState) -> NDArray[float64]:
        raise NotImplementedError()

    def encode_point(self, point) -> int:
        raise NotImplementedError()
    
    def decode_point_index(self, index) -> Point:
        raise NotImplementedError()
    
    def num_points(self) -> int:
        raise NotImplementedError()
    
    def shape(self) -> tuple[int, int, int]:
        raise NotImplementedError()


def get_encoder_by_name(name, board_size) -> Encoder:
    if isinstance(board_size, int):
        board_size = (board_size, board_size)
    module = importlib.import_module('dlgo.encoders.' + name)
    constructor = getattr(module, 'create')
    return constructor(board_size)