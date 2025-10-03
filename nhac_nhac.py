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
    board: list[list[list[Gobbler]]]  # Each position is now a stack of gobblers

    def __init__(self):
        self.board = [[[] for _ in range(3)] for _ in range(3)]

    def __str__(self):
        board_str = ""
        for i, row in enumerate(self.board):
            board_str += '|'.join(str(self.top_gobbler_at((i, j)))*2 if self.top_gobbler_at((i, j)) else '  ' for j in range(3)) + '\n'
            if i != 2:
                board_str += '—' * 8 + '\n'
        return board_str

    def validate_pos(self, pos: tuple[int, int]) -> bool:
        """Check if a position is within board bounds."""
        return 0 <= pos[0] < 3 and 0 <= pos[1] < 3

    def top_gobbler_at(self, pos: tuple[int, int]) -> Gobbler | None:
        """Returns the top gobbler at the given position, or None if empty."""
        stack = self.board[pos[0]][pos[1]]
        return stack[-1] if stack else None

    def can_place_gobbler(self, pos: tuple[int, int], gobbler: Gobbler) -> bool:
        """Check if a gobbler can be placed at the given position."""
        top_gobbler = self.top_gobbler_at(pos)
        return top_gobbler is None or gobbler.size > top_gobbler.size

    def place_gobbler(self, pos: tuple[int, int], gobbler: Gobbler) -> bool:
        """Place a gobbler at the given position. Returns True if successful."""
        if not self.can_place_gobbler(pos, gobbler):
            return False
        self.board[pos[0]][pos[1]].append(gobbler)
        return True

    def remove_top_gobbler(self, pos: tuple[int, int]) -> Gobbler | None:
        """Remove and return the top gobbler from the given position."""
        stack = self.board[pos[0]][pos[1]]
        return stack.pop() if stack else None

    def move_gobbler(self, from_pos: tuple[int, int], to_pos: tuple[int, int]) -> bool:
        """Move the top gobbler from one position to another."""
        gobbler = self.remove_top_gobbler(from_pos)
        if gobbler is None:
            return False
        
        if not self.place_gobbler(to_pos, gobbler):
            # Put it back if we can't place it
            self.board[from_pos[0]][from_pos[1]].append(gobbler)
            return False
        return True

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

    def __init__(self, p1_name: str, p2_name: str, initial_state = GameState.P1_TURN):
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
                if not self.board.validate_pos(pos):
                    return False
                if gobbler_index < 0 or gobbler_index >= len(player.gobblers):
                    return False

                # Check if we can place the gobbler at this position
                gobbler = player.gobblers[gobbler_index]
                return self.board.can_place_gobbler(pos, gobbler)
                
            case MovePlay(player, from_pos, to_pos):
                if not (self.board.validate_pos(from_pos) and self.board.validate_pos(to_pos)):
                    return False

                # Check if there's a gobbler to move and it belongs to current player
                top_gobbler = self.board.top_gobbler_at(from_pos)
                if top_gobbler is None or top_gobbler.color != player.color:
                    return False
                # Check if we can place it at the destination
                return self.board.can_place_gobbler(to_pos, top_gobbler)
                
            case _:
                return False  # Invalid move type

    def _check_winner(self) -> PlayerType | None:
        """Check if there's a winner. Returns the winning player's color or None."""
        # Check rows
        for row in range(3):
            colors = [self.board.top_gobbler_at((row, col)) for col in range(3)]
            if all(g is not None and g.color == colors[0].color for g in colors):
                return colors[0].color
        
        # Check columns
        for col in range(3):
            colors = [self.board.top_gobbler_at((row, col)) for row in range(3)]
            if all(g is not None and g.color == colors[0].color for g in colors):
                return colors[0].color
        
        # Check diagonals
        # Main diagonal (top-left to bottom-right)
        colors = [self.board.top_gobbler_at((i, i)) for i in range(3)]
        if all(g is not None and g.color == colors[0].color for g in colors):
            return colors[0].color
        
        # Anti-diagonal (top-right to bottom-left)
        colors = [self.board.top_gobbler_at((i, 2-i)) for i in range(3)]
        if all(g is not None and g.color == colors[0].color for g in colors):
            return colors[0].color
        
        return None

    def _switch_turn(self):
        """Switch to the next player's turn."""
        turn_map = {
            GameState.P1_TURN: GameState.P2_TURN,
            GameState.P2_TURN: GameState.P1_TURN
        }
        self.state = turn_map[self.state]

    def _update_game_state(self):
        """Check for winners and update game state accordingly."""
        # Check for a winner
        winner_color = self._check_winner()
        if winner_color is not None:
            self.state = GameState.P1_WINS if winner_color == PlayerType.RED else GameState.P2_WINS
        else:
            # Switch turn if no winner
            self._switch_turn()

    def play(self, move: NhacNhacPlay) -> bool:
        if self.state not in [GameState.P1_TURN, GameState.P2_TURN]:
            return False # game ended
        
        if not self._validate_move(move):
            return False
        
        match move:
            case PutPlay(player, gobbler_index, pos):
                gobbler = player.gobblers.pop(gobbler_index)
                self.board.place_gobbler(pos, gobbler)

            case MovePlay(player, from_pos, to_pos):
                self.board.move_gobbler(from_pos, to_pos)

            case _:
                return False  # This should never happen due to validation
        
        # Update game state (check for wins, switch turns)
        self._update_game_state()
        return True

def main():
    game = NhacNhac("Alice", "Bob")
    
    while game.state in [GameState.P1_TURN, GameState.P2_TURN]:
        print(f"\n{game}")
        current_player = game.current_player
        print(f"\n{current_player.name}'s turn")
        
        try:
            # Get move type
            move_type = input("Enter move type (put/move): ").strip().lower()
            
            if move_type == "put":
                # Show available gobblers
                print("Available gobblers:")
                for i, gobbler in enumerate(current_player.gobblers):
                    print(f"{i}: {gobbler}")
                
                gobbler_index = int(input("Choose gobbler index: "))
                row = int(input("Enter row (0-2): "))
                col = int(input("Enter col (0-2): "))
                
                move = PutPlay(current_player, gobbler_index, (row, col))
                
            elif move_type == "move":
                from_row = int(input("From row (0-2): "))
                from_col = int(input("From col (0-2): "))
                to_row = int(input("To row (0-2): "))
                to_col = int(input("To col (0-2): "))
                
                move = MovePlay(current_player, (from_row, from_col), (to_row, to_col))
                
            else:
                print("Invalid move type!")
                continue
            
            # Execute move
            if game.play(move):
                print("Move successful!")
            else:
                print("Invalid move! Try again.")
                
        except (ValueError, IndexError) as e:
            print(f"Invalid input: {e}")
    
    # Game ended
    print(f"\n{game}")
    
    match game.state:
        case GameState.P1_WINS:
            print(f"🎉 Game over! {game.p1.name} wins!")
        case GameState.P2_WINS:
            print(f"🎉 Game over! {game.p2.name} wins!")
        case GameState.DRAW:
            print("Game over! It's a draw!")
        case _:
            print("Game ended unexpectedly.")

if __name__ == "__main__":
    main()
