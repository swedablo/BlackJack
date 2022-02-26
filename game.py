import BlackJack
import MLStrategy
import sys


if __name__ == '__main__':

    players     = 2
    realRounds  = 150000

    trainRounds = 100000
    trainModel  = True #If set to False, a loaded Q-table will be used.
    saveQValues = False #Only applicalbe if "TrainModel" is set to True. Will then save down trained Q-table to file

    #Create Machine Learning (reinforced learning) model
    model = MLStrategy.MLStrategy()
    #Train model with <trainRounds> number of rounds
    if trainModel:
        model.train(trainRounds, saveQValues = saveQValues)
        print('\nModel training is now completed!')
    else:
        try:
            model.loadQValue()
        except:
            sys.exit(1) #an exception was raised. Close the program


    print('\nStarts playing real game\n')

    #Play game according to trained model
    Game = BlackJack.BlackJack(players)

    print('Number of players equals: {}'.format(len(Game.players)))
    print('Number of rounds equals : {}\n'.format(realRounds))

    #Machine learning strategy
    print('ML strategy:')
    Game.play_MLStrategy(model, realRounds, debug=False)
    Game.showScores()
    Game.reinitializeScores()

    #Dealer Strategy
    print('Dealer strategy')
    Game.play_DealerStrategy(realRounds, debug=False)
    Game.showScores()
    Game.reinitializeScores()

