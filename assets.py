# --- assets.py
from pathlib import Path
import pygame
from typing import Dict, Tuple
from config import CARD_SIZE, SUITS, RANKS

# ---------------------------------------------------------------------------------------------------
# --- Function: assetPath()
def asset_path(*parts) -> Path:
    # adjust "assets/cards" to your actual directory
    return Path(__file__).resolve().parent / "assets" / "cards" / Path(*parts)

# --- Function: fileNameFor()
def filename_for(rank: str, suit: str) -> str:
    return f"{rank}_of_{suit}.png"      # e.g. "2_of_clubs.png", "A_of_hearts.png", "10_of_spades.png"

# --- Function: loadCardImages()
def load_card_images(size: Tuple[int,int] = CARD_SIZE) -> Dict[Tuple[str, str], pygame.Surface]:
    images: Dict[Tuple[str,str], pygame.Surface] = {}
    for suit in SUITS:
        for rank in RANKS:
            img = pygame.image.load(asset_path(filename_for(rank, suit))).convert_alpha()
            if img.get_size() != size:
                img = pygame.transform.smoothscale(img, size)
            images[(rank, suit)] = img
    return images

# --- Function: loadCardBack()
def load_card_back(name: str = "card_back_black.png") -> pygame.Surface:
    back = pygame.image.load(asset_path(name)).convert_alpha()
    if back.get_size() != CARD_SIZE:
        back = pygame.transform.smoothscale(back, CARD_SIZE)
    return back