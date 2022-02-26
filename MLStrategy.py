"""
The states we have are:
1. Player's total [12-21]
2. SoftHand or HardHand of the player [True, False]
3. Dealer's face-up card [2-11] (where '11' represents an Ace)

The actions, a, we have are:
1. HIT: 1
2. STAND: 0

Reward:
Win: 1
Loss: -1

player_Q_values[(pT, dT, sH)][a] = q-value

"""
import player
import BlackJack
import numpy as np
import pickle

class MLStrategy:
    def __init__(self):
        self.learning_rate = 0.05 #alpha
        self.discount_rate = 0.9

        #Epsilon-greedy strategy
        self.exploration_rate = 1 #eplison
        self.max_exploration_rate = 1
        self.min_exploration_rate = 0.05
        self.exploration_decay_rate = 0.00005

        self.actions = [1,0] #action, 1:Hit, 0:Stand

        #Initiating the player Q-function
        self.player_Q_values = {}
        for pT in range(12,22): #player total
            for dT in range (2,12): #dealer total
                for sH in [True, False]: #player has soft hand
                    self.player_Q_values[(pT,dT,sH)] = {}
                    for a in self.actions: 
                        if (pT == 21) and (a == 0):
                            self.player_Q_values[(pT,dT,sH)][a] = 10 #bias towards not hitting at 21
                        elif (pT == 21) and (a == 1):
                            self.player_Q_values[(pT,dT,sH)][a] = -15 #bias towards not hitting at 21
                        else:
                            self.player_Q_values[(pT,dT,sH)][a] = 0
        
        self.player_state_action = [] #[(pT, dT, sH)]

    def chooseAction(self, player, dealer):     
        state = (player.getTotal(), dealer.getTotal(), player.hasSoftHand())

        if state[0] < 12: #Always hit if player's total is less than 12
            return 1

        if np.random.uniform(0,1) <= self.exploration_rate:
            action = np.random.choice(self.actions)
        else: #Greedy, i.e. uses the current Q-values to determine action
            v = -1000 # 
            action = 0
            for a in self.actions:
                if self.player_Q_values[state][a] > v:
                    action = a
                    v = self.player_Q_values[state][a] 
        
        state_action_pair = [state, action]
        self.player_state_action.append(state_action_pair)
        
        return action # 1->Hit, 0->Stand
                        
    def reward(self, player, dealer, winner):

        delete = """state_action_pair = self.player_state_action.pop()
        state, action = state_action_pair

        reward = self.player_Q_values[state][action] + self.learning_rate*( winner - self.player_Q_values[state][action] )
        self.player_Q_values[state][action] += round(reward,3)

        self.player_state_action = []"""


        power = 0
        for state_action_pair in reversed(self.player_state_action):
            
            state, action = state_action_pair
            
            #calculate the reward
            if self.discount_rate == 0 and (power > 0):
                break
            reward = self.player_Q_values[state][action] + self.learning_rate*( winner*self.discount_rate**(power) - self.player_Q_values[state][action] )
            self.player_Q_values[state][action] = round(reward,3)
            
            #Increase the power to make earlier moves have smaller impact then later moves.
            power += 1
        self.player_state_action = []
    
    def train(self, rounds, debug = False, saveQValues = False):

        game = BlackJack.BlackJack()
        
        for r in range(rounds):
            if debug: print('\n--- Start of ROUND {}'.format(r+1))
            game.setupGame()

            if debug: print('Game setup. Start to play')
            if debug: print('Player starts with: ', game.getStatus(game.players[0]))

            #play one round
            while True: #Play until action == 0 (i.e. Stand) or until player bust.
                action = self.chooseAction(game.players[0], game.dealer)
                if debug: print(f'Action = {action}')
                if action == 0:
                    break
                else:
                    game.hitMe(game.players[0])
                    if (game.players[0].getTotal() > 21):
                        if debug: print('BUSTS!', game.getStatus(game.players[0]))
                        break  
                if debug: print('->NewTotal: ', game.getStatus(game.players[0]))
            game.playDealersTurn()

            #Round is now done. Decide winner and reward
            winners = game.decideWinner()
            self.reward(game.players[0], game.dealer, winners[game.players[0].getName()])
            self.updateExplorationRate(r)

            game.updateScores()
            if debug:
                print('--- End of ROUND {}'.format(r+1))
                game.show()

            if r%10000 == 0: 
                print('Round: {}....'.format(r))
                print('Exploration rate: {}'.format(self.getExplorationRate()))
                game.showScores()
                game.reinitializeScores()
        #All rounds have now been played.     
        
        #Print Q-table
        self.printDecisionTable()

            #Save Q-table to file
        if saveQValues:
            self.saveQValue()



    def updateExplorationRate(self, episode):
        self.exploration_rate = self.min_exploration_rate + (self.max_exploration_rate - self.min_exploration_rate )*np.exp(-1*self.exploration_decay_rate*episode)

    def setExplorationRate(self, expl_rate):
        self.exploration_rate = expl_rate
    
    def getExplorationRate(self):
        return self.exploration_rate
    
    def printDecisionTable(self):
        softHand = False
        for pT in range(21,11,-1):
            print("Player's Hand: {}  | ".format(pT) )
            for dT in range(2,12):
                if self.player_Q_values[(pT,dT,softHand)][1] > self.player_Q_values[(pT,dT,softHand)][0]:
                    print(' {}:H (H:{}/S:{})'.format(dT, self.player_Q_values[(pT,dT,softHand)][1], self.player_Q_values[(pT,dT,softHand)][0]),end=', ')
                else: 
                    print(' {}:S (H:{}/S:{})'.format(dT, self.player_Q_values[(pT,dT,softHand)][1], self.player_Q_values[(pT,dT,softHand)][0]),end=', ')
            print(' ')
    
    def saveQValue(self):
        f = open('trainedMLQValue.pkl','wb')
        pickle.dump(self.player_Q_values,f)
        f.close()
    
    def loadQValue(self):
        try:
            f = open('trainedMLQValue.pkl', 'rb')
            self.player_Q_values = pickle.load(f)
            f.close()
        except:
            print("""
            ERROR: The file 'trainedMLQValue.pkl' did not exists, used for loading the Q-values.
            
            Please train the model first and save down the Q-table before trying to load the Q-table.
            """)
            raise


