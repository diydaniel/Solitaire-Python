# --- game.py 
import random
import pygame
from typing import List, Tuple, Dict
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, GREEN,
    CARD_SIZE, SUITS, RANKS, RANK_TO_VAL, RED_SUITS,
    TABLEAU_X0, TABLEAU_Y0, TABLEAU_GAP_X,
    FACEUP_GAP, FACEDOWN_GAP,
    FOUND_X0, FOUND_Y0, FOUND_GAP_X,
    STOCK_POS, WASTE_POS,
    FOUND_SUITS, SUIT_COLOR,
)
from animations import WinAnimation
from assets import load_card_images, load_card_back
from model import Card

# ---------------------------------------------------------------------------------------------------
# --- Function: isRed() --- Helpers/ Rules ---
def is_red(suit: str) -> bool:  # Purpose: Tells you if a suit is a red suit.
    return suit in RED_SUITS    # How: Returns True if suit is in RED_SUITS (typically {'♥', '♦'}), else False.


# --- Function: canStackOnTableau()
def can_stack_on_tableau(dst_top: Tuple[str,str] | None, moving_top: Tuple[str,str]) -> bool:   
    
    # Purpose: Checks if a card (or a moving pile’s top card) can be placed on a tableau pile.

    """Tableau rule: alt color, descending by 1. Empty accepts K."""

    if dst_top is None:

        # dst_top: Tuple[str, str] | None — the current top card on the destination tableau pile, or None if the pile is empty.
            # A card is a tuple (rank, suit) like ('7', '♣').
                # moving_top: Tuple[str, str] — the top card of what you want to move, e.g. ('6', '♦').

        return moving_top[0] == 'K'

            # If the destination is empty, only a King ('K') can be placed.
                # Otherwise, you must place alternating colors and descending by 1 rank.
    
    dr, ds = dst_top            # Example: dst_top=('7','♣'), moving_top=('6','♦') → black vs red, 6 is one less than 7 → True.
    mr, ms = moving_top             # Example: dst_top=None, moving_top=('Q','♥') → empty but not a King → False.

        # How:
                # If dst_top is None → return moving_top[0] == 'K'.
                    # Else unpack both cards, then check:
                        # is_red(ds) != is_red(ms) → colors alternate (red on black or black on red).
                            # RANK_TO_VAL[mr] == RANK_TO_VAL[dr] - 1 → ranks descend by one (e.g., 6 on 7).

    return (is_red(ds) != is_red(ms)) and (RANK_TO_VAL[mr] == RANK_TO_VAL[dr] - 1)


# --- Function: canStackOnFoundation()
def can_stack_on_foundation(dst_top: Tuple[str,str] | None, moving: Tuple[str,str], slot_index: int) -> bool:

    # Purpose: Checks if a card can go onto a foundation pile (the four suit piles you build up from Ace to King).

    mr, ms = moving
    required_suit = FOUND_SUITS[slot_index]
    if ms != required_suit:                     # must match this slot’s suit
        return False
    if dst_top is None:                         # dst_top: Tuple[str, str] | None --- current top card on that foundation pile, or None if empty.
        return mr == 'A'                        # moving: Tuple[str, str] --- the card you want to place.
    tr, ts = dst_top
    return (ms == ts) and (RANK_TO_VAL[mr] == RANK_TO_VAL[tr] + 1)

            # slot_index: int — which foundation pile (0..3), used to pick the required suit from FOUND_SUITS.

# ---------------------------------------------------------------------------------------------------
# --- Object BluePrint: Game 
class Game:
    def __init__(self, screen: pygame.Surface):

# ---------------------------------------------------------------------------------------------------
# --- Class Attributes ---

        self.screen = screen
        # assets
        self.card_images = load_card_images()
        self.card_back = load_card_back()
        self.win_anim: WinAnimation | None = None

        # piles
        self.tableau: List[List[Card]] = [[] for _ in range(7)]
        self.foundations: List[List[Card]] = [[], [], [], []]
        self.stock: List[Tuple[str,str]] = []
        self.waste: List[Card] = []

        # deck + deal
        self.deck: List[Tuple[str,str]] = [(r, s) for s in SUITS for r in RANKS]
        random.shuffle(self.deck)
        self.deal_cards()
        self.stock = self.deck[:]
        self.deck.clear()

        # drag state
        self.dragging = False
        self.drag_from: Tuple[str, int | None] = ("", None)  # ("waste", None) or ("tableau", col)
        self.drag_cards: List[Card] = []
        self.drag_offset = (0, 0)
        self.drag_pos = (0, 0)
        self.last_click_ms = 0

# ---------------------------------------------------------------------------------------------------
    # --- Method: endDrag() --- state helpers ---
    def end_drag(self):
        self.dragging = False
        self.drag_from = ("", None)
        self.drag_cards = []

    # --- Method: foundationTop()
    def foundation_top(self, i: int) -> Tuple[str,str] | None:
        pile = self.foundations[i]
        if not pile:
            return None
        top = pile[-1]
        return (top.rank, top.suit)
    
    # --- Method: dealCards()
    def deal_cards(self):
        for col in range(7):
            for _ in range(col + 1):
                r, s = self.deck.pop()
                self.tableau[col].append(Card(r, s, self.card_images[(r,s)], face_up=False))
            self.tableau[col][-1].face_up = True

    # --- Method: newGame()
    def new_game(self):
        self.win_anim = None
        self.deck = [(r, s) for s in SUITS for r in RANKS]
        random.shuffle(self.deck)
        for col in self.tableau: col.clear()
        for f in self.foundations: f.clear()
        self.waste.clear()
        self.stock.clear()
        self.deal_cards()
        self.stock.extend(self.deck)
        self.deck.clear()

    # --- Method: columnHitTest() ----- hit testing -----
    def column_hit_test(self, mx, my) -> Tuple[int, int]:
        for col_idx, col in enumerate(self.tableau):
            x = TABLEAU_X0 + col_idx * TABLEAU_GAP_X
            y = TABLEAU_Y0
            for i, c in enumerate(col):
                h = FACEUP_GAP if c.face_up else FACEDOWN_GAP
                rect = pygame.Rect(x, y, CARD_SIZE[0], CARD_SIZE[1] if i == len(col)-1 else h)
                if rect.collidepoint(mx, my):
                    return (col_idx, i if c.face_up else -1)
                y += h
        return (-1, -1)
    
    # --- Method: Win animation
    def _is_win(self) -> bool:
        """Win if all 4 foundations are complete (13 each)."""
        return all(len(pile) == 13 for pile in self.foundations)

    # --- Method: Win animation
    def _snapshot_visible_cards(self) -> list[tuple[pygame.Surface, pygame.Rect]]:
        """
        Build (image, rect) tuples using the same coordinates as draw_*().
        We DO NOT mutate live rects—use fresh pygame.Rects at draw positions.
        """
        cards: list[tuple[pygame.Surface, pygame.Rect]] = []

        # Foundations (all cards in the stack; they overlap at the same spot)
        for i, pile in enumerate(self.foundations):
            x = FOUND_X0 + i * FOUND_GAP_X
            y = FOUND_Y0
            for c in pile:
                img = c.image if c.face_up else self.card_back
                cards.append((img, pygame.Rect(x, y, *CARD_SIZE)))

        # Waste (you only draw the top card; include just that)
        if self.waste:
            img = self.waste[-1].image if self.waste[-1].face_up else self.card_back
            cards.append((img, pygame.Rect(*WASTE_POS, *CARD_SIZE)))

        # Tableau (each card at its stacked y)
        for col_i, column in enumerate(self.tableau):
            x = TABLEAU_X0 + col_i * TABLEAU_GAP_X
            y = TABLEAU_Y0
            for c in column:
                img = c.image if c.face_up else self.card_back
                cards.append((img, pygame.Rect(x, y, *CARD_SIZE)))
                y += FACEUP_GAP if c.face_up else FACEDOWN_GAP

        return cards
    
# ---------------------------------------------------------------------------------------------------

    # --- Method: Win animation
    def _start_win_animation(self):
        cards = self._snapshot_visible_cards()
        self.win_anim = WinAnimation(self.screen, cards)

    # --- Method: Win animation
    def _check_win_and_start(self):
        if self.win_anim is None and self._is_win():
            self._start_win_animation()

    # --- Method: Win animation
    def update(self, dt: float):
    # placeholder for future animations / timers
        pass
    
# ---------------------------------------------------------------------------------------------------

    # --- Method: handleEvent() ----- events -----
    def handle_event(self, event: pygame.event.Event):
        # Block interactions while the win animation is running (except 'N' to deal)
        if self.win_anim and not self.win_anim.finished:
            double = False  # default for non-mousedown events

            if event.type == pygame.KEYDOWN and event.key == pygame.K_n:
                self.new_game()
                self.win_anim = None
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            now = pygame.time.get_ticks()
            double = (now - self.last_click_ms) < 300
            self.last_click_ms = now

            # stock click
            if pygame.Rect(STOCK_POS, CARD_SIZE).collidepoint(mx, my):
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
            waste_rect = pygame.Rect(WASTE_POS, CARD_SIZE)
            if self.waste and waste_rect.collidepoint(mx, my):
                if double:
                    moving = self.waste[-1]
                    mv = (moving.rank, moving.suit)
                    for fi in range(4):
                        if can_stack_on_foundation(self.foundation_top(fi), mv, fi):
                            self.waste.pop()
                            self.foundations[fi].append(moving)
                            self._check_win_and_start()   # <-- add this
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

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.drag_pos = event.pos

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
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
                    x = FOUND_X0 + fi * FOUND_GAP_X
                    y = FOUND_Y0
                    area = pygame.Rect(x, y, *CARD_SIZE)
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
                    x = TABLEAU_X0 + ci * TABLEAU_GAP_X
                    area = pygame.Rect(x, TABLEAU_Y0, CARD_SIZE[0], SCREEN_HEIGHT - TABLEAU_Y0)
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

    # ----- Method:
    def draw_tableau(self):
        for i, column in enumerate(self.tableau):
            x = TABLEAU_X0 + i * TABLEAU_GAP_X
            y = TABLEAU_Y0
            for card in column:
                card.draw(self.screen, x, y, self.card_back)
                y += FACEUP_GAP if card.face_up else FACEDOWN_GAP

    # ----- Method:
    def draw_foundations(self):
        font = pygame.font.SysFont("Arial", 24, bold=True)
        for i in range(4):
            x = FOUND_X0 + i * FOUND_GAP_X
            y = FOUND_Y0
            if self.foundations[i]:
                self.foundations[i][-1].draw(self.screen, x, y, self.card_back)
            else:
                pygame.draw.rect(self.screen, (230,230,230), (x, y, *CARD_SIZE), 2, border_radius=8)
                suit = FOUND_SUITS[i]
                symbol = {'clubs':'♣','diamonds':'♦','hearts':'♥','spades':'♠'}[suit]
                label = font.render(symbol, True, SUIT_COLOR[suit])
                self.screen.blit(label, (x + CARD_SIZE[0]//2 - label.get_width()//2,
                                         y + CARD_SIZE[1]//2 - label.get_height()//2))

    # ----- Method:
    def draw(self):
        self.screen.fill(GREEN)
        # stock
        if self.stock:
            self.screen.blit(self.card_back, STOCK_POS)
        else:
            pygame.draw.rect(self.screen, (230,230,230), (*STOCK_POS, *CARD_SIZE), 2, border_radius=8)
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
        
        # Safety net: if the board is already in a win state, start the animation
        if self.win_anim is None and self._is_win():
            self._start_win_animation()

        # Win celebration overlay (renders on top of the board)
        if self.win_anim and not self.win_anim.finished:
            self.win_anim.draw()