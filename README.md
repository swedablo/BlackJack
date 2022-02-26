# BlackJack
A blackjack program, including a strategy derived from Machine Learning.

The program compares a simple Dealer Strategy to a Machine Learning Strategy using reinforced learning. Its quite fascinationg how the ML program learns by itself, without knowing the rules of the game, a strategy very close to the well known "Basic Strategy" (as describe in the book "Beat The Dealer" by Edward O Thorp).

Run "game.py" to start the simulation.

### Blackjack Rules: ###
1. The goal of BlackJack is to beat the dealer's hand without going above 21.
2. The dealer have to draw a card until the dealer has 17 or above.
3. On a tie, the player's bet is returned to the player.
4. BlackJack (i.e. Ace + 10) gives 1.5 times the bet.
5. All suited cards (K, D and J) is valued 10.
6. Ace can be either 11 (aka soft hand) or 1 (aka hard hand).
