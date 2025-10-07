from nhacnhac import NhacNhac, GameState, PutPlay, MovePlay
from minMax import MinimaxAI
import time

# Gerado por IA
def main():
    game = NhacNhac("Alice", "Bob")
    ai_p1 = None
    ai_p2 = None

    print("Selecione o modo de jogo:")
    print("  1: Humano vs. Humano")
    print("  2: Humano (Alice) vs. IA (Bob)")
    print("  3: IA (Alice) vs. Humano (Bob)")
    print("  4: IA (Alice) vs. IA (Bob)")
    
    choice = input("Escolha uma opção (1-4): ").strip()

    if choice in ['3', '4']:
        try:
            depth_p1 = int(input("Qual a profundidade da IA para Alice (P1)?").strip())
            ai_p1 = MinimaxAI(game.p1, depth=depth_p1)
        except ValueError:
            print("Profundidade inválida. Usando a padrão (3).")
            ai_p1 = MinimaxAI(game.p1, depth=3)

    if choice in ['2', '4']:
        try:
            depth_p2 = int(input("Qual a profundidade da IA para Bob (P2)?").strip())
            ai_p2 = MinimaxAI(game.p2, depth=depth_p2)
        except ValueError:
            print("Profundidade inválida. Usando a padrão (3).")
            ai_p2 = MinimaxAI(game.p2, depth=3)

    while game.state in [GameState.P1_TURN, GameState.P2_TURN]:
        print(f"\n{game}")
        current_player = game.current_player
        print(f"É a vez de {current_player.color.color_code()}{current_player.name}\033[0m")        
        move = None
        is_human_turn = True

        if current_player == game.p1 and ai_p1:
            print(f"IA ({game.p1.name}) está pensando...")
            move = ai_p1.choose_move(game)
            is_human_turn = False

        elif current_player == game.p2 and ai_p2:
            print(f"IA ({game.p2.name}) está pensando...")
            move = ai_p2.choose_move(game)
            is_human_turn = False
        
        if is_human_turn:
            try:
                move_type = input("Digite o tipo de jogada (put/move): ").strip().lower()
                
                if move_type == "put":
                    print("Peças disponíveis:")
                    for i, gobbler in enumerate(current_player.gobblers):
                        print(f"  {i}: {gobbler}")
                    
                    gobbler_index = int(input("Escolha o índice da peça: "))
                    row = int(input("Digite a linha (0-2): "))
                    col = int(input("Digite a coluna (0-2): "))
                    move = PutPlay(current_player, gobbler_index, (row, col))
                    
                elif move_type == "move":
                    from_row = int(input("Mover da linha (0-2): "))
                    from_col = int(input("Mover da coluna (0-2): "))
                    to_row = int(input("Mover para a linha (0-2): "))
                    to_col = int(input("Mover para a coluna (0-2): "))
                    move = MovePlay(current_player, (from_row, from_col), (to_row, to_col))
                    
                else:
                    print("Tipo de jogada inválido!")
                    continue
            except (ValueError, IndexError) as e:
                print(f"Entrada inválida: {e}")
                continue

        if move and game.play(move):
            print("Jogada bem-sucedida!")
            if ai_p1 and ai_p2:
                time.sleep(1)
        else:
            print("Jogada inválida! Tente novamente.")
    
    print(f"\n{game}")
    match game.state:
        case GameState.P1_WINS: print(f"🎉 Fim de jogo! {game.p1.name} venceu!")
        case GameState.P2_WINS: print(f"🎉 Fim de jogo! {game.p2.name} venceu!")
        case GameState.DRAW: print("Fim de jogo! Empate!")
        case _: print("O jogo terminou.")

if __name__ == "__main__":
    main()