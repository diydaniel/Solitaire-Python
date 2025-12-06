# --- game.py
"""
Game dispatcher.

`Game` is the public class used by app.py. It selects the correct
variant implementation (Klondike, Spider, etc.) based on GameVariant
and delegates all calls to it.
"""

from __future__ import annotations
import pygame as pg

from .assets import load_card_images
from .model import GameVariant
from .base_game import BaseVariantGame
from .klondike import KlondikeGame
from .spider import SpiderGame


class Game:
    """
    Public game entrypoint used by app.run_one_game_session.

    app.py does:
        game = Game(screen, variant)

    This wrapper:
      - loads card images once,
      - instantiates the correct variant implementation, and
      - delegates handle_event / update / draw / new_game to it.
    """

    def __init__(self, screen: pg.Surface, variant: GameVariant):
        self.screen = screen
        self.variant = variant

        # Load card images once and share across variants
        self.card_images = load_card_images()

        if variant == GameVariant.KLONDIKE:
            self._impl: BaseVariantGame = KlondikeGame(screen, self.card_images)
        elif variant == GameVariant.SPIDER:
            self._impl = SpiderGame(screen, self.card_images)
        else:
            raise ValueError(f"Unsupported game variant: {variant!r}")

    def handle_event(self, event: pg.event.Event) -> None:
        self._impl.handle_event(event)

    def update(self, dt: float) -> None:
        self._impl.update(dt)

    def draw(self) -> None:
        self._impl.draw()

    def new_game(self) -> None:
        """Start a fresh deal for the current variant."""
        self._impl.new_game()
