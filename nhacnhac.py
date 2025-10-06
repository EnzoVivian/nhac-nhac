# logica_jogo.py

import copy
from dataclasses import dataclass
from abc import ABC
from enum import Enum

reset_code = "\033[0m"

class PlayerType(str, Enum):
    RED = "red"
    BLUE = "blue"

    def color_code(self):
        return "\033[91m" if self == PlayerType.RED else "\033[94m"

class SizeType(int, Enum):
    SMALL = 1
    MEDIUM = 2
    LARGE = 3

@dataclass
class Gobbler:
    size: SizeType
    color: PlayerType

    def __str__(self):
        color_code = self.color.color_code()
        size_char = {SizeType.SMALL: 'S', SizeType.MEDIUM: 'M', SizeType.LARGE: 'L'}[self.size]
        return f"{color_code}{size_char}{reset_code}"

class Player:
    name: str
    color: PlayerType
    gobblers: list[Gobbler]

    def __init__(self, name: str, color: PlayerType):
        self.name = name
        self.color = color
        self.gobblers = [Gobbler(size, color) for size in SizeType for _ in range(2)]
    
    def __str__(self):
        color_code = self.color.color_code()
        return f"Player {color_code}{self.name}{reset_code}\n|{'|'.join(str(g) for g in self.gobblers)}|"

class Board:
    board: list[list[list[Gobbler]]]

    def __init__(self):
        self.board = [[[] for _ in range(3)] for _ in range(3)]

    def __str__(self):
        board_str = ""
        for i, row in enumerate(self.board):
            line_parts = []
            for j in range(3):
                gobbler = self.top_gobbler_at((i, j))
                if gobbler:
                    line_parts.append(f" {gobbler}") 
                else:
                    line_parts.append("  ")
            
            board_str += '|'.join(line_parts) + '\n'
            if i != 2:
                board_str += '—' * 8 + '\n'
        return board_str

    def validate_pos(self, pos: tuple[int, int]) -> bool:
        return 0 <= pos[0] < 3 and 0 <= pos[1] < 3

    def top_gobbler_at(self, pos: tuple[int, int]) -> Gobbler | None:
        stack = self.board[pos[0]][pos[1]]
        return stack[-1] if stack else None

    def can_place_gobbler(self, pos: tuple[int, int], gobbler: Gobbler) -> bool:
        top_gobbler = self.top_gobbler_at(pos)
        return top_gobbler is None or gobbler.size > top_gobbler.size

    def place_gobbler(self, pos: tuple[int, int], gobbler: Gobbler) -> Gobbler | None:
        if not self.can_place_gobbler(pos, gobbler):
            return "INVALID_MOVE"
        
        covered_gobbler = self.top_gobbler_at(pos)
        self.board[pos[0]][pos[1]].append(gobbler)
        return covered_gobbler

    def move_gobbler(self, from_pos: tuple[int, int], to_pos: tuple[int, int]) -> tuple[Gobbler, Gobbler | None] | str:
        gobbler_to_move = self.top_gobbler_at(from_pos)
        if gobbler_to_move is None:
            return "INVALID_MOVE"
        
        top_at_dest = self.top_gobbler_at(to_pos)
        if not (top_at_dest is None or gobbler_to_move.size > top_at_dest.size):
             return "INVALID_MOVE"

        moved_gobbler = self.remove_top_gobbler(from_pos)
        covered_gobbler = self.place_gobbler(to_pos, moved_gobbler)
        
        return (moved_gobbler, covered_gobbler)

    def remove_top_gobbler(self, pos: tuple[int, int]) -> Gobbler | None:
        stack = self.board[pos[0]][pos[1]]
        return stack.pop() if stack else None

@dataclass
class NhacNhacPlay(ABC):
    player: Player

@dataclass
class PutPlay(NhacNhacPlay):
    gobbler_index: int
    pos: tuple[int, int]

@dataclass
class MovePlay(NhacNhacPlay):
    from_pos: tuple[int, int]
    to_pos: tuple[int, int]

class GameState(Enum):
    P1_TURN = "p1_turn"
    P2_TURN = "p2_turn"
    P1_WINS = "p1_wins"
    P2_WINS = "p2_wins"
    DRAW = "draw"
    
class NhacNhac:
    board: Board
    p1: Player
    p2: Player
    state: GameState

    def __init__(self, p1_name: str, p2_name: str, initial_state=GameState.P1_TURN):
        self.board = Board()
        self.p1 = Player(p1_name, PlayerType.RED)
        self.p2 = Player(p2_name, PlayerType.BLUE)
        self.state = initial_state

    def __str__(self):
        return f"{self.p1}\n{self.p2}\n{self.board}"

    @property
    def current_player(self) -> Player | None:
        match self.state:
            case GameState.P1_TURN: return self.p1
            case GameState.P2_TURN: return self.p2
            case _: return None

    def _validate_move(self, move: NhacNhacPlay) -> bool:
        if move.player != self.current_player:
            return False

        match move:
            case PutPlay(player, gobbler_index, pos):
                if not self.board.validate_pos(pos): return False
                if gobbler_index < 0 or gobbler_index >= len(player.gobblers): return False
                gobbler = player.gobblers[gobbler_index]
                return self.board.can_place_gobbler(pos, gobbler)
                
            case MovePlay(player, from_pos, to_pos):
                if not (self.board.validate_pos(from_pos) and self.board.validate_pos(to_pos)): return False
                top_gobbler = self.board.top_gobbler_at(from_pos)
                if top_gobbler is None or top_gobbler.color != player.color: return False
                return self.board.can_place_gobbler(to_pos, top_gobbler)
                
            case _:
                return False

    def _check_winner(self) -> PlayerType | None:
        for row in range(3):
            line = [self.board.top_gobbler_at((row, col)) for col in range(3)]
            if line[0] and all(g is not None and g.color == line[0].color for g in line):
                return line[0].color
        for col in range(3):
            line = [self.board.top_gobbler_at((row, col)) for row in range(3)]
            if line[0] and all(g is not None and g.color == line[0].color for g in line):
                return line[0].color
        diag1 = [self.board.top_gobbler_at((i, i)) for i in range(3)]
        if diag1[0] and all(g is not None and g.color == diag1[0].color for g in diag1):
            return diag1[0].color
        
        diag2 = [self.board.top_gobbler_at((i, 2-i)) for i in range(3)]
        if diag2[0] and all(g is not None and g.color == diag2[0].color for g in diag2):
            return diag2[0].color
        
        return None

    def _switch_turn(self):
        turn_map = {GameState.P1_TURN: GameState.P2_TURN, GameState.P2_TURN: GameState.P1_TURN}
        self.state = turn_map.get(self.state, self.state)

    def _update_game_state(self):
        winner_color = self._check_winner()
        if winner_color is not None:
            self.state = GameState.P1_WINS if winner_color == PlayerType.RED else GameState.P2_WINS
        else:
            self._switch_turn()

    def play(self, move: NhacNhacPlay) -> bool:
        if self.state not in [GameState.P1_TURN, GameState.P2_TURN]:
            return False
        if not self._validate_move(move):
            return False
        
        success = False
        match move:
            case PutPlay(player, gobbler_index, pos):
                gobbler = player.gobblers[gobbler_index]
                result = self.board.place_gobbler(pos, gobbler)
                if result != "INVALID_MOVE":
                    player.gobblers.pop(gobbler_index)
                    success = True
            case MovePlay(player, from_pos, to_pos):
                result = self.board.move_gobbler(from_pos, to_pos)
                if result != "INVALID_MOVE":
                    success = True
            case _:
                return False
        
        if success:
            self._update_game_state()
        return success
