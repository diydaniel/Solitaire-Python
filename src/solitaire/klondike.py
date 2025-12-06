# --- klondike.py -------------------------------------------------
from __future__ import annotations

from typing import List, Tuple
from collections import Counter
import random
import pygame as pg

from .base_game import BaseVariantGame
from .assets import load_card_back
from .animations import WinAnimation
from .model import Card, can_stack_on_foundation, can_stack_on_tableau
from .config import (
    GREEN,
    STOCK_POS,
    WASTE_POS,
    CARD_SIZE,
    FACEUP_GAP,
    FOUND_X0,
    FOUND_STEP_X,
    FOUND_Y0,
    TABLEAU_X0,
    TABLEAU_STEP_X,
    TABLEAU_Y0,
    SCREEN_HEIGHT,
    FACEDOWN_GAP,
    FOUND_SUITS,
    SUIT_COLOR,
)

# ---------------------------------------------------------------------------------------------------
# Klondike Solitaire 
# ---------------------------------------------------------------------------------------------------

class KlondikeGame(BaseVariantGame):
    def __init__(self, screen: pg.Surface, card_images):
        super().__init__(screen, card_images)
        
        self.screen = screen

        # assets
        self.card_images = card_images      # reuse passed-in dict
        self.card_back = load_card_back()
        self.win_anim: WinAnimation | None = None

        # piles
        self.tableau: List[List[Card]] = [[] for _ in range(7)]
        self.foundations: List[List[Card]] = [[], [], [], []]
        self.stock: List[Tuple[str, str]] = []
        self.waste: List[Card] = []

        # ---- deck + deal ----
        self.deck: List[Tuple[str, str]] = list(self.card_images.keys())
        random.shuffle(self.deck)

        self.deal_cards()
        self.stock = self.deck[:]
        self.deck.clear()

        # ---- drag state ----
        self.dragging: bool = False
        # ("waste", None) or ("tableau", column_index)
        self.drag_from: Tuple[str, int | None] = ("", None)
        self.drag_cards: List[Card] = []
        self.drag_offset: Tuple[int, int] = (0, 0)
        self.drag_pos: Tuple[int, int] = (0, 0)
        self.last_click_ms: int = 0

        # ---- start-of-game deal animation ----
        self.deal_anim_active: bool = False
        self.deal_anim_time: float = 0.0
        self.deal_anim_steps: list[dict] = []
        self._deal_anim_total_time: float = 0.0

        # build animation steps for this initial deal
        self._prepare_deal_animation()

        counts = Counter(self.deck)
        dupes = [k for k, v in counts.items() if v > 1]
        if dupes:
            print("WARNING: duplicate logical cards in deck:", dupes)

    
    def foundation_top(self, i: int) -> Tuple[str, str] | None:
        """
        Return the (rank, suit) of the top card in foundation pile i,
        or None if that foundation pile is empty.
        """
        pile = self.foundations[i]
        if not pile:
            return None
        top = pile[-1]
        return (top.rank, top.suit)

    
    def deal_cards(self):
        for col in range(7):
            for _ in range(col + 1):
                if not self.deck:
                    raise RuntimeError("Deck ran out of cards while dealing tableau.")
                r, s = self.deck.pop()
                self.tableau[col].append(
                    Card(r, s, self.card_images[(r, s)], face_up=False)
                )
            self.tableau[col][-1].face_up = True

    
    def new_game(self):
        self.win_anim = None

        # Rebuild deck from loaded images (same source as __init__)
        self.deck = list(self.card_images.keys())
        random.shuffle(self.deck)

        for col in self.tableau:
            col.clear()
        for f in self.foundations:
            f.clear()
        self.waste.clear()
        self.stock.clear()

        self.deal_cards()
        self.stock.extend(self.deck)
        self.deck.clear()

        # 🔹 build a fresh deal animation for the new game
        self._prepare_deal_animation()


    # --- testing 
    def column_hit_test(self, mx, my) -> Tuple[int, int]:
        for col_idx, col in enumerate(self.tableau):
            x = TABLEAU_X0 + col_idx * TABLEAU_STEP_X
            y = TABLEAU_Y0
            for i, c in enumerate(col):
                h = FACEUP_GAP if c.face_up else FACEDOWN_GAP
                rect = pg.Rect(x, y, CARD_SIZE[0], CARD_SIZE[1] if i == len(col)-1 else h)
                if rect.collidepoint(mx, my):
                    return (col_idx, i if c.face_up else -1)
                y += h
        return (-1, -1)
    
# ---------------------------------------------------------------------------------------------------
# --- Animation
    def _is_win(self) -> bool:
        """Win if all 4 foundations are complete (13 each)."""
        return all(len(pile) == 13 for pile in self.foundations)

    
    def _snapshot_visible_cards(self) -> list[tuple[pg.Surface, pg.Rect]]:
        """
        Build (image, rect) tuples using the same coordinates as draw_*().
        We DO NOT mutate live rects—use fresh pg.Rects at draw positions.
        """
        cards: list[tuple[pg.Surface, pg.Rect]] = []

        # Foundations (all cards in the stack; they overlap at the same spot)
        for i, pile in enumerate(self.foundations):
            x = FOUND_X0 + i * FOUND_STEP_X
            y = FOUND_Y0
            for c in pile:
                img = c.image if c.face_up else self.card_back
                cards.append((img, pg.Rect(x, y, *CARD_SIZE)))

        # Waste (you only draw the top card; include just that)
        if self.waste:
            img = self.waste[-1].image if self.waste[-1].face_up else self.card_back
            cards.append((img, pg.Rect(*WASTE_POS, *CARD_SIZE)))

        # Tableau (each card at its stacked y)
        for col_i, column in enumerate(self.tableau):
            x = TABLEAU_X0 + col_i * TABLEAU_STEP_X
            y = TABLEAU_Y0
            for c in column:
                img = c.image if c.face_up else self.card_back
                cards.append((img, pg.Rect(x, y, *CARD_SIZE)))
                y += FACEUP_GAP if c.face_up else FACEDOWN_GAP

        return cards
    
    
    def _start_win_animation(self):
        cards = self._snapshot_visible_cards()
        self.win_anim = WinAnimation(self.screen, cards)

    
    def _check_win_and_start(self):
        if self.win_anim is None and self._is_win():
            self._start_win_animation()

    
    def animation_update(self, dt: float):
        # placeholder for future animations / timers
        pass

    def _prepare_deal_animation(self) -> None:
        """
        Build an animated deal sequence from the stock position to
        each tableau card in the same order they were dealt logically.
        """
        self.deal_anim_steps.clear()
        self.deal_anim_time = 0.0
        self.deal_anim_active = True

        origin_x, origin_y = STOCK_POS  # visual "dealer" origin

        delay_per_card = 0.08   # seconds between card starts
        travel_time = 0.25      # seconds a card takes to fly

        step_index = 0

        # Match the logical deal pattern: col 0 gets 1 card, col 1 gets 2, ...
        for col_idx in range(7):
            column = self.tableau[col_idx]
            for row_idx, card in enumerate(column):
                # target X for this column
                end_x = TABLEAU_X0 + col_idx * TABLEAU_STEP_X

                # target Y: stack down from TABLEAU_Y0
                y = TABLEAU_Y0
                for i in range(row_idx):
                    above = column[i]
                    y += FACEUP_GAP if above.face_up else FACEDOWN_GAP
                end_y = y

                delay = step_index * delay_per_card

                self.deal_anim_steps.append({
                    "card": card,
                    "start": (origin_x, origin_y),
                    "end": (end_x, end_y),
                    "delay": delay,
                    "duration": travel_time,
                })
                step_index += 1

        if self.deal_anim_steps:
            last = self.deal_anim_steps[-1]
            self._deal_anim_total_time = last["delay"] + last["duration"]
        else:
            self._deal_anim_total_time = 0.0
            self.deal_anim_active = False

    
# ---------------------------------------------------------------------------------------------------
    
    # --- state helpers --- some would use this as update()
    def end_drag(self):
        """Reset all drag-related state."""
        self.dragging = False
        self.drag_from = ("", None)
        self.drag_cards = []


    def handle_event(self, event: pg.event.Event) -> None:
        # Block interactions while the win animation is running (except 'N' to deal)
        if self.win_anim and not self.win_anim.finished:
            double = False  # default for non-mousedown events

            if event.type == pg.KEYDOWN and event.key == pg.K_n:
                self.new_game()
                self.win_anim = None
            return
        # 🔹 Block normal interactions while the initial deal animation is running
        if self.deal_anim_active:
            # Optional: allow 'N' to skip and start a new deal immediately
            if event.type == pg.KEYDOWN and event.key == pg.K_n:
                self.new_game()
                self.deal_anim_active = False
            return

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            now = pg.time.get_ticks()
            double = (now - self.last_click_ms) < 300
            self.last_click_ms = now

            # stock click
            if pg.Rect(STOCK_POS, CARD_SIZE).collidepoint(mx, my):
                if self.stock:
                    r, s = self.stock.pop()
                    self.waste.append(Card(r, s, self.card_images[(r,s)], face_up=True))
                else:
                    while self.waste:
                        c = self.waste.pop()
                        self.stock.append((c.rank, c.suit))
                        #self._check_win_and_start()   # <-- add this
                return
            
            # --- waste area: handle double-click first, else start drag ---
            waste_rect = pg.Rect(WASTE_POS, CARD_SIZE)
            if self.waste and waste_rect.collidepoint(mx, my):
                if double:
                    moving = self.waste[-1]
                    mv = (moving.rank, moving.suit)
                    for fi in range(4):
                        if can_stack_on_foundation(self.foundation_top(fi), mv, fi):
                            self.waste.pop()
                            self.foundations[fi].append(moving)
                            self._check_win_and_start()
                            break
                    return  # handled double-click

                # single-click → start drag of waste top
                self.dragging = True
                self.drag_from = ("waste", None)
                self.drag_cards = [self.waste[-1]]
                self.drag_offset = (waste_rect.x - mx, waste_rect.y - my)
                self.drag_pos = (mx, my)
                return
            
            
            # --- tableau: double-click top under mouse to foundation ---
            if double:
                moved = False
                col_idx, idx = self.column_hit_test(mx, my)
                if col_idx != -1 and idx == len(self.tableau[col_idx]) - 1 and idx != -1:
                    c = self.tableau[col_idx][-1]
                    if c.face_up:
                        mv = (c.rank, c.suit)
                        for fi in range(4):
                            if can_stack_on_foundation(self.foundation_top(fi), mv, fi):
                                self.tableau[col_idx].pop()
                                self.foundations[fi].append(c)
                                if self.tableau[col_idx] and not self.tableau[col_idx][-1].face_up:
                                    self.tableau[col_idx][-1].face_up = True
                                self._check_win_and_start()   # <-- add this
                                moved = True
                                break
                if moved:
                    return

            # --- tableau: start drag from a face-up run ---
            col_idx, idx = self.column_hit_test(mx, my)
            if col_idx != -1 and idx != -1 and self.tableau[col_idx][idx].face_up:
                self.dragging = True
                self.drag_from = ("tableau", col_idx)
                self.drag_cards = self.tableau[col_idx][idx:]
                top_rect = self.drag_cards[0].rect
                self.drag_offset = (top_rect.x - mx, top_rect.y - my)
                self.drag_pos = (mx, my)
                return

        elif event.type == pg.MOUSEMOTION and self.dragging:
            self.drag_pos = event.pos

        elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
            if not self.dragging or not self.drag_cards:
                self.end_drag()
                return

            mx, my = event.pos
            placed = False

            # foundations first (single card)
            if len(self.drag_cards) == 1:
                moving = self.drag_cards[0]
                mv = (moving.rank, moving.suit)
                for fi in range(4):
                    x = FOUND_X0 + fi * FOUND_STEP_X
                    y = FOUND_Y0
                    area = pg.Rect(x, y, *CARD_SIZE)
                    if area.collidepoint(mx, my) and can_stack_on_foundation(self.foundation_top(fi), mv, fi):
                        if self.drag_from[0] == "tableau":
                            src = self.tableau[self.drag_from[1]]  # type: ignore
                            src.pop()
                            if src and not src[-1].face_up:
                                src[-1].face_up = True
                        else:
                            self.waste.pop()
                        self.foundations[fi].append(moving)
                        placed = True
                        self._check_win_and_start()   # <-- add this
                        break

            # otherwise tableau
            if not placed:
                drop_col = -1
                for ci in range(7):
                    x = TABLEAU_X0 + ci * TABLEAU_STEP_X
                    area = pg.Rect(x, TABLEAU_Y0, CARD_SIZE[0], SCREEN_HEIGHT - TABLEAU_Y0)
                    if area.collidepoint(mx, my):
                        drop_col = ci
                        break

                if drop_col != -1:
                    moving_top = (self.drag_cards[0].rank, self.drag_cards[0].suit)
                    dst_top = None
                    if self.tableau[drop_col] and self.tableau[drop_col][-1].face_up:
                        t = self.tableau[drop_col][-1]
                        dst_top = (t.rank, t.suit)

                    if can_stack_on_tableau(dst_top, moving_top):
                        if self.drag_from[0] == "tableau":
                            src = self.tableau[self.drag_from[1]]  # type: ignore
                            count = len(self.drag_cards)
                            del src[-count:]
                            if src and not src[-1].face_up:
                                src[-1].face_up = True
                        else:
                            self.waste.pop()
                        self.tableau[drop_col].extend(self.drag_cards)
                        placed = True

            # end drag always
            self.end_drag()

   
    def draw_tableau(self):
        for i, column in enumerate(self.tableau):
            x = TABLEAU_X0 + i * TABLEAU_STEP_X
            y = TABLEAU_Y0
            for card in column:
                card.draw(self.screen, x, y, self.card_back)
                y += FACEUP_GAP if card.face_up else FACEDOWN_GAP

    
    def draw_foundations(self):
        font = pg.font.SysFont("Arial", 24, bold=True)
        for i in range(4):
            x = FOUND_X0 + i * FOUND_STEP_X
            y = FOUND_Y0
            if self.foundations[i]:
                self.foundations[i][-1].draw(self.screen, x, y, self.card_back)
            else:
                pg.draw.rect(self.screen, (230,230,230), (x, y, *CARD_SIZE), 2, border_radius=8)
                suit = FOUND_SUITS[i]
                symbol = {'clubs':'♣','diamonds':'♦','hearts':'♥','spades':'♠'}[suit]
                label = font.render(symbol, True, SUIT_COLOR[suit])
                self.screen.blit(label, (x + CARD_SIZE[0]//2 - label.get_width()//2,
                                         y + CARD_SIZE[1]//2 - label.get_height()//2))

    def update(self, dt: float) -> None:
        # Advance deal animation timer
        if self.deal_anim_active:
            self.deal_anim_time += dt
            if self.deal_anim_time >= self._deal_anim_total_time:
                self.deal_anim_active = False
        # You can add other per-frame logic here later


    def draw(self) -> None:
        self.screen.fill(GREEN)

        if self.deal_anim_active:
            # While dealing: show empty stock outline, foundations, and flying cards

            # empty stock outline (no pile yet)
            pg.draw.rect(
                self.screen,
                (230, 230, 230),
                (*STOCK_POS, *CARD_SIZE),
                2,
                border_radius=8,
            )

            # foundation placeholders
            self.draw_foundations()

            # animate tableau cards
            t = self.deal_anim_time
            for step in self.deal_anim_steps:
                delay = step["delay"]
                duration = step["duration"]

                if t < delay:
                    continue  # card hasn't started yet

                alpha = min(1.0, (t - delay) / duration)
                sx, sy = step["start"]
                ex, ey = step["end"]
                x = sx + (ex - sx) * alpha
                y = sy + (ey - sy) * alpha

                card = step["card"]
                card.draw(self.screen, int(x), int(y), self.card_back)

            # no waste / drag / normal tableau while dealing

        else:
            # --- stock
            if self.stock:
                self.screen.blit(self.card_back, STOCK_POS)
            else:
                # empty stock outline
                pg.draw.rect(
                    self.screen,
                    (230, 230, 230),
                    (*STOCK_POS, *CARD_SIZE),
                    2,
                    border_radius=8,
                )

            # waste
            if self.waste and not (self.dragging and self.drag_from[0] == "waste"):
                self.waste[-1].draw(self.screen, *WASTE_POS, self.card_back)

            # foundations + tableau
            self.draw_foundations()
            self.draw_tableau()

            # drag overlay
            if self.dragging and self.drag_cards:
                mx, my = self.drag_pos
                x = mx + self.drag_offset[0]
                y = my + self.drag_offset[1]
                for c in self.drag_cards:
                    c.draw(self.screen, x, y, self.card_back)
                    y += FACEUP_GAP

        # Safety net: if the board is already in a win state, start the win animation
        if self.win_anim is None and self._is_win():
            self._start_win_animation()

        # Win celebration overlay (renders on top of the board)
        if self.win_anim and not self.win_anim.finished:
            self.win_anim.draw()