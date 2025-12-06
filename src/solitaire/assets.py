# --- assets.py
from pathlib import Path
from typing import Dict, Tuple
import pygame
from importlib import resources

from .config import CARD_SIZE, RANKS, SUITS


def _cards_dir():
    """
    Return a Traversable object for the cards directory bundled with the package.
    This works whether the package is installed normally or in editable mode.
    """
    # solitaire/assets/cards
    return Path(__file__).parent / "assets" / "cards"


def load_card_images(size: Tuple[int, int] = CARD_SIZE) -> Dict[Tuple[str, str], pygame.Surface]:
    """
    Load all *valid* card face images into a dict keyed by (rank, suit).

    Expected filename format:
        "<rank>_of_<suit>.png"
    e.g. "A_of_spades.png", "10_of_hearts.png"

    Only cards where rank ∈ RANKS and suit ∈ SUITS are kept.
    Back images / demo images are skipped.
    """
    images: Dict[Tuple[str, str], pygame.Surface] = {}
    cards_dir = _cards_dir()

    for path in cards_dir.iterdir():
        name = path.name
        lower = name.lower()

        # Skip card backs, demo images, screenshots, etc.
        if "back" in lower or "demo" in lower or "screenshot" in lower:
            continue

        if "_of_" not in name or not name.endswith(".png"):
            continue

        # Parse "A_of_spades.png" -> rank="A", suit="spades"
        rank_part, suit_part_ext = name.split("_of_", 1)
        suit_part = suit_part_ext[:-4]  # strip ".png"

        rank = rank_part
        suit = suit_part

        if rank not in RANKS or suit not in SUITS:
            print(f"[load_card_images] Skipping unknown card asset: {name}")
            continue

        key = (rank, suit)
        if key in images:
            print(f"[load_card_images] Duplicate asset for {key}: {name} (skipping)")
            continue

        # resources.as_file gives us a real filesystem path even from a wheel/zip
        with resources.as_file(path) as fs_path:
            surf = pygame.image.load(str(fs_path)).convert_alpha()

        if surf.get_size() != size:
            surf = pygame.transform.smoothscale(surf, size)

        images[key] = surf

    print(f"[load_card_images] Loaded {len(images)} unique card faces from package assets.")
    return images


def load_card_back(name: str = "card_back_black.png") -> pygame.Surface:
    """
    Load the back-of-card image and scale it to CARD_SIZE if needed.
    """
    cards_dir = _cards_dir()
    back_path = cards_dir / name

    if not back_path.exists():
        raise FileNotFoundError(f"Missing card back image: {back_path}")

    with resources.as_file(back_path) as fs_path:
        back = pygame.image.load(str(fs_path)).convert_alpha()

    if back.get_size() != CARD_SIZE:
        back = pygame.transform.smoothscale(back, CARD_SIZE)

    return back
