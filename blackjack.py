from mlstrategy import MLStrategy
import deck 
import player
import mlstrategy
import dealerstrategy

class Score:
    def __init__(self, name='', strategy='dealerstrategy', win=0, tie=0, losses=0):
        self.namePlayer = name
        self.playerstrategy = strategy
        self.wins = win
        self.ties = tie
        self.losses = losses
    
    def updateStrategy(self,strategy):
        self.playerstrategy = strategy
    
    def win(self):
        self.wins += 1

    def tie(self):
        self.ties += 1    

    def loss(self):
        self.losses += 1
    
    def BlackJack(self):
        self.wins += 1.5
    
    def show(self):
        text = """{}'s scores (Strategy: {}):
            -wins: {}
            -ties: {}
            -losses: {}
            """.format(self.namePlayer, self.playerstrategy, self.wins, self.ties, self.losses)
        print(text)

    def reinitialize(self):
        self.wins = 0
        self.ties = 0
        self.losses = 0

    def getScores(self):
        return (self.namePlayer, self.wins, self.ties, self.losses)

class BlackJack:

    def __init__(self, numPlayers = 1, selectedStrategies = [], debug=False):
        self.playDeck = deck.Deck()
        self.players = []
        self.selectableStrategies = ['dealerstrategy', 'mlstrategy']
        self.dealer = player.Player('Dealer', self.selectableStrategies[0])
        self.scores = {}
        self.addPlayers(numPlayers) #and sets default strategy.
        self.updatePlayerStrategy(selectedStrategies,debug)

    def addPlayers(self, numPlayers):
        for p in range(numPlayers):
            name = 'Player_{}'.format(p+1)
            self.players.append(player.Player(name, self.selectableStrategies[0]))
            self.scores[name] = Score(name=name)

    def updatePlayerStrategy(self, selectedStrategies, debug):
        if selectedStrategies:
            idx = 0
            for strat in selectedStrategies:
                if debug: print('strategy = {}. selectableStrategies = {}.'.format(strat,self.selectableStrategies))
                if (idx >= len(self.players)): #selected strategies are more than number of players
                    if debug: print()
                    break
                elif strat.lower() in self.selectableStrategies:
                    if debug: print('idx = {}. Strategy is applied to player {}'.format(idx, self.players[idx].getName()))
                    self.players[idx].updateStrategy(strat.lower()) 
                    self.scores[self.players[idx].getName()].updateStrategy(strat.lower())
                    idx += 1
                else:
                    print("Selected strategy '{}' for player '{}' is not part of selectable strategies {}.\nDefault strategy is applied.".format(strat,self.players[idx].getName(),self.selectableStrategies))
        else:
            if debug: print('selectedStrategies is empty')

    def setupGame(self, debug):
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
        if debug: self.show()
    
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

    def playTurn(self, player, Strategy, debug):
        if debug: print('Initial total: ', self.getStatus(player))
        while True: #Play until player's action == 0 (i.e. Stand) or until player bust.
            action = Strategy.chooseAction(player, self.dealer)
            if debug: print(f'Action = {action}')
            if action == 0:
                break
            else:
                self.hitMe(player, debug)
                if (player.getTotal() > 21):
                    if debug: print('BUSTS!', self.getStatus(player))
                    break  
            if debug: print('->NewTotal: ', self.getStatus(player))


    def play(self, MLModel, rounds = 1, debug = False ):
        MLModel.setExplorationRate(0)
        DealerModel = dealerstrategy.DealerStrategy()

        for r in range(rounds):
            #Initialize table setup to start the round
            if debug: print('\nRound {}. Will setup game and iterate over players'.format(r))
            self.setupGame(debug)
            #Players' turn
            for player in self.players:
                #Select strategy and play the turn
                if player.getStrategy() == self.selectableStrategies[0]: #Dealer's strategy
                    self.playTurn(player, DealerModel, debug)
                elif player.getStrategy() == self.selectableStrategies[1]: #Machine learning strategy
                    self.playTurn(player, MLModel, debug )
                else:
                    print("ERROR! Something went wrong.\nPlayer ({}) strategy '{}' does not exists in selectable strategies\n".format(player.getName(), player.getStrategy))
           
            #Dealer's turn
            self.playDeck.putCardOnTop(self.hiddenCardDealer)
            self.playTurn(self.dealer, DealerModel, debug )

            #Round finalized. Updates scores.
            self.updateScores()         
       
    def hitMe(self, player, debug=False):
        player.drawCard(self.playDeck.drawCard(), debug)
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

    


