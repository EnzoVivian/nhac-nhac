Grupo Bob BreezIA: Bruno Panizzi, Enzo Vivian, Guilherme Tavares e Gustavo Amaro

Implementação do jogo Nhac Nhac e de uma inteligência artificial Minimax em Python para o trabalho de Inteligência Artificial, com suporte para:
- Dois jogadores humanos
- Humano vs IA
- IA vs IA

Arquivos principais
-------------------
- `nhacnhac.py` - Implementação das regras do jogo;
- `minMax.py` - Implementação da IA Minimax, com podqa alpha e beta e também avaliação de eurística;
- `main.py` - Interface de linha de comando para jogar.


Como executar (é necessário o Python 3.10 ou maior)
```
python main.py (Windows)
python3 main.py (Linux)
```

Para jogar, basta seguir as instruções no terminal, lembrando que não existe limite para o número de jogadas que a IA pode prever, porém, como um dos requisitos
do trabalho é o turno durar no máximo 30 segundos, é recomendado usar até 5 de profundidade.

Modos de jogo
--------------------
- 1: Ambos os jogadores inserem jogadas manualmente;
- 2: Humano joga primeiro;
- 3: IA joga primeiro;
- 4: Ambos jogadoes são controlados pela IA.

Jogadas
--------------------
- put: insere a peça no lugar escolhido;
- move: caso sua peça não esteja "engolida" por outra, pode move-la de lugar.

- As linhas estão ordenadas de cima para baixo em ordem crescente (0 é a superior, 2 é a inferior)
- As colunas estão ordenadas da esquerda para a direita em ordem crescente (0 é a esquerda, 2 é a direita)
- Para desfazer uma jogada, basta digitar algo inválido, como uma letra, e a jogada atual será invalidada, reiniciando o turno
