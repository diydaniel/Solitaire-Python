# --- config.py
from __future__ import annotations
from typing import Tuple
import pygame as pg

pg.init()

GREEN = (0, 128, 0)

# Base sizes (single game window size)
BASE_SCREEN = (1520, 1320)
BASE_CARD_SIZE = (115, 160)

SUITS = ["hearts", "diamonds", "clubs", "spades"]
RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
RANK_TO_VAL = {r: i + 1 for i, r in enumerate(RANKS)}
RED_SUITS = {"hearts", "diamonds"}

FOUND_SUITS = ["clubs", "diamonds", "hearts", "spades"]
SUIT_COLOR = {
    "clubs": (20, 20, 20),
    "spades": (20, 20, 20),
    "hearts": (220, 40, 40),
    "diamonds": (220, 40, 40),
}

# ---------- single “preset” just to satisfy imports ----------
class WindowPreset:
    MEDIUM = "medium"   # only one we actually use

# ---------- globals used by the game ----------
SCREEN_WIDTH, SCREEN_HEIGHT = BASE_SCREEN
CARD_SIZE: Tuple[int, int] = BASE_CARD_SIZE

TABLEAU_COLS = 7
TABLEAU_GAP_X = 0
TABLEAU_STEP_X = 0
TABLEAU_X0 = 0
TABLEAU_Y0 = 0

FOUND_GAP_X = 0
FOUND_STEP_X = 0
FOUND_X0 = 0
FOUND_Y0 = 0

TOP_ROW_Y = 25
FACEUP_GAP = 30
FACEDOWN_GAP = 10

STOCK_POS: Tuple[int, int] = (0, 0)
WASTE_POS: Tuple[int, int] = (0, 0)


def _rebuild_layout() -> None:
    """
    Compute layout once for the fixed 1280x900 window.
    Cards and piles are centered and spaced nicely.
    """
    global TABLEAU_GAP_X, TABLEAU_STEP_X, TABLEAU_X0, TABLEAU_Y0
    global FOUND_GAP_X, FOUND_STEP_X, FOUND_X0, FOUND_Y0
    global TOP_ROW_Y, STOCK_POS, WASTE_POS

    card_w, card_h = CARD_SIZE

    # ----- TABLEAU (7 columns) -----
    cols = TABLEAU_COLS

    # fixed-ish gap relative to card width
    TABLEAU_GAP_X = int(card_w * 0.6)
    TABLEAU_STEP_X = card_w + TABLEAU_GAP_X

    tableau_width = cols * card_w + (cols - 1) * TABLEAU_GAP_X
    TABLEAU_X0 = (SCREEN_WIDTH - tableau_width) // 2
    TABLEAU_Y0 = int(SCREEN_HEIGHT * 0.35)

    # ----- TOP ROW (stock, waste, 4 foundations) -----
    TOP_ROW_Y = int(SCREEN_HEIGHT * 0.12)

    gap_stock_waste = int(card_w * 0.25)
    gap_waste_found = int(card_w * 1.0)
    FOUND_GAP_X = int(card_w * 0.55)
    FOUND_STEP_X = card_w + FOUND_GAP_X

    top_row_width = (
        2 * card_w               # stock + waste
        + gap_stock_waste
        + gap_waste_found
        + 4 * card_w             # 4 foundations
        + 3 * FOUND_GAP_X
    )

    top_x0 = (SCREEN_WIDTH - top_row_width) // 2

    STOCK_POS = (top_x0, TOP_ROW_Y)
    WASTE_POS = (STOCK_POS[0] + card_w + gap_stock_waste, TOP_ROW_Y)

    FOUND_X0 = WASTE_POS[0] + card_w + gap_waste_found
    FOUND_Y0 = TOP_ROW_Y


def set_window_preset(preset: str) -> Tuple[int, int, int]:
    """
    Kept for compatibility with app.py, but always returns the single
    fixed window size and card size.
    """
    global SCREEN_WIDTH, SCREEN_HEIGHT, CARD_SIZE

    SCREEN_WIDTH, SCREEN_HEIGHT = BASE_SCREEN
    CARD_SIZE = BASE_CARD_SIZE
    flags = 0  # no FULLSCREEN, no RESIZABLE

    _rebuild_layout()
    return flags, SCREEN_WIDTH, SCREEN_HEIGHT


# initialize once
set_window_preset(WindowPreset.MEDIUM)
