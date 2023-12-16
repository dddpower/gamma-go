from dlgo.gotypes import Player, Point
from dlgo.goboard_slow import Move, Board

COLS = "ABCDEFGHJKLMNOPQRST"
STONE_TO_CHAR = {
    None: ' . ',
    Player.black: ' X ',
    Player.white: ' O ',
}

def print_move(player: Player, move: Move):
    if move.is_pass:
        move_str = 'passes'
    elif move.is_resign:
        move_str = 'resigns'
    else:
        move_str = '%s%d' % (COLS[move.point.col - 1], move.point.row)
    print("%s %s" % (player, move_str))

def print_board(board: Board):
    for row in range(board.num_rows, 0, -1):
        bump = " " if row <= 9 else ""
        line = []
        for col in range(1, board.num_cols + 1):
            stone = board.get(Point(row, col))
            line.append(STONE_TO_CHAR[stone])
        print('%s%d %s' % (bump, row, ''.join(line)))
    print('    ' + '  '.join(COLS[:board.num_cols]))