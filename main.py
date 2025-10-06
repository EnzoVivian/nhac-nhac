from nhacnhac import NhacNhac, GameState, PutPlay, MovePlay
from minMax import MinimaxAI

def main():
    game = NhacNhac("Alice", "Bob")
    ai_p2 = None

    use_ai = input("Bob deve ser controlado pela IA Minimax? (s/n): ").strip().lower()
    if use_ai == 's':
        try:
            depth = int(input("Qual a profundidade da IA? (ex: 3, 4, 5): ").strip())
            ai_p2 = MinimaxAI(game.p2, depth=depth)
        except ValueError:
            print("Profundidade inválida. Usando a padrão (3).")
            ai_p2 = MinimaxAI(game.p2, depth=3)


    while game.state in [GameState.P1_TURN, GameState.P2_TURN]:
        print(f"\n{game}")
        current_player = game.current_player
        print(f"É a vez de {current_player.name}")
        
        move = None
        if current_player == game.p2 and ai_p2:
            print("IA está pensando...")
            move = ai_p2.choose_move(game)
        else:
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