from MLStrategy import MLStrategy
import deck 
import player
import MLStrategy

class Score:
    def __init__(self, name='', win=0, tie=0, losses=0):
        self.namePlayer = name
        self.wins = win
        self.ties = tie
        self.losses = losses
    
    def win(self):
        self.wins += 1

    def tie(self):
        self.ties += 1    

    def loss(self):
        self.losses += 1
    
    def BlackJack(self):
        self.wins += 1.5
    
    def show(self):
        text = """{}'s scores:
            -wins: {}
            -ties: {}
            -losses: {}
            """.format(self.namePlayer, self.wins, self.ties, self.losses)
        print(text)

    def reinitialize(self):
        self.wins = 0
        self.ties = 0
        self.losses = 0

    def getScores(self):
        return (self.namePlayer, self.wins, self.ties, self.losses)

class BlackJack:

    def __init__(self, numPlayers = 1):
        self.playDeck = deck.Deck()
        self.dealer = player.Player('Dealer')
        self.players = []
        self.scores = {}
        self.addPlayers(numPlayers)

    def addPlayers(self, numPlayers):
        for p in range(numPlayers):
            self.players.append(player.Player('Player_{}'.format(p+1)))
            self.scores['Player_{}'.format(p+1)] = Score(name='Player_{}'.format(p+1))

    def setupGame(self):
        #First card for players
        for p in self.players:
            p.clearTotal()
            self.hitMe(p)

        #First card for dealer
        self.dealer.clearTotal()
        self.hitMe(self.dealer)
#        self.dealer.drawCard(self.playDeck.drawCard())

        #Second card for players
        for p in self.players:
            #p.drawCard(self.playDeck.drawCard())
            self.hitMe(p)

        #Second (hidden) card for dealer
        self.hiddenCardDealer = self.playDeck.drawCard()
    
    def getStatus(self, player):
        """Used in the 'show' function to get detailed information of a table"""
        if player.hasSoftHand():
            return("{} has {}, soft hand: {}".format(player.getName(), player.getTotal(), player.showHand())) 
        else:
            return("{} has {}, hard hand: {}".format(player.getName(), player.getTotal(), player.showHand()))

    def show(self):
        print('*** DEALER ***')
        print(self.getStatus(self.dealer))
        print(' ')
        print('*** PLAYERS ***')
        for p in self.players:
            print(self.getStatus(p))
        print(' ')

    def playOneRound_DealerStrategy(self):
        #Iterate through each player
        for p in self.players:
            self.dealerStrategy(p)

        self.playDealersTurn()

    def playDealersTurn(self): 
        #Dealers turn. First the hidden card is flipped. Do that by re-introducing it to the top of the deck
        self.playDeck.putCardOnTop(self.hiddenCardDealer)
        self.dealerStrategy(self.dealer)

    def dealerStrategy(self, player):
        while player.getTotal() < 17:
            self.hitMe(player)

    def play_DealerStrategy(self, rounds = 1, debug = False):
        for r in range(rounds):
            self.setupGame()
            self.playOneRound_DealerStrategy()
            self.updateScores()
            if debug:
                print('\n--- ROUND {}'.format(r+1))
                self.show()

    def play_MLStrategy(self, Strategy, rounds = 1, debug = False ):
        
        Strategy.setExplorationRate(0)

        if debug: print('Strategy created')
        for r in range(rounds):

            if debug: print('\n--- Start of ROUND {}'.format(r+1))
            
            self.setupGame()
            if debug: print('Game setup. Start to play')
            if debug: print('Player starts with: ', self.getStatus(self.players[0]))
            #play one round
            for player in self.players: #let all players play
                while True: #Play until player's action == 0 (i.e. Stand) or until player bust.
                    action = Strategy.chooseAction(player, self.dealer)
                    if debug: print(f'Action = {action}')
                    if action == 0:
                        break
                    else:
                        self.hitMe(player)
                        if (player.getTotal() > 21):
                            if debug: print('BUSTS!', self.getStatus(player))
                            break  
                    if debug: print('->NewTotal: ', self.getStatus(player))
            self.playDealersTurn()

            #Round is now done. Decide winner and reward

            self.updateScores()
            if debug:
                print('--- End of ROUND {}'.format(r+1))
                self.show()
        


    def train_MLStrategy(self, rounds = 1, debug = False, saveQValues=False):
        
        Strategy = MLStrategy.MLStrategy()
        if debug: print('Strategy created')
        for r in range(rounds):

            if debug: print('\n--- Start of ROUND {}'.format(r+1))
            
            self.setupGame()
            if debug: print('Game setup. Start to play')
            if debug: print('Player starts with: ', self.getStatus(self.players[0]))
            #play one round
            while True: #Play until action == 0 (i.e. Stand) or until player bust.
                action = Strategy.chooseAction(self.players[0], self.dealer)
                if debug: print(f'Action = {action}')
                if action == 0:
                    break
                else:
                    self.hitMe(self.players[0])
                    if (self.players[0].getTotal() > 21):
                        if debug: print('BUSTS!', self.getStatus(self.players[0]))
                        break  
                if debug: print('->NewTotal: ', self.getStatus(self.players[0]))
            self.playDealersTurn()

            #Round is now done. Decide winner and reward
            winners = self.decideWinner()
            Strategy.reward(self.players[0], self.dealer, winners[self.players[0].getName()])
            Strategy.updateExplorationRate(r)

            self.updateScores()
            if debug:
                print('--- End of ROUND {}'.format(r+1))
                self.show()

            if r%1000 == 0: 
                print('Round: {}....'.format(r))
                print('Exploration rate: {}'.format(Strategy.getExplorationRate()))
                self.showScores()
                self.reinitializeScores()
        
        #Print Q-table
        Strategy.printDecisionTable()
        if saveQValues:
            Strategy.saveQValueJson()
        
        
       
    def hitMe(self, player):
        player.drawCard(self.playDeck.drawCard())
        if self.playDeck.getCardsLeft() < 10:
            self.playDeck.reinitializeDeck()
            self.playDeck.shuffle()

    def decideWinner(self):
        winners = {}
        for p in self.players:
            if p.hasBlackJack():
                winners[p.getName()] = 1
            elif (p.getTotal() > 21) or ( (p.getTotal() < self.dealer.getTotal()) and (self.dealer.getTotal() <= 21) ):
                winners[p.getName()] = -1
            elif p.getTotal() == self.dealer.getTotal():
                winners[p.getName()] = 0
            else:
                winners[p.getName()] = 1
        return winners

    #### SCORE RELATED FUNCTIONS ####
    def updateScores(self):
        for p in self.players:
            if p.hasBlackJack():
                self.scores[p.getName()].BlackJack()
            elif (p.getTotal() > 21) or ( (p.getTotal() < self.dealer.getTotal()) and (self.dealer.getTotal() <= 21) ):
                self.scores[p.getName()].loss()
            elif p.getTotal() == self.dealer.getTotal():
                self.scores[p.getName()].tie()
            else:
                self.scores[p.getName()].win()

    def showScores(self):
        for key in self.scores:
            self.scores[key].show()

    def reinitializeScores(self):
        for key in self.scores:
            self.scores[key].reinitialize()

if __name__ == '__main__':

    players = 1
    rounds  = 150001
    train = False
    saveQValues = False

    myGame = BlackJack(players)

    if train:
        myGame.train_MLStrategy(rounds, debug=False, saveQValues=saveQValues)

    rounds = 100000
    print('Number of players equals: {}'.format(len(myGame.players)))
    print('Number of rounds equals : {}'.format(rounds))

    #Machine learning strategy
    print('ML strategy:')
    myGame.play_MLStrategy(rounds, debug=False)
    myGame.showScores()
    myGame.reinitializeScores()

    #Dealer Strategy
    print('Dealer strategy')
    myGame.play_DealerStrategy(rounds, debug=False)
    myGame.showScores()
    myGame.reinitializeScores()

    


