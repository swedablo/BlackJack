import BlackJack
import MLStrategy


if __name__ == '__main__':

    players     = 1

    trainRounds = 100000
    realRounds  = 150000

    #Create Machine Learning (reinforced learning) model
    model = MLStrategy.MLStrategy()
    #Train model with <trainRounds> number of rounds
    model.train(trainRounds)

    print('\nModel training is now completed!\nStarts playing real game\m')

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

