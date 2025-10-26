# --- model.py ---
import pygame

# --- Object: Card --- model.py
class Card:
    def __init__(self, rank: str, suit: str, image: pygame.Surface, face_up: bool = False):
        self.rank = rank
        self.suit = suit
        self.image = image
        self.face_up = face_up
        self.rect = self.image.get_rect()

    # --- Function: draw() --- model.py
    def draw(self, surf: pygame.Surface, x: int, y: int, back: pygame.Surface):
        self.rect.topleft = (x, y)
        surf.blit(self.image if self.face_up else back, self.rect.topleft)