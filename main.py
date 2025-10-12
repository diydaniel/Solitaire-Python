import pygame, random
from pathlib import Path
from typing import Dict, Tuple

# --- Initialize Pygame ---
pygame.init()

# --- Setup the game window ---
SCREEN_WIDTH, SCREEN_HEIGHT = 1024, 768
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Solitaire")
# --- Setup colors ---
GREEN = (0, 128, 0)

# --- Create a deck of cards ---
CARD_SIZE: Tuple[int, int] = (72, 96)  # change as needed
SUITS = ['hearts', 'diamonds', 'clubs', 'spades']
RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']


def asset_path(*parts) -> Path:
    # adjust "assets/cards" to your actual directory
    return Path(__file__).resolve().parent / "assets" / "cards" / Path(*parts)

def filename_for(rank: str, suit: str) -> str:
    # e.g. "2_of_clubs.png", "A_of_hearts.png", "10_of_spades.png"
    return f"{rank}_of_{suit}.png"


# --- Load card images ---
def load_card_images(size: Tuple[int,int] = CARD_SIZE) -> Dict[Tuple[str, str], pygame.Surface]:
    images: Dict[Tuple[str,str], pygame.Surface] = {}

    for suit in SUITS:
        for rank in RANKS:
            img = pygame.image.load(asset_path(filename_for(rank, suit))).convert_alpha()
            if img.get_size() != size:
                img = pygame.transform.smoothscale(img, size)
            images[(rank, suit)] = img
    return images
        
card_images = load_card_images()
card_back = pygame.image.load(asset_path("card_back_black.png")).convert_alpha()
if card_back.get_size() != CARD_SIZE:
    card_back = pygame.transform.smoothscale(card_back, CARD_SIZE)

# --- Define card class ---
class Card:
    def __init__(self, rank, suit, image, face_up=False):
        self.rank = rank
        self.suit = suit
        self.image = image
        self.face_up = face_up
        self.rect = self.image.get_rect()

    def draw(self, surf, x, y):
        self.rect.topleft = (x, y)
        surf.blit(self.image if self.face_up else card_back, self.rect.topleft)

# --- Build deck as tuples, then shuffle ---
deck = [(rank, suit) for suit in SUITS for rank in RANKS]
random.shuffle(deck)

# --- Piles ---
tableau = [[] for _ in range(7)]                   # 7 columns
foundations = {s: [] for s in SUITS}               # not used yet
stock: list[Tuple[str,str]] = []                   # will fill after deal
waste: list[Card] = []

# --- Deal cards to tableau (Klondike 1:7) ---
def deal_cards():
    global deck
    for col in range(7):
        for k in range(col + 1):
            rank, suit = deck.pop()
            image = card_images[(rank,suit)]
            card = Card(rank, suit, image=image, face_up=False)
            tableau[col].append(card)
            # flip the top card in this column
            tableau[col][-1].face_up=True

deal_cards()
# remaining deck becomes stock (face down)
stock = deck[:]    # copy what remains
deck.clear()

# --- Helpers for drawing pile positions ---
TABLEAU_X0, TABLEAU_Y0, TABLEAU_GAP_X = 100, 150, 100
FACEUP_GAP, FACEDOWN_GAP = 22, 10

def draw_tableau():
    for i, column in enumerate(tableau):
         x = TABLEAU_X0 + i * TABLEAU_GAP_X
         y = TABLEAU_Y0
         for card in column:
            card.draw(screen, x, y)
            y += FACEUP_GAP if card.face_up else FACEDOWN_GAP

STOCK_POS = (50, 50)
WASTE_POS = (150, 50)

# --- Game loop ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            # Click stock: deal one to waste or recycle
            stock_rect = pygame.Rect(STOCK_POS, CARD_SIZE)
            if stock_rect.collidepoint(mx, my):
                if stock:
                    r, s = stock.pop()
                    img = card_images[(r, s)]
                    waste.append(Card(r, s, img, face_up=True))
                else:
                    # recycle waste into stock, flip down
                    while waste:
                        c = waste.pop()
                        stock.append((c.rank, c.suit))

    screen.fill(GREEN)

    # Draw stock
    if stock:
        screen.blit(card_back, STOCK_POS)
    else:
        # empty slot outline
        pygame.draw.rect(screen, (230,230,230), (*STOCK_POS, *CARD_SIZE), width=2, border_radius=8)

    # Draw waste (top card only for now)
    if waste:
        waste[-1].draw(screen, *WASTE_POS)

    # Draw tableau
    draw_tableau()

    pygame.display.flip()

pygame.quit()