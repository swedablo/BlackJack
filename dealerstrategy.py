# Dealer strategy
# is to hit if total is below 17, otherwise stand.
#
# This class is created to have a interface
# between all strategies in the BlackJack class
#

class DealerStrategy:

    def __init__(self):
        self.name = "Dealer's Strategy"
        
    def chooseAction(self, player, dealer):
        action = 0
        if player.getTotal() < 17:
            action = 1
        return action # 1->Hit, 0->Stand

    def getStrategyName(self):
        return self.name