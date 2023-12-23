from dlgo.agent.base import Agent
from dlgo.agent import naive
from dlgo.gotypes import Player
from dlgo.goboard import GameState, Move
from typing import Optional
import copy
import random, math

class MCTSNode(object):
    def __init__(self, game_state: GameState, parent: Optional["MCTSNode"]=None, move: Optional[Move]=None):
        self.game_state = game_state
        self.parent = parent
        self.move = move
        self.win_counts = {
            Player.black: 0,
            Player.white: 0,
        }
        self.num_rollouts = 0
        self.children: list[MCTSNode] = []
        self.unvisiterd_moves = game_state.legal_moves()
    
    def add_random_child(self):
        index = random.randint(0, len(self.unvisiterd_moves) - 1)
        new_move = self.unvisiterd_moves.pop(index)
        new_game_state = self.game_state.apply_move(new_move)
        new_node = MCTSNode(new_game_state, self, new_move)
        self.children.append(new_node)
        return new_node

    def record_win(self, winner: Player):
        self.win_counts[winner] += 1
        self.num_rollouts += 1

    def can_add_child(self):
        return len(self.unvisiterd_moves) > 0
    
    def is_terminal(self):
        return self.game_state.is_over()
    
    # def winning_frac(self, player: Player):
    #     return float(self.win_counts[player]) / float(self.num_rollouts)

    # 임의 구현함
    def winning_pct(self, player: Player) -> float:
        return float(self.win_counts[player]) / float(self.num_rollouts)
    
def uct_score(parent_rollouts: int, child_rollouts: int, win_pct: float, temperature: float):
    exploration = math.sqrt(math.log(parent_rollouts) / child_rollouts)
    return win_pct + temperature * exploration

class MCTSAgent(Agent):
    def __init__(self, num_rounds= 0, temperature=1.5):
        # A placeholder constructor, needs to be implemented
        self.num_rounds = num_rounds
        self.temperature = temperature

    def select_move(self, game_state: GameState):
        root = MCTSNode(game_state)

        for i in range(self.num_rounds):
            node = root
            while (not node.can_add_child()) and (not node.is_terminal()):
                node = self.select_child(node)

            if node.can_add_child():
                node = node.add_random_child()
            
            winner = self.simulate_random_game(node.game_state)

            while node is not None:
                node.record_win(winner)
                node = node.parent
        
            best_move: Optional[Move] = None
            best_pct = -1.0
            for child in root.children:
                child_pct = child.winning_pct(game_state.next_player)
                if child_pct > best_pct:
                    best_pct = child_pct
                    best_move = child.move
            return best_move
    
    def select_child(self, node: MCTSNode) -> MCTSNode:
        total_rollouts = sum(child.num_rollouts for child in node.children)

        best_score: float = -1.0
        best_child: MCTSNode = node  # None 타입을 피하기 위해 임의로 한 node를 지정함
        for child in node.children:
            score = uct_score(
                total_rollouts,
                child.num_rollouts,
                child.winning_pct(node.game_state.next_player),
                self.temperature
            )
            if score > best_score:
                best_score = score
                best_child = child
        return best_child

    def simulate_random_game(self, game_state: GameState) -> Player:
        game = copy.deepcopy(game_state)
        bots = {
            Player.black: naive.RandomBot(),
            Player.white: naive.RandomBot(),
        }
        while not game.is_over():
            bot_move = bots[game.next_player].select_move(game)
            game = game.apply_move(bot_move)
        
        return game.next_player