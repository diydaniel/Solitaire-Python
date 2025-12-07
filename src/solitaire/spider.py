# --- spider.py 
from __future__ import annotations

from typing import List
import random
import pygame as pg

from .base_game import BaseVariantGame
from .assets import load_card_back
from .model import Card
from .config import (
    GREEN,
    STOCK_POS,
    CARD_SIZE,
    FACEUP_GAP,
    FACEDOWN_GAP,
    RANK_TO_VAL,
    RANKS,
)

SPIDER_COLS = 10

# EDIT THESE NUMBERS to change spacing
SPIDER_EDGE_MARGIN_FACTOR = 1.8   # how far columns stay away from left/right edges (× card width)
SPIDER_COL_GAP_MIN_FACTOR = 0.3  # minimum gap between columns (× card width)
SPIDER_COL_GAP_MAX_FACTOR = 1.0  # maximum gap between columns (× card width)
SPIDER_STOCK_TO_TABLEAU_GAP = 60  # pixels; increase for more space



class SpiderGame(BaseVariantGame):
    """
    Simple 1-suit Spider solitaire (2 decks of spades, 104 cards):

    - 10 tableau columns:
        * columns 0..3: 6 cards each
        * columns 4..9: 5 cards each
        * only top card face-up in each column
    - Remaining cards go to stock.
    - Click stock to deal 1 face-up card to each column (only if no column is empty).
    - You can drag descending runs (e.g. 9-8-7-6).
    - When a full K→A run is at the bottom of a column, it is removed
      and counted as a completed stack.
    """

    def __init__(self, screen: pg.Surface, card_images):
        super().__init__(screen, card_images)
        self.card_back = load_card_back()

        # 10 tableau columns
        self.tableau: List[List[Card]] = [[] for _ in range(10)]
        self.stock: List[tuple[str, str]] = []
        self.completed_runs: int = 0

        # drag state
        self.dragging: bool = False
        self.drag_from_col: int | None = None
        self.drag_stack: List[Card] = []
        self.drag_offset: tuple[int, int] = (0, 0)
        self.drag_pos: tuple[int, int] = (0, 0)
        self.last_click_ms: int = 0

        self.new_game()

    # ---------- deck / setup ----------

    def _build_spider_deck(self) -> list[tuple[str, str]]:
        """
        Build a 1-suit Spider deck:
        2 standard decks, but only spades (13 ranks × 8 copies = 104 cards).
        """
        deck: list[tuple[str, str]] = []
        for _ in range(8):  # 8 copies of each rank
            for r in RANKS:
                deck.append((r, "spades"))
        random.shuffle(deck)
        return deck

    def new_game(self) -> None:
        self.tableau = [[] for _ in range(10)]
        self.stock = []
        self.completed_runs = 0

        deck = self._build_spider_deck()

        # Deal 54 cards to tableau:
        #  - columns 0..3: 6 cards each
        #  - columns 4..9: 5 cards each
        for col_idx in range(10):
            cards_in_col = 6 if col_idx < 4 else 5
            for i in range(cards_in_col):
                r, s = deck.pop()
                face_up = (i == cards_in_col - 1)
                c = Card(r, s, self.card_images[(r, s)], face_up=face_up)
                self.tableau[col_idx].append(c)

        # Remaining cards to stock (top is at the end)
        self.stock = deck[:]
        deck.clear()

        # reset drag
        self.dragging = False
        self.drag_stack = []
        self.drag_from_col = None

    # ---------- layout tuning for Spider ----------
        # ---------- layout helpers ----------
    def _tableau_top_y(self) -> int:
        """Top Y position for the 10 columns."""
        stock_y = STOCK_POS[1]
        return stock_y + CARD_SIZE[1] + SPIDER_STOCK_TO_TABLEAU_GAP

    
    def _column_x(self, col_idx: int) -> int:
        """
        X position for a Spider column.

        - 10 columns
        - centered as a block in the window
        - spacing controlled by the SPIDER_* constants above
        """
        card_w, _ = CARD_SIZE
        screen_w, _ = self.screen.get_size()
        cols = SPIDER_COLS  # 10

        # 1) HORIZONTAL MARGIN TO WINDOW EDGES  --------------------
        #    Increase SPIDER_EDGE_MARGIN_FACTOR for more edge space
        edge_margin = int(card_w * SPIDER_EDGE_MARGIN_FACTOR)

        # how much width is available for the block of 10 columns
        available = screen_w - 2 * edge_margin

            # 2) GAP BETWEEN COLUMNS  ----------------------------------
        #    Gap is clamped between MIN and MAX factors
        if cols > 1:
            ideal_gap = (available - cols * card_w) / (cols - 1)
            min_gap = int(card_w * SPIDER_COL_GAP_MIN_FACTOR)
            max_gap = int(card_w * SPIDER_COL_GAP_MAX_FACTOR)
            gap_x = max(min_gap, min(max_gap, ideal_gap))
        else:
            gap_x = 0

        block_w = cols * card_w + (cols - 1) * gap_x
        x0 = (screen_w - block_w) // 2  # center the whole block

        return int(x0 + col_idx * (card_w + gap_x))



    def _column_hit_test(self, mx: int, my: int) -> tuple[int, int]:
        """
        Return (column_index, card_index) for the topmost card hit.
        card_index = -1 if we hit a facedown-only region.
        """
        for col_idx, col in enumerate(self.tableau):
            x = self._column_x(col_idx)
            y = self._tableau_top_y()
            for i, c in enumerate(col):
                h = FACEUP_GAP if c.face_up else FACEDOWN_GAP
                rect = pg.Rect(
                    x,
                    y,
                    CARD_SIZE[0],
                    CARD_SIZE[1] if i == len(col) - 1 else h,
                )
                if rect.collidepoint(mx, my):
                    return (col_idx, i if c.face_up else -1)
                y += h
        return (-1, -1)

    # ---------- rules helpers ----------

    def _rank_value(self, rank: str) -> int:
        return RANK_TO_VAL[rank]

    def _can_pick_stack(self, col_idx: int, card_idx: int) -> bool:
        """
        True if from card_idx downward we have a descending-by-1 run.
        """
        col = self.tableau[col_idx]
        if card_idx < 0 or card_idx >= len(col):
            return False
        if not col[card_idx].face_up:
            return False

        for i in range(card_idx, len(col) - 1):
            a = col[i]
            b = col[i + 1]
            if self._rank_value(a.rank) != self._rank_value(b.rank) + 1:
                return False
        return True

    def _can_drop_stack(self, moving_top: Card, dest_col_idx: int) -> bool:
        """
        Drop rules:
          - On empty column: always allowed
          - On card that is exactly one rank higher (8 on 9, 4 on 5, etc.)
        """
        col = self.tableau[dest_col_idx]
        if not col:
            return True
        top = col[-1]
        return self._rank_value(top.rank) == self._rank_value(moving_top.rank) + 1

    def _check_complete_runs(self) -> None:
        """
        After a move or a stock deal, check for K→A runs at the bottom
        of each column and remove them.
        """
        for col_idx, col in enumerate(self.tableau):
            if len(col) < 13:
                continue

            tail = col[-13:]
            ok = True
            for i in range(12):
                if self._rank_value(tail[i].rank) != self._rank_value(
                    tail[i + 1].rank
                ) + 1:
                    ok = False
                    break

                if ok:
                    # Remove the run and count it
                    del self.tableau[col_idx][-13:]
                    self.completed_runs += 1

                    # 🔹 Flip the new top card if it exists and is face down
                    col_after = self.tableau[col_idx]
                    if col_after and not col_after[-1].face_up:
                        col_after[-1].face_up = True


    def _deal_from_stock(self) -> None:
        """
        Deal 1 card to each tableau column from stock:
          - Only if no column is empty.
          - Only if at least 10 cards remain in stock.
        """
        if any(len(col) == 0 for col in self.tableau):
            return
        if len(self.stock) < 10:
            return

        for col_idx in range(10):
            r, s = self.stock.pop()
            c = Card(r, s, self.card_images[(r, s)], face_up=True)
            self.tableau[col_idx].append(c)

        self._check_complete_runs()

    def _is_win(self) -> bool:
        """
        Win when all 8 K→A runs are complete and both stock and tableau are empty.
        (For now we mainly track completed_runs; you can tighten this later.)
        """
        return self.completed_runs >= 8 and not self.stock and all(
            len(col) == 0 for col in self.tableau
        )

    # ---------- main variant interface ----------

    def handle_event(self, event: pg.event.Event) -> None:
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            now = pg.time.get_ticks()
            # (double-click unused for now, but kept if we want it later)
            double = (now - self.last_click_ms) < 300
            self.last_click_ms = now

            # Stock click: deal a new row
            if pg.Rect(STOCK_POS, CARD_SIZE).collidepoint(mx, my):
                self._deal_from_stock()
                return

            # Start drag from tableau
            col_idx, card_idx = self._column_hit_test(mx, my)
            if col_idx != -1 and card_idx != -1:
                if self._can_pick_stack(col_idx, card_idx):
                    col = self.tableau[col_idx]
                    self.dragging = True
                    self.drag_from_col = col_idx
                    self.drag_stack = col[card_idx:]

                    # compute top card position for offset
                    top_x = self._column_x(col_idx)
                    top_y = self._tableau_top_y()
                    for i in range(card_idx):
                        c = col[i]
                        top_y += FACEUP_GAP if c.face_up else FACEDOWN_GAP
                    self.drag_offset = (top_x - mx, top_y - my)
                    self.drag_pos = (mx, my)
                    return

        elif event.type == pg.MOUSEMOTION and self.dragging:
            self.drag_pos = event.pos

        elif event.type == pg.MOUSEBUTTONUP and event.button == 1 and self.dragging:
            mx, my = event.pos
            placed = False

            for col_idx in range(10):
                x = self._column_x(col_idx)
                area = pg.Rect(
                    x,
                    self._tableau_top_y(),
                    CARD_SIZE[0],
                    self.screen.get_height() ,
                )
                if area.collidepoint(mx, my):
                    moving_top = self.drag_stack[0]
                    if self._can_drop_stack(moving_top, col_idx):
                        src_col = self.tableau[self.drag_from_col]  # type: ignore
                        count = len(self.drag_stack)
                        del src_col[-count:]
                        self.tableau[col_idx].extend(self.drag_stack)

                        if src_col and not src_col[-1].face_up:
                            src_col[-1].face_up = True

                        placed = True
                        self._check_complete_runs()
                    break

            # end drag
            self.dragging = False
            self.drag_stack = []
            self.drag_from_col = None

    def update(self, dt: float) -> None:
        # No time-based spider animation yet
        pass

    def _draw_tableau(self) -> None:
        for col_idx, col in enumerate(self.tableau):
            x = self._column_x(col_idx)
            y = self._tableau_top_y()
            for c in col:
                c.draw(self.screen, x, y, self.card_back)
                y += FACEUP_GAP if c.face_up else FACEDOWN_GAP

    def draw(self) -> None:
        # Same green background for consistency
        self.screen.fill(GREEN)

        # Stock pile
        if self.stock:
            self.screen.blit(self.card_back, STOCK_POS)
        else:
            pg.draw.rect(
                self.screen,
                (230, 230, 230),
                (*STOCK_POS, *CARD_SIZE),
                2,
                border_radius=8,
            )

        # HUD: completed runs
        font = pg.font.SysFont("Arial", 24, bold=True)
        text = font.render(
            f"Completed runs: {self.completed_runs} / 8",
            True,
            (255, 255, 255),
        )
        self.screen.blit(
            text,
            (STOCK_POS[0] + CARD_SIZE[0] + 40, STOCK_POS[1]),
        )

        # Tableau
        self._draw_tableau()

        # Drag overlay
        if self.dragging and self.drag_stack:
            mx, my = self.drag_pos
            x = mx + self.drag_offset[0]
            y = my + self.drag_offset[1]
            for c in self.drag_stack:
                c.draw(self.screen, x, y, self.card_back)
                y += FACEUP_GAP
