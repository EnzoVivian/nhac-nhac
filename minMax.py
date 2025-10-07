from nhacnhac import PutPlay, MovePlay, SizeType

class MinimaxAI:
    
    def __init__(self, player, depth=10):
        self.player = player
        self.depth = depth

    def choose_move(self, game):
        best_move = None
        best_value = -float('inf')
        alpha = -float('inf')
        beta = float('inf')

        possible_moves = list(self._get_all_moves(game, self.player))
        for move in possible_moves:
            undo_info = self._make_move(game, move)
            
            board_value = self._minimax(game, self.depth - 1, alpha, beta, False)
            
            self._undo_move(game, move, undo_info)
            
            if board_value > best_value:
                best_value = board_value
                best_move = move
            
            alpha = max(alpha, board_value)
        
        print(f"Jogada: {type(best_move).__name__}")
        return best_move


    def _minimax(self, game, depth, alpha, beta, is_maximizing):
        winner = game._check_winner()
        if depth == 0 or winner is not None:
            return self._evaluate_board(game)

        possible_moves = self._get_all_moves(game, game.current_player)

        if is_maximizing:
            max_eval = -float('inf')
            for move in possible_moves:
                undo_info = self._make_move(game, move)
                evaluation = self._minimax(game, depth - 1, alpha, beta, False)
                self._undo_move(game, move, undo_info)
                
                max_eval = max(max_eval, evaluation)
                alpha = max(alpha, evaluation)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in possible_moves:
                undo_info = self._make_move(game, move)
                evaluation = self._minimax(game, depth - 1, alpha, beta, True)
                self._undo_move(game, move, undo_info)

                min_eval = min(min_eval, evaluation)
                beta = min(beta, evaluation)
                if beta <= alpha:
                    break
            return min_eval
    
    def _make_move(self, game, move):
        game._switch_turn()
        if isinstance(move, PutPlay):
            gobbler = move.player.gobblers.pop(move.gobbler_index)
            covered_piece = game.board.place_gobbler(move.pos, gobbler)
            return (gobbler, covered_piece)
        if isinstance(move, MovePlay):
            moved_piece, covered_piece = game.board.move_gobbler(move.from_pos, move.to_pos)
            return (moved_piece, covered_piece)

    def _undo_move(self, game, move, undo_info):
        if isinstance(move, PutPlay):
            gobbler, covered_piece = undo_info
            game.board.remove_top_gobbler(move.pos)
            if covered_piece:
                game.board.place_gobbler(move.pos, covered_piece)
            move.player.gobblers.insert(move.gobbler_index, gobbler)
        if isinstance(move, MovePlay):
            moved_piece, covered_piece = undo_info
            game.board.remove_top_gobbler(move.to_pos)
            if covered_piece:
                game.board.place_gobbler(move.to_pos, covered_piece)
            game.board.place_gobbler(move.from_pos, moved_piece)
        game._switch_turn()

    def _evaluate_board(self, game):
        winner = game._check_winner()
        if winner is not None:
            return 10000 if winner == self.player.color else -10000

        score = 0
        piece_value = {SizeType.LARGE: 3, SizeType.MEDIUM: 2, SizeType.SMALL: 1}
        lines = self._get_all_lines(game.board)
        for line in lines:
            score += self._evaluate_line(line)

        position_value = [[2, 1, 2], [1, 3, 1], [2, 1, 2]]
        for r in range(3):
            for c in range(3):
                piece = game.board.top_gobbler_at((r, c))
                if piece:
                    value = piece_value[piece.size] * position_value[r][c]
                    score += value if piece.color == self.player.color else -value
        
        for gobbler in game.p1.gobblers:
            score += piece_value[gobbler.size] * 5 if game.p1.color == self.player.color else -piece_value[gobbler.size] * 5
        for gobbler in game.p2.gobblers:
            score += piece_value[gobbler.size] * 5 if game.p2.color == self.player.color else -piece_value[gobbler.size] * 5
        return score
    
    def _get_all_lines(self, board):
        lines = []
        for r in range(3): lines.append([board.top_gobbler_at((r, c)) for c in range(3)])
        for c in range(3): lines.append([board.top_gobbler_at((r, c)) for r in range(3)])
        lines.append([board.top_gobbler_at((i, i)) for i in range(3)])
        lines.append([board.top_gobbler_at((i, 2 - i)) for i in range(3)])
        return lines
    
    def _evaluate_line(self, line):
        score = 0
        ai_pieces = sum(1 for p in line if p and p.color == self.player.color)
        opp_pieces = sum(1 for p in line if p and p.color != self.player.color)
        if ai_pieces == 2 and opp_pieces == 0: score += 500
        elif ai_pieces == 1 and opp_pieces == 0: score += 50
        if opp_pieces == 2 and ai_pieces == 0: score -= 500
        elif opp_pieces == 1 and ai_pieces == 0: score -= 50
        return score

    # Otimização para criar jogadas gerado por IA
    def _get_all_moves(self, game, player):
        for i, gobbler in enumerate(player.gobblers):
            for r in range(3):
                for c in range(3):
                    if game.board.can_place_gobbler((r, c), gobbler):
                        yield PutPlay(player, i, (r, c))
        
        for r in range(3):
            for c in range(3):
                g = game.board.top_gobbler_at((r, c))
                if g and g.color == player.color:
                    for r2 in range(3):
                        for c2 in range(3):
                            if (r, c) != (r2, c2) and game.board.can_place_gobbler((r2, c2), g):
                                yield MovePlay(player, (r, c), (r2, c2))
        
        
