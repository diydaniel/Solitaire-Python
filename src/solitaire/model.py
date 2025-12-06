# --- model.py ---
import pygame

from enum import Enum
from typing import List, Tuple, Dict
from .config import (
    RANK_TO_VAL,
    FOUND_SUITS
)

# ---------------------------------------------------------------------------------------------------
# Game variants
# ---------------------------------------------------------------------------------------------------

class GameVariant(Enum):
    KLONDIKE = "Klondike"
    SPIDER = "Spider"
    FREECELL = "FreeCell"
    PYRAMID = "Pyramid"
    TRIPEAKS = "TriPeaks"

# ---------------------------------------------------------------------------------------------------
# Card model
# ---------------------------------------------------------------------------------------------------

class Card:
    def __init__(self, rank: str, suit: str, image: pygame.Surface, face_up: bool = False):
        self.rank = rank
        self.suit = suit
        self.image = image
        self.face_up = face_up
        self.rect = self.image.get_rect()

    
    def draw(self, surf: pygame.Surface, x: int, y: int, back: pygame.Surface):
        self.rect.topleft = (x, y)
        surf.blit(self.image if self.face_up else back, self.rect.topleft)

# ---------------------------------------------------------------------------------------------------
# Helper functions for move legality
# ---------------------------------------------------------------------------------------------------
def is_red(suit: str) -> bool:
    """
        Returns True if the suit is red.
        Adjust if you use different suit strings in CARD filenames.
    """
    return suit in ("hearts", "diamonds")
    

def can_stack_on_tableau(dst_top: Tuple[str,str] | None, moving_top: Tuple[str,str]) -> bool:   
    
    # Purpose: Checks if a card (or a moving pile’s top card) can be placed on a tableau pile.

    """Tableau rule: alt color, descending by 1. Empty accepts K."""

    if dst_top is None:
        # Empty column: only a King may be placed
        return moving_top[0] == "K"
        
    dr, ds = dst_top
    mr, ms = moving_top

    # Colors must alternate AND rank must be exactly one less
    return (is_red(ds) != is_red(ms)) and (RANK_TO_VAL[mr] == RANK_TO_VAL[dr] - 1)

        
           

def can_stack_on_foundation(dst_top: Tuple[str, str] | None,
                            moving: Tuple[str, str],
                            slot_index: int) -> bool:
    """
        Foundation rule: must match this slot's suit and build up A -> K.

        dst_top: (rank, suit) or None  - current top card.
        moving: (rank, suit)           - card to place.
        slot_index: int                - which foundation pile (0..3), used to
                                     pick required suit from FOUND_SUITS.
    """
    mr, ms = moving
    required_suit = FOUND_SUITS[slot_index]

    # Must match this foundation's suit
    if ms != required_suit:
        return False

    # Empty foundation: must be an Ace
    if dst_top is None:
        return mr == "A"

    tr, ts = dst_top
    # Same suit, rank exactly one higher
    return (ms == ts) and (RANK_TO_VAL[mr] == RANK_TO_VAL[tr] + 1)