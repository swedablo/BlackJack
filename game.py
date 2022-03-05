import blackjack
import mlstrategy
import sys


if __name__ == '__main__':

    players     = 4
    strategies  = ['mlstrategy', 'mlstrategy', 'dealerstrategy'] #Select the strategy you want each player to adhere to. Default is dealer's strategy.
    realRounds  = 100000


    trainRounds = 250000
    trainModel  = True #If set to False, a loaded Q-table will be used.
    saveQValues = False #Only applicalbe if "TrainModel" is set to True. Will then save down trained Q-table to file

    #Create Machine Learning (reinforced learning) model
    model = mlstrategy.MLStrategy()
    #Train model with <trainRounds> number of rounds
    if trainModel:
        model.train(trainRounds, saveQValues = saveQValues)
        print('\nModel training is now completed!')
    else:
        try:
            model.loadQValue()
        except:
            sys.exit(1) #an exception was raised. Close the program


    print('\nStarts playing real game:\n')

    #Play game according to trained model
    Game = blackjack.BlackJack(players, strategies, debug=False)

    print('Number of players equals: {}'.format(len(Game.players)))
    print('Number of rounds equals : {}\n'.format(realRounds))

    #Mixed strategies
    print('\n---Mixed Strategies---')
    Game.play(model, realRounds, debug=False)
    Game.showScores()
    Game.reinitializeScores()



