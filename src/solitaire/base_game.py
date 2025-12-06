# --- base_game.py ------------------------------------------------
from __future__ import annotations

from typing import Dict
import pygame as pg


class BaseVariantGame:
    """Common interface for all solitaire variants."""

    def __init__(self, screen: pg.Surface, card_images: Dict):
        self.screen = screen
        self.card_images = card_images

    def handle_event(self, event: pg.event.Event) -> None:
        raise NotImplementedError

    def update(self, dt: float) -> None:
        raise NotImplementedError

    def draw(self) -> None:
        raise NotImplementedError

    def new_game(self) -> None:
        """Start a fresh deal. Concrete variants must implement."""
        raise NotImplementedError
