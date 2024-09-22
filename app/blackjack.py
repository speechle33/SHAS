import requests

class BlackjackGame:
    def __init__(self, deck_id=None, player_hand=None, dealer_hand=None):
        self.api_base_url = "https://deckofcardsapi.com/api/deck"
        self.deck_id = deck_id
        self.player_hand = player_hand if player_hand is not None else []
        self.dealer_hand = dealer_hand if dealer_hand is not None else []

        if not self.deck_id:
            self._initialize_deck()

    def _initialize_deck(self):
        response = requests.get(f"{self.api_base_url}/new/shuffle/?deck_count=1")
        data = response.json()
        self.deck_id = data["deck_id"]

    def _draw_cards(self, count):
        response = requests.get(f"{self.api_base_url}/{self.deck_id}/draw/?count={count}")
        return response.json()["cards"]

    def start_new_game(self):
        self.player_hand = self._draw_cards(2)

    def get_player_score(self):
        return self._calculate_score(self.player_hand)

    def get_dealer_score(self):
        return self._calculate_score(self.dealer_hand)

    def _calculate_score(self, hand):
        score = 0
        ace_count = 0
        card_values = {
            "JACK": 10,
            "QUEEN": 10,
            "KING": 10,
            "ACE": 11  # initially consider the ace as 11
        }

        for card in hand:
            value = card["value"]
            if value.isdigit():
                score += int(value)
            else:
                score += card_values.get(value, 0)
            if value == "ACE":
                ace_count += 1

        while score > 21 and ace_count:
            score -= 10  # convert an ace from 11 to 1
            ace_count -= 1

        return score

    def player_draw_card(self):
        card = self._draw_cards(1)[0]
        self.player_hand.append(card)
        return card

    def dealer_draw_card(self):
        card = self._draw_cards(1)[0]
        self.dealer_hand.append(card)
        return card

    def get_game_state(self):
        return {
            "deck_id": self.deck_id,
            "player_hand": self.player_hand,
            "player_score": self.get_player_score(),
            "dealer_hand": self.dealer_hand,
            "dealer_score": self.get_dealer_score(),
        }

    def is_player_busted(self):
        return self.get_player_score() > 21

    def is_dealer_busted(self):
        return self.get_dealer_score() > 21

    def should_dealer_draw(self):
        return self.get_dealer_score() < 17