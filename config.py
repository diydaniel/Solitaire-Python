# --- config.py
from typing import Tuple

# --- Window
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 960 # 1280, 960...OG
GREEN = (0, 128, 0)

# --- Cards
CARD_SIZE: Tuple[int, int] = (104, 130)  # 72,96...OG: change as needed/ export to /assets.py
SUITS = ['hearts', 'diamonds', 'clubs', 'spades'] # export to /assets.py
RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K'] # export to /assets.py
RANK_TO_VAL = {r:i+1 for i,r in enumerate(RANKS)}
RED_SUITS = {'hearts','diamonds'}

# --- Layout
TABLEAU_X0, TABLEAU_Y0, TABLEAU_GAP_X = 150, 200, 150 # 100, 150, 100 OG...
FACEUP_GAP, FACEDOWN_GAP = 40, 25 # 30, 15 OG...
FOUND_X0, FOUND_Y0, FOUND_GAP_X = 625, 30, 150   # 400, 30, 150...OG: tweak positions as you like
STOCK_POS = (25, 25)    # 25, 25...OG
WASTE_POS = (150, 25)   # 125, 25...OG

# --- Foundation slots (fixed suit L->R)
FOUND_SUITS = ['hearts', 'diamonds', 'spades', 'clubs']  # left → right
SUIT_COLOR = {
    'clubs': (30,30,30), 'spades': (30,30,30),
    'hearts': (200,20,20), 'diamonds': (200,20,20),
}