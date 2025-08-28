import pygame

class Card:
    def __init__(self, x, y, width, height, front_image, back_image, card_id):
        self.rect = pygame.Rect(x, y, width, height)
        # scale images to card size
        self.front_image = pygame.transform.scale(front_image, (width, height))
        self.back_image  = pygame.transform.scale(back_image,  (width, height))
        self.is_flipped = False
        self.is_matched = False
        self.card_id = card_id

    def draw(self, surface):
        if self.is_flipped or self.is_matched:
            surface.blit(self.front_image, self.rect)
        else:
            surface.blit(self.back_image, self.rect)

    def show(self):
        # open card (no toggle)
        if not self.is_matched:
            self.is_flipped = True

    def hide(self):
        # close only if not matched
        if not self.is_matched:
            self.is_flipped = False
