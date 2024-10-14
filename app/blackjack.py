import requests

class BlackjackGame:
    def __init__(self, deck_id=None, player_hand=None, dealer_hand=None):
        self.api_base_url = "https://deckofcardsapi.com/api/deck" # Базовый URL для работы с API колоды карт
        self.deck_id = deck_id # Идентификатор текущей колоды карт
        self.player_hand = player_hand if player_hand is not None else [] # Список карт в руке игрока
        self.dealer_hand = dealer_hand if dealer_hand is not None else [] # Список карт в руке дилера

        if not self.deck_id:
            self._initialize_deck() # Инициализация новой колоды, если deck_id не указан

    def _initialize_deck(self):
        # Запрос на создание и перемешивание новой колоды
		response = requests.get(f"{self.api_base_url}/new/shuffle/?deck_count=1")
         # Преобразование ответа в формат JSON
		data = response.json()
        # Сохранение идентификатора новой колоды
		self.deck_id = data["deck_id"]

    def _draw_cards(self, count):
	# Запрос на вытягивание карт из колоды
        response = requests.get(f"{self.api_base_url}/{self.deck_id}/draw/?count={count}")
        return response.json()["cards"] # Возвращает список вытянутых карт

    def start_new_game(self):
        self.player_hand = self._draw_cards(2) # Вытягиваются две карты для игрока

    def get_player_score(self):
        return self._calculate_score(self.player_hand) # Вычисление счета для руки игрока

    def get_dealer_score(self):
        return self._calculate_score(self.dealer_hand) # Вычисление счета для руки дилера

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
                score += int(value) # Добавление числовых карт к счету
            else:
                score += card_values.get(value, 0) # Добавление очков лицевых карт
            if value == "ACE":
                ace_count += 1

        while score > 21 and ace_count:
            score -= 10  # convert an ace from 11 to 1
            ace_count -= 1 # Уменьшение счетчика тузов

        return score # Возвращение итогового счета

    def player_draw_card(self):
        card = self._draw_cards(1)[0] # Вытягивание одной карты
        self.player_hand.append(card) # Добавление карты к руке игрока
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