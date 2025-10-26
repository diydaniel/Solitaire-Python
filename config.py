# --- config.py ---
from typing import Tuple

# --- Window --- config.py
SCREEN_WIDTH, SCREEN_HEIGHT = 1024, 768
GREEN = (0, 128, 0)

# --- Cards --- config.py
CARD_SIZE: Tuple[int, int] = (72, 96)  # change as needed/ export to /assets.py
SUITS = ['hearts', 'diamonds', 'clubs', 'spades'] # export to /assets.py
RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K'] # export to /assets.py
RANK_TO_VAL = {r:i+1 for i,r in enumerate(RANKS)}
RED_SUITS = {'hearts','diamonds'}

# --- Layout --- config.py
TABLEAU_X0, TABLEAU_Y0, TABLEAU_GAP_X = 100, 150, 100
FACEUP_GAP, FACEDOWN_GAP = 30, 15
FOUND_X0, FOUND_Y0, FOUND_GAP_X = 400, 30, 150   # tweak positions as you like
STOCK_POS = (25, 25)
WASTE_POS = (125, 25)

# --- Foundation slots (fixed suit L->R) --- config.py
FOUND_SUITS = ['clubs', 'diamonds', 'hearts', 'spades']  # left → right
SUIT_COLOR = {
    'clubs': (30,30,30), 'spades': (30,30,30),
    'hearts': (200,20,20), 'diamonds': (200,20,20),
}