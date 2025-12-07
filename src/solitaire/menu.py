# --- menu.py ---------------------------------------------------
import math
from enum import Enum, auto
from typing import List, Tuple

import pygame as pg

from .model import GameVariant


FONT_SIZE_TITLE = 48
FONT_SIZE_BUTTON = 32
FONT_SIZE_SMALL = 20
FPS = 60


class MenuResult(Enum):
    START = auto()
    QUIT = auto()


class Button:
    def __init__(self, rect: pg.Rect, text: str, font: pg.font.Font, on_click):
        self.rect = rect
        self.text = text
        self.font = font
        self.on_click = on_click
        self.hover = False

    def draw(self, surf: pg.Surface, disabled: bool = False):
        if disabled:
            bg = (55, 55, 65)
            border = (110, 110, 130)
            text_col = (170, 170, 190)
        else:
            bg = (60, 60, 70) if not self.hover else (85, 85, 110)
            border = (200, 200, 220)
            text_col = (240, 240, 250)

        pg.draw.rect(surf, bg, self.rect, border_radius=12)
        pg.draw.rect(surf, border, self.rect, width=2, border_radius=12)
        label = self.font.render(self.text, True, text_col)
        surf.blit(label, label.get_rect(center=self.rect.center))

    def handle_event(self, event: pg.event.Event, disabled: bool = False):
        if disabled:
            self.hover = False
            return

        if event.type == pg.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif (
            event.type == pg.MOUSEBUTTONDOWN
            and event.button == 1
            and self.hover
        ):
            self.on_click()


class Menu:
    def __init__(self, screen: pg.Surface,
                 title: str = "Solitaire  •  codejacket.io"):
        self.screen = screen
        self.title = title
        self.clock = pg.time.Clock()
        self.result: MenuResult | None = None

        # ---- state ----
        # game variant
        self.variants: List[GameVariant] = [
            GameVariant.KLONDIKE,
            GameVariant.SPIDER,
        ]
        self.variant_index = 0
        self.selected_variant = self.variants[self.variant_index]

        # spider difficulty (number of suits)
        # 1, 2, 4 suits — for now your Spider implementation uses 1 suit
        self.spider_modes: List[Tuple[int, str]] = [
            (1, "Spider: 1 suit (easy)"),
            (2, "Spider: 2 suits (medium)"),
            (4, "Spider: 4 suits (hard)"),
        ]
        self.spider_mode_index = 0
        self.selected_spider_suits: int = self.spider_modes[
            self.spider_mode_index
        ][0]

        # dropdown state
        self.variant_dropdown_open = False
        self.spider_dropdown_open = False

        # fonts
        self.title_font = pg.font.SysFont("arial", FONT_SIZE_TITLE, bold=True)
        self.button_font = pg.font.SysFont("arial", FONT_SIZE_BUTTON)
        self.small_font = pg.font.SysFont("arial", FONT_SIZE_SMALL)

        # create buttons with horizontal layout
        self._init_buttons()

    # ------------------------------------------------------------------ #
    # layout helpers
    # ------------------------------------------------------------------ #
    def _init_buttons(self) -> None:
        w, h = self.screen.get_size()

        row_y = int(h * 0.55)
        gap_x = 24

        # fixed widths (feel free to tweak)
        variant_w = 260
        spider_w = 280
        start_w = 180
        quit_w = 140
        btn_h = 60

        total_w = variant_w + spider_w + start_w + quit_w + 3 * gap_x
        start_x = (w - total_w) // 2

        # rects
        variant_rect = pg.Rect(start_x, row_y, variant_w, btn_h)
        spider_rect = pg.Rect(
            variant_rect.right + gap_x, row_y, spider_w, btn_h
        )
        start_rect = pg.Rect(spider_rect.right + gap_x, row_y, start_w, btn_h)
        quit_rect = pg.Rect(start_rect.right + gap_x, row_y, quit_w, btn_h)

        # callbacks
        def toggle_variant_dd():
            # open/close variant dropdown; close spider dropdown
            self.variant_dropdown_open = not self.variant_dropdown_open
            if self.variant_dropdown_open:
                self.spider_dropdown_open = False

        def toggle_spider_dd():
            # only useful when Spider is selected
            if self.selected_variant is not GameVariant.SPIDER:
                return
            self.spider_dropdown_open = not self.spider_dropdown_open
            if self.spider_dropdown_open:
                self.variant_dropdown_open = False

        def start_game():
            self.result = MenuResult.START

        def quit_game():
            self.result = MenuResult.QUIT

        # buttons
        self.variant_button = Button(
            variant_rect,
            self._variant_button_label(),
            self.button_font,
            toggle_variant_dd,
        )

        self.spider_button = Button(
            spider_rect,
            self._spider_button_label(),
            self.button_font,
            toggle_spider_dd,
        )

        self.start_button = Button(
            start_rect, "Start Game", self.button_font, start_game
        )
        self.quit_button = Button(
            quit_rect, "Quit", self.button_font, quit_game
        )

    # ------------------------------------------------------------------ #
    # label helpers
    # ------------------------------------------------------------------ #
    def _variant_button_label(self) -> str:
        if self.selected_variant == GameVariant.KLONDIKE:
            return "Variant: Klondike"
        elif self.selected_variant == GameVariant.SPIDER:
            return "Variant: Spider"
        return "Variant"

    def _spider_button_label(self) -> str:
        suits, label = self.spider_modes[self.spider_mode_index]
        return label

    # ------------------------------------------------------------------ #
    # dropdown helpers
    # ------------------------------------------------------------------ #
    def _variant_option_rects(self):
        """Return list of (GameVariant, label, rect)."""
        options = [
            (GameVariant.KLONDIKE, "Klondike"),
            (GameVariant.SPIDER, "Spider"),
        ]
        base = self.variant_button.rect
        w = base.width
        h = base.height
        rects = []
        for i, (variant, label) in enumerate(options):
            r = pg.Rect(
                base.x,
                base.bottom + 4 + i * (h + 2),
                w,
                h,
            )
            rects.append((variant, label, r))
        return rects

    def _spider_option_rects(self):
        """Return list of (suits, label, rect)."""
        base = self.spider_button.rect
        w = base.width
        h = base.height
        rects = []
        for i, (suits, label) in enumerate(self.spider_modes):
            r = pg.Rect(
                base.x,
                base.bottom + 4 + i * (h + 2),
                w,
                h,
            )
            rects.append((suits, label, r))
        return rects

    def _draw_dropdown(self, options, selected_key=None):
        """Generic dropdown renderer. options: list of (key, label, rect)."""
        for key, label, r in options:
            bg = (40, 40, 50)
            border = (200, 200, 220)
            if selected_key is not None and key == selected_key:
                bg = (70, 80, 110)

            pg.draw.rect(self.screen, bg, r, border_radius=10)
            pg.draw.rect(
                self.screen, border, r, width=2, border_radius=10
            )
            txt = self.button_font.render(label, True, (240, 240, 250))
            self.screen.blit(txt, txt.get_rect(center=r.center))

    # ------------------------------------------------------------------ #
    # drawing helpers
    # ------------------------------------------------------------------ #
    def _draw_background(self, t: float):
        w, h = self.screen.get_size()
        self.screen.fill((25, 28, 35))

        # subtle animated horizontal stripes
        for i in range(0, h, 40):
            shade = 25 + int(10 * (1 + math.sin(i * 0.02 + t * 0.8)))
            pg.draw.rect(
                self.screen,
                (shade, shade, shade + 5),
                (0, i, w, 40),
            )

    def _draw_title(self):
        w, _ = self.screen.get_size()
        label = self.title_font.render(self.title, True, (240, 240, 250))
        self.screen.blit(label, label.get_rect(center=(w // 2, 140)))

    # ------------------------------------------------------------------ #
    # main loop
    # ------------------------------------------------------------------ #
    def run(self) -> MenuResult:
        running = True
        t = 0.0

        while running and self.result is None:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.result = MenuResult.QUIT

                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.result = MenuResult.QUIT

                # --- mouse handling ---
                if self.result is not None:
                    continue

                # first give raw events to buttons (hover + click)
                self.variant_button.handle_event(event)
                # spider button disabled when variant is not Spider
                spider_disabled = self.selected_variant != GameVariant.SPIDER
                self.spider_button.handle_event(event, disabled=spider_disabled)
                self.start_button.handle_event(event)
                self.quit_button.handle_event(event)

                # dropdown click logic
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos

                    # handle variant dropdown
                    if self.variant_dropdown_open:
                        handled = False
                        for variant, label, r in self._variant_option_rects():
                            if r.collidepoint(mx, my):
                                self.selected_variant = variant
                                self.variant_button.text = (
                                    self._variant_button_label()
                                )
                                self.variant_dropdown_open = False
                                # if we switched away from spider, close spider dd
                                if variant != GameVariant.SPIDER:
                                    self.spider_dropdown_open = False
                                handled = True
                                break
                        if handled:
                            continue  # don't process spider dd for this event

                        # click outside closes dropdown
                        if not self.variant_button.rect.collidepoint(mx, my):
                            self.variant_dropdown_open = False

                    # handle spider dropdown
                    if (
                        self.selected_variant == GameVariant.SPIDER
                        and self.spider_dropdown_open
                    ):
                        handled = False
                        for suits, label, r in self._spider_option_rects():
                            if r.collidepoint(mx, my):
                                self.selected_spider_suits = suits
                                # update index + label
                                for i, (s, lab) in enumerate(
                                    self.spider_modes
                                ):
                                    if s == suits:
                                        self.spider_mode_index = i
                                        break
                                self.spider_button.text = (
                                    self._spider_button_label()
                                )
                                self.spider_dropdown_open = False
                                handled = True
                                break
                        if handled:
                            continue

                        # click outside closes dropdown
                        if not self.spider_button.rect.collidepoint(mx, my):
                            self.spider_dropdown_open = False

            # drawing
            t += 1 / FPS
            self._draw_background(t)
            self._draw_title()

            # main buttons row
            spider_disabled = self.selected_variant != GameVariant.SPIDER

            self.variant_button.draw(self.screen)
            self.spider_button.draw(self.screen, disabled=spider_disabled)
            self.start_button.draw(self.screen)
            self.quit_button.draw(self.screen)

            # dropdowns (on top)
            if self.variant_dropdown_open:
                self._draw_dropdown(
                    self._variant_option_rects(),
                    selected_key=self.selected_variant,
                )
            if self.spider_dropdown_open and not spider_disabled:
                self._draw_dropdown(
                    self._spider_option_rects(),
                    selected_key=self.selected_spider_suits,
                )

            # small hint text
            w, h = self.screen.get_size()
            hint = self.small_font.render(
                "Choose a variant (and Spider difficulty), then click Start Game.  ESC to quit.",
                True,
                (175, 180, 195),
            )
            self.screen.blit(
                hint, hint.get_rect(center=(w // 2, h - 60))
            )

            pg.display.flip()
            self.clock.tick(FPS)

        return self.result or MenuResult.QUIT
