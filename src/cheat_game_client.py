import random
from math import exp
from collections import defaultdict

from cheat_game_server import Game
from cheat_game_server import Player, Human
from cheat_game_server import Claim, Take_Card, Cheat, Call_Cheat
from cheat_game_server import Rank, Suit, Card
from cheat_game_server import ActionEnum

class Agent(Player):
    def __init__(self, name):
        super(Agent, self).__init__(name)

    def make_claim(self, cards, claim):
        print 'making claim: {0:1d} cards of rank {1}'.format(claim.count, str(claim.rank))
        super(Agent, self).make_claim(cards, claim)

    def make_honest_claim(self, claim):
        super(Agent, self).make_honest_claim(claim)

    def take_card_from_deck(self, silent=False):
        if not silent: print 'Taking Card from deck'
        super(Agent, self).take_card_from_deck()

    def call_cheat(self):
        print 'Calling "Cheat!"'
        super(Agent, self).call_cheat()

    def make_move(self):
        print
        print 'Player {0:1d} ({1:s}) turn'.format(self.id, self.name)
        print "================"+"="*len(self.name)
        honest_moves = self.possible_honest_moves()
        state = self.game.get_state()
        opponent_count = state[3 - self.id]
        deck_count = state['DECK']
        table_count = state['TABLE']
        last_action = state['LAST_ACTION']
        cards_revealed = state['CARDS_REVEALED']
        last_claim = self.game.last_claim()
        # if opponent placed his last cards on the table - call_cheat or lose
        action = self.agent_logic(deck_count, table_count, opponent_count,
                                  last_action, last_claim, honest_moves, cards_revealed)
        assert action in honest_moves or isinstance(action, Cheat)
        if isinstance(action, Call_Cheat):
            self.call_cheat()
        elif isinstance(action, Claim):
            self.make_honest_claim(action)
        elif isinstance(action, Take_Card):
            self.take_card_from_deck()
        elif isinstance(action, Cheat):
            self.make_claim(action.cards, Claim(action.rank, action.count))


class DemoAgent(Agent):
    def __init__(self, name):
        super(DemoAgent, self).__init__(name)
        self.cheat_prob = {"NO_MOVES": 0.6, "AVAIL_CLAIMS": 0.1}
        self.call_cheat_prob = {1: 0.06, 2: 0.011, 3: 0.28, 4: 0.47}

    def agent_logic(self, deck_count, table_count, opponent_count,
                    last_action, last_claim, honest_moves, cards_revealed):
        """
        This function implements action logic / move selection for the agent\n
        :param deck_count:
        :param table_count:
        :param opponent_count:
        :param last_action: ActionEnum.TAKE_CARD or .MAKE_CLAIM or .CALL_CHEAT
        :param last_claim:
        :param honest_moves: a list of available actions, other than making a false ("cheat") claim
        :param cards_revealed: if last action was "call cheat" cards on table were revealed
        :return: Action object Call_Cheat or Claim or Take_Card or Cheat
        """
        scores = {}
        if opponent_count == 0:
            return Call_Cheat()
        available_claim = False
        for move in honest_moves:
            if isinstance(move, Claim):
                scores[move] = move.count
                available_claim = True
            elif isinstance(move, Take_Card):
                scores[move] = 0.6
            elif isinstance(move, Call_Cheat):
                if last_claim:
                    scores[move] = self.call_cheat_prob[last_claim.count]
                else:
                    scores[move] = 0.0
        if available_claim:
            scores[Cheat()] = self.cheat_prob["AVAIL_CLAIMS"]
        else:
            scores[Cheat()] = self.cheat_prob["NO_MOVES"]
        # randomize scores add random \in [-0.5..0.5)
        for move, score in scores.iteritems():
            scores[move] = score + 0.5 * (2.0 * random.random() - 1)
        # select move based on max score
        move = max(scores, key=scores.get)
        if isinstance(move, Take_Card):
            return move
        elif isinstance(move, Call_Cheat):
            return move
        elif isinstance(move, Claim):
            return move
        elif isinstance(move, Cheat):
            top_rank = self.table.top_rank()
            rank_above = Rank.above(top_rank)
            rank_below = Rank.below(top_rank)
            rank_above_score = rank_below_score = 0
            # choose cheat rank based on distance to remaining agent's card
            for card in self.cards:
                rank_above_score += card.rank.dist(rank_above)
                rank_below_score += card.rank.dist(rank_below)
            if rank_above_score < rank_below_score:
                cheat_rank = rank_above
            else:
                cheat_rank = rank_below
            cheat_count = 1
            # decaying function of number of cards on the table - cheat less when risk is large
            r = 0.5 * exp(-0.1 * table_count)
            while cheat_count < 4 and random.random() < r and len(self.cards) >= (cheat_count + 1):
                cheat_count += 1
            # select cards furthest from current claim rank
            dist = defaultdict(int)
            for ind, card in enumerate(self.cards):
                dist[card] = cheat_rank.dist(card.rank)
            claim_cards = sorted(dist, key=dist.get)[:cheat_count]
            return Cheat(claim_cards, cheat_rank, cheat_count)
            
            
class TrackingDemoAgent(Agent):
    def __init__(self, name):
        super(TrackingDemoAgent, self).__init__(name)
        self.cheat_prob = {"NO_MOVES": 0.6, "AVAIL_CLAIMS": 0.1}
        self.call_cheat_prob = {1: 0.06, 2: 0.11, 3: 0.28, 4: 0.47}

        self.cards_placed  = []
        self.cards_opponent_claimed = []
        self.cards_my_claimed = []

    def calculateScore(self, honest_moves, last_claim):
        available_claim = False
        self.scores = {}
        for move in honest_moves:
            if isinstance(move, Claim):
                self.scores[move] = move.count
                available_claim = True
            elif isinstance(move, Take_Card):
                self.scores[move] = 0.6
            elif isinstance(move, Call_Cheat):
                if last_claim:
                    self.scores[move] = self.call_cheat_prob[last_claim.count]
                else:
                    self.scores[move] = 0.0
        if available_claim:
            self.scores[Cheat()] = self.cheat_prob["AVAIL_CLAIMS"]
        else:
            self.scores[Cheat()] = self.cheat_prob["NO_MOVES"]

    def pickMoveFromScore(self):
        # randomize scores add random \in [-0.5..0.5)
        for move, score in self.scores.iteritems():
            self.scores[move] = score + 0.5 * (2.0 * random.random() - 1)
        # select move based on max score
        return max(self.scores, key=self.scores.get)
    def agent_logic(self, deck_count, table_count, opponent_count,
                    last_action, last_claim, honest_moves, cards_revealed):
        """
        This function implements action logic / move selection for the agent\n
        :param deck_count:
        :param table_count:
        :param opponent_count:
        :param last_action: ActionEnum.TAKE_CARD or .MAKE_CLAIM or .CALL_CHEAT
        :param last_claim:
        :param honest_moves: a list of available actions, other than making a false ("cheat") claim
        :param cards_revealed: if last action was "call cheat" cards on table were revealed
        :return: Action object Call_Cheat or Claim or Take_Card or Cheat
        """
        if opponent_count == 0:
            return Call_Cheat()


        if last_claim:
            self.cards_opponent_claimed.append(last_claim)
        self.calculateScore(honest_moves,last_claim)


        if last_action == ActionEnum.CALL_CHEAT:
            self.cards_placed = []
            self.cards_opponent_claimed = []
            self.cards_my_claimed = []
        self.print_expected_cards()

        if last_claim:
            amount_of_rank = 0
            for card in self.cards_placed:
                if card.rank == last_claim.rank:
                    amount_of_rank += card.count
            for card in self.cards:
                if card.rank == last_claim.rank:
                    amount_of_rank += 1

            if amount_of_rank + last_claim.count > 4:
                return Call_Cheat()
            else:
                for card in self.cards_opponent_claimed:
                   if card.rank == last_claim.rank:
                       amount_of_rank += card.count
                if amount_of_rank + last_claim.count > 4:
                   probabilityCallCheat = random.randrange(100)
                   if probabilityCallCheat > 50 * (0 if 1/(table_count) == 0 else table_count):
                      return Call_Cheat()

        move = self.pickMoveFromScore()

        #has only one card - use special strategy
        
        if len(self.cards):
        if isinstance(move, Take_Card):
            return move
        elif isinstance(move, Call_Cheat):
            return move
        elif isinstance(move, Claim):
            self.cards_placed.append(move)
            self.cards_my_claimed.append(move)
            return move
        elif isinstance(move, Cheat):
            top_rank = self.table.top_rank()
            rank_above = Rank.above(top_rank)
            rank_below = Rank.below(top_rank)
            rank_above_score = rank_below_score = 0
            # choose cheat rank based on distance to remaining agent's card
            for card in self.cards:
                rank_above_score += card.rank.dist(rank_above)
                rank_below_score += card.rank.dist(rank_below)
            if rank_above_score < rank_below_score:
                possible = self.possible_cheat(rank_above, 1)
                if possible == 0:
                   cheat_rank = rank_above
                else:
                   cheat_rank = rank_below
            else:
                possible = self.possible_cheat(rank_below, 1)
                if possible == 0:
                   cheat_rank = rank_below
                else:
                   cheat_rank = rank_above
            cheat_count = 1
            # decaying function of number of cards on the table - cheat less when risk is large
            r = 0.5 * exp(-0.1 * table_count)
            possible_continue = 0
            while random.random() < r and \
                            len(self.cards) >= (cheat_count + 1) and \
                            possible_continue == 0 and \
                            cheat_count < 4:
                possible = self.possible_cheat(cheat_rank, cheat_count)
                if possible != 0:
                   probabilityCallCheat = random.randrange(100)
                   if probabilityCallCheat > 40:
                       possible_continue = 1
                   else:
                       cheat_count += 1
            # select cards furthest from current claim rank
            dist = defaultdict(int)
            for ind, card in enumerate(self.cards):
                dist[card] = cheat_rank.dist(card.rank)
            claim_cards = sorted(dist, key=dist.get)[:cheat_count]
            move = Cheat(claim_cards, cheat_rank, cheat_count)
            self.cards_my_claimed.append(Claim(cheat_rank, cheat_count))
            for card in claim_cards:
                self.cards_placed.append(Claim(card.rank, 1))
            return move

    def call_cheat(self):
        self.cards_placed = []
        self.cards_opponent_claimed = []
        self.cards_my_claimed = []
        super(TrackingDemoAgent, self).call_cheat()

    def possible_cheat(self, rank_given, num):
        amount_of_rank = 0
        for card in self.cards_my_claimed:
            if card.rank == rank_given:
                 amount_of_rank += card.count
        if amount_of_rank + num > 4:
            return 0
        else:
            return 1

    def print_expected_cards(self):
        print "Opponent Claims:"
        for c in self.cards_opponent_claimed:
            print "\t{0}".format(c)
        print "Cards Placed By Player:"
        for c in self.cards_placed:
            print "\t{0}".format(c)

cheat = Game(TrackingDemoAgent("Demo 1"), TrackingDemoAgent("me"))
cheat.play()
