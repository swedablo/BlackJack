import random

class Card:
    def __init__(self, val, suit):
        self.value = val
        self.suit = suit

    def show(self):
        return "{} of {}".format(self.value, self.suit)

    def __str__(self):
        return self.show()

    def getValue(self):
        return self.value

class Deck:
    def __init__(self):
        self.cards = []
        self.buildDeck()
        self.shuffle()

    def buildDeck(self):
        suits = ['Spades', "Clubs", "Diamonds", "Hearts"]
        values = [1,2,3,4,5,6,7,8,9,10,10,10,10]
        for s in suits:
            for v in values:
                self.cards.append(Card(v,s))
    
    def show(self):
        for c in self.cards:
            print(c.show())

    def reinitializeDeck(self):
        self.cards = []
        self.buildDeck()

    def shuffle(self):
        random.shuffle(self.cards)
    
    def drawCard(self):
        return self.cards.pop()
    
    def putCardOnTop(self, card):
        self.cards.append(card)

    def getCardsLeft(self):
        return len(self.cards)

if __name__ == '__main__':
    print('---Creating deck')
    deck = Deck()
    deck.show()

    card = deck.drawCard()
    print('---my card is {}'.format(card.show()))
#    deck.cards.append(card)
    card = deck.drawCard()
    print('---my card is {}'.format(card.show()))

    for i in range(10,1,-1):
        print(i)



