import deck

class Player:

    def __init__(self, name, strategy):
        self.name = name
        self.strategy = strategy
        self.clearTotal()

    def updateStrategy(self,strategy):
        self.strategy = strategy

    def drawCard(self, newCard, debug=False):
        self.cards.append(newCard)
        cardValue = self.cards[-1].getValue()
        if debug: print('Player class: newCard = {}. CardValue = {}'.format(newCard.show(), cardValue))
        if cardValue == 1 and (self.totalHand + 11 <= 21): #an Ace was drawn and can be used as a soft Ace.
            self.softHand = True
            self.totalHand += 11
        elif self.softHand and (self.totalHand + cardValue > 21):
            self.softHand = False
            self.totalHand += cardValue - 10 #Ace is counted as "1" instead of "11"
        else:
            self.totalHand += cardValue
    
    def clearTotal(self):
        self.softHand = False
        self.totalHand = 0
        self.cards = []

    def hasSoftHand(self):
        """Returns true if player has a soft hand soft hand"""
        return self.softHand

    def hasBlackJack(self):
        return (self.totalHand == 21) and (len(self.cards) == 2)

    def getTotal(self):
        return self.totalHand
    
    def getName(self):
        return self.name

    def getStrategy(self):
        return self.strategy

    def showHand(self):        
        return [str(c) for c in self.cards]


    



