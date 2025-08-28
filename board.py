import pygame
import random
import time
from .card import Card

class Board:
    def __init__(self, screen, rows, cols, card_images, back_image, sounds):
        self.screen = screen
        self.rows = rows
        self.cols = cols
        self.sounds = sounds or {}

        # ----- Layout calc -----
        W, H = self.screen.get_size()
        top_ui = 110   # reserve top UI space for timer/moves/hints
        margin = 30
        gap = 12

        max_w = (W - 2*margin - (cols - 1)*gap) // cols
        max_h = (H - top_ui - 2*margin - (rows - 1)*gap) // rows
        card_w = card_h = min(max_w, max_h)
        self.card_w, self.card_h = int(card_w), int(card_h)

        grid_w = cols * self.card_w + (cols - 1) * gap
        grid_h = rows * self.card_h + (rows - 1) * gap
        self.start_x = (W - grid_w) // 2
        self.start_y = top_ui + (H - top_ui - grid_h) // 2
        self.gap = gap

        # ----- Build deck -----
        needed_pairs = (rows * cols) // 2
        if len(card_images) < needed_pairs:
            raise ValueError(f"Need at least {needed_pairs} unique images in Assets/images/")

        base = card_images[:needed_pairs]
        deck = []
        for idx, img in enumerate(base):
            deck.append((idx, img))
            deck.append((idx, img))
        random.shuffle(deck)

        # ----- Create cards -----
        self.cards = []
        k = 0
        for r in range(rows):
            for c in range(cols):
                x = self.start_x + c * (self.card_w + self.gap)
                y = self.start_y + r * (self.card_h + self.gap)
                card_id, front_img = deck[k]
                k += 1
                self.cards.append(Card(x, y, self.card_w, self.card_h, front_img, back_image, card_id))

        # Matching state
        self.first = None
        self.second = None
        self.hide_time = None
        self.matched_pairs = 0
        self.total_pairs = needed_pairs

        # Hint system
        self.hints_left = 3
        self.hint_time = None  # timestamp when hint should stop

    def draw(self, surface):
        # handle hide mismatch after delay
        if self.hide_time and time.time() >= self.hide_time:
            self.first.hide()
            self.second.hide()
            self.first, self.second = None, None
            self.hide_time = None

        # handle hint expiration (non-blocking)
        if self.hint_time and time.time() >= self.hint_time:
            # unflip any non-matched cards that were flipped by hint
            for card in self.cards:
                if not card.is_matched:
                    card.hide()
            self.hint_time = None

        for card in self.cards:
            card.draw(surface)

    def _card_at_pos(self, pos):
        for card in self.cards:
            if card.rect.collidepoint(pos):
                return card
        return None

    def handle_click(self, pos):
        # if currently waiting to hide mismatch or hint is active, ignore clicks
        if self.hide_time or self.hint_time:
            return False

        card = self._card_at_pos(pos)
        if card is None or card.is_matched or card.is_flipped:
            return False

        card.show()
        if 'flip.wav' in self.sounds:
            try:
                self.sounds['flip.wav'].play()
            except Exception:
                pass

        if self.first is None:
            self.first = card
            return True
        else:
            self.second = card
            self._check_match()
            return True

    def _check_match(self):
        if self.first and self.second:
            if self.first.card_id == self.second.card_id:
                # Match
                self.first.is_matched = True
                self.second.is_matched = True
                self.matched_pairs += 1
                if 'match.wav' in self.sounds:
                    try:
                        self.sounds['match.wav'].play()
                    except Exception:
                        pass
                self.first, self.second = None, None
            else:
                # Mismatch: wait 0.7 sec before hiding
                self.hide_time = time.time() + 0.7

    def reveal_all_temp(self, duration=2.0):
        """Reveal all cards for `duration` seconds (non-blocking)."""
        # Only allow hint if some hints left and no pending hide/mismatch
        if self.hints_left <= 0 or self.hide_time or self.hint_time:
            return

        # Flip all not-matched cards
        for card in self.cards:
            card.show()
        self.hints_left -= 1
        self.hint_time = time.time() + duration

    def is_finished(self):
        return self.matched_pairs == self.total_pairs
