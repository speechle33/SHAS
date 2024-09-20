import random

class BlackjackGame:
    def __init__(self):
        self.deck = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11] * 4
        random.shuffle(self.deck)
        self.dealer_hand = []
        self.player_hand = []
        self.deal_initial()

    def deal_initial(self):
        self.player_hand.append(self.deck.pop())
        self.dealer_hand.append(self.deck.pop())
        self.player_hand.append(self.deck.pop())
        self.dealer_hand.append(self.deck.pop())

    def hit(self, hand):
        hand.append(self.deck.pop())

    def calculate_score(self, hand):
        score = sum(hand)
        if score > 21 and 11 in hand:
            hand.remove(11)
            hand.append(1)
            score = sum(hand)
        return score

    def get_game_state(self):
        return {
            'dealer_hand': self.dealer_hand,
            'player_hand': self.player_hand,
            'dealer_score': self.calculate_score(self.dealer_hand),
            'player_score': self.calculate_score(self.player_hand),
        }

    def is_over(self):
        player_score = self.calculate_score(self.player_hand)
        dealer_score = self.calculate_score(self.dealer_hand)
        if player_score > 21:
            return 'player_bust'
        elif dealer_score > 21:
            return 'dealer_bust'
        elif player_score == 21 or dealer_score == 21:
            return 'blackjack'
        return None