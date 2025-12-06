# --- menu.py
import pygame
import math
from enum import Enum, auto

from .model import GameVariant

FONT_SIZE = 48
FPS = 60


class MenuResult(Enum):
    START = auto()
    QUIT = auto()


class Button:
    def __init__(self, rect, text, font, on_click):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.on_click = on_click
        self.hover = False

    def draw(self, surf):
        bg = (60, 60, 70) if not self.hover else (85, 85, 110)
        border = (200, 200, 220)
        pygame.draw.rect(surf, bg, self.rect, border_radius=12)
        pygame.draw.rect(surf, border, self.rect, width=2, border_radius=12)
        label = self.font.render(self.text, True, (240, 240, 250))
        surf.blit(label, label.get_rect(center=self.rect.center))

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.hover
        ):
            self.on_click()


class Menu:
    def __init__(self, screen, title="Choose Your Adventure"):
        self.screen = screen
        self.title = title
        self.clock = pygame.time.Clock()
        self.result = None

        # Game variant state
        self.variants = [GameVariant.KLONDIKE, GameVariant.SPIDER]
        self.variant_index = 0
        self.selected_variant = self.variants[self.variant_index]
        self.variant_dropdown_open = False

        # Fonts
        self.title_font = pygame.font.SysFont("arial", FONT_SIZE, bold=True)
        self.menu_font = pygame.font.SysFont("arial", 36)
        self.small_font = pygame.font.SysFont("arial", 24)

        w, h = self.screen.get_size()

        # Layout: 3 rows -> Adventure dropdown, Start, Quit
        button_w, button_h, spacing = 380, 60, 16
        num_rows = 3
        total_h = num_rows * button_h + (num_rows - 1) * spacing
        start_y = h // 2 - total_h // 2
        cx = w // 2 - button_w // 2

        # 1) Adventure dropdown (row 0)
        variant_y = start_y
        self.variant_button = Button(
            (cx, variant_y, button_w, button_h),
            "",
            self.menu_font,
            self._toggle_variant_dropdown,
        )
        self.variant_options = [
            (GameVariant.KLONDIKE, "Klondike"),
            (GameVariant.SPIDER, "Spider"),
        ]
        self._update_variant_button_label()

        # 2) Start game (row 1)
        start_y_btn = start_y + (button_h + spacing)

        def start_game():
            self.result = MenuResult.START

        self.start_button = Button(
            (cx, start_y_btn, button_w, button_h),
            "Start game",
            self.menu_font,
            start_game,
        )

        # 3) Quit (row 2)
        quit_y = start_y + 2 * (button_h + spacing)

        def quit_():
            self.result = MenuResult.QUIT

        self.quit_button = Button(
            (cx, quit_y, button_w, button_h),
            "Quit",
            self.menu_font,
            quit_,
        )

        self.buttons = [self.start_button, self.quit_button]

    # --- variant label / dropdown helpers -----------------------------------
    def _update_variant_button_label(self):
        mapping = {
            GameVariant.KLONDIKE: "Klondike",
            GameVariant.SPIDER: "Spider",
        }
        self.variant_button.text = mapping.get(self.selected_variant, "Adventure")

    def _toggle_variant_dropdown(self):
        self.variant_dropdown_open = not self.variant_dropdown_open

    def _select_variant(self, variant):
        self.selected_variant = variant
        self.variant_dropdown_open = False
        self._update_variant_button_label()

    def _get_variant_option_rects(self):
        rects = []
        base = self.variant_button.rect
        option_h = base.height
        option_w = base.width
        x = base.x
        for i, (variant, label) in enumerate(self.variant_options):
            y = base.bottom + 4 + i * (option_h + 2)
            rects.append((variant, label, pygame.Rect(x, y, option_w, option_h)))
        return rects

    def _draw_dropdown(self, option_rects):
        for _, label, r in option_rects:
            bg = (40, 40, 50)
            border = (200, 200, 220)
            pygame.draw.rect(self.screen, bg, r, border_radius=10)
            pygame.draw.rect(self.screen, border, width=2, rect=r, border_radius=10)
            text_surf = self.menu_font.render(label, True, (240, 240, 250))
            self.screen.blit(text_surf, text_surf.get_rect(center=r.center))

    def _draw_dropdown_arrow(self, button: Button, is_open: bool):
        cx = button.rect.right - 24
        cy = button.rect.centery
        size = 8
        if is_open:
            points = [
                (cx - size, cy + size // 2),
                (cx + size, cy + size // 2),
                (cx,        cy - size),
            ]
        else:
            points = [
                (cx - size, cy - size // 2),
                (cx + size, cy - size // 2),
                (cx,        cy + size),
            ]
        pygame.draw.polygon(self.screen, (240, 240, 250), points)

    # --- drawing helpers -----------------------------------------------------
    def draw_title(self):
        w, _ = self.screen.get_size()
        label = self.title_font.render(self.title, True, (240, 240, 250))
        self.screen.blit(label, label.get_rect(center=(w // 2, 80)))

    def draw_background(self, t):
        w, h = self.screen.get_size()
        self.screen.fill((25, 28, 35))
        for i in range(0, h, 40):
            shade = 25 + int(10 * (1 + math.sin(i * 0.02 + t * 0.8)))
            pygame.draw.rect(
                self.screen, (shade, shade, shade + 5), (0, i, w, 40)
            )

    # --- main loop -----------------------------------------------------------
    def run(self):
        running = True
        t = 0.0

        while running and self.result is None:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.result = MenuResult.QUIT

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.result = MenuResult.QUIT

                # Mouse handling
                handled_dropdown_click = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos

                    # Variant dropdown first
                    if self.variant_dropdown_open:
                        for variant, label, r in self._get_variant_option_rects():
                            if r.collidepoint(mx, my):
                                self._select_variant(variant)
                                handled_dropdown_click = True
                                break

                        if not handled_dropdown_click and not self.variant_button.rect.collidepoint(mx, my):
                            self.variant_dropdown_open = False

                        if handled_dropdown_click:
                            continue

                # Buttons
                self.variant_button.handle_event(event)
                for b in self.buttons:
                    b.handle_event(event)

            # Draw
            t += 1 / FPS
            self.draw_background(t)
            self.draw_title()

            # Buttons and dropdown
            for b in self.buttons:
                b.draw(self.screen)

            self.variant_button.draw(self.screen)
            self._draw_dropdown_arrow(self.variant_button, self.variant_dropdown_open)

            if self.variant_dropdown_open:
                self._draw_dropdown(self._get_variant_option_rects())

            # Hints
            w, h = self.screen.get_size()
            hint1 = self.small_font.render(
                "Choose an Adventure, then Start game", True, (170, 175, 190)
            )
            hint2 = self.small_font.render(
                "ESC to quit", True, (170, 175, 190)
            )
            self.screen.blit(hint1, hint1.get_rect(center=(w // 2, h - 60)))
            self.screen.blit(hint2, hint2.get_rect(center=(w // 2, h - 30)))

            pygame.display.flip()
            self.clock.tick(FPS)

        return self.result or MenuResult.QUIT
