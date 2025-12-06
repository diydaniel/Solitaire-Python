# --- app.py
import pygame as pg

from . import config
from .config import WindowPreset
from .game import Game
from .menu import Menu, MenuResult


def run_one_game_session(screen: pg.Surface, variant):
    """
    Runs one game session at a fixed window size.

    Returns:
        False -> exit app entirely (window close)
        True  -> go back to menu
    """
    clock = pg.time.Clock()
    ui_font = pg.font.SysFont("arial", 20)

    game = Game(screen, variant)
    running_game = True

    # In-game menu dropdown state
    menu_open = False

    while running_game:
        dt = clock.tick(60) / 1000.0
        sw, sh = screen.get_size()

        # --- "Menu" button in top-left ---
        menu_button_rect = pg.Rect(10, 10, 120, 32)

        # --- dropdown options right under the button ---
        option_height = 30
        option_width = menu_button_rect.width
        option_spacing = 2

        options = [
            ("new",  "New game"),
            ("quit", "Main Menu"),
        ]

        option_rects: list[tuple[str, str, pg.Rect]] = []
        for i, (key, label) in enumerate(options):
            r = pg.Rect(
                menu_button_rect.x,
                menu_button_rect.bottom + 4 + i * (option_height + option_spacing),
                option_width,
                option_height,
            )
            option_rects.append((key, label, r))

        # ------------- event loop -------------
        for e in pg.event.get():
            if e.type == pg.QUIT:
                return False  # exit the whole app

            if e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
                if menu_open:
                    # ESC closes dropdown first
                    menu_open = False
                else:
                    # ESC returns to main menu
                    running_game = False
                break

            if e.type == pg.MOUSEBUTTONDOWN and e.button == 1:
                mx, my = e.pos

                if menu_open:
                    # 1) Click on an option
                    handled = False
                    for key, label, r in option_rects:
                        if r.collidepoint(mx, my):
                            handled = True
                            if key == "new":
                                game.new_game()
                                menu_open = False
                            elif key == "quit":
                                running_game = False
                                menu_open = False
                            break

                    if handled:
                        break  # handled click; no forwarding to game this frame

                    # 2) Click on the menu button again -> close dropdown
                    if menu_button_rect.collidepoint(mx, my):
                        menu_open = False
                        # don't forward this click to the game
                        continue

                    # 3) Click anywhere else -> close dropdown and forward to game
                    menu_open = False
                    # fall through to game.handle_event(e) below

                else:
                    # Dropdown closed: click on Menu button opens it
                    if menu_button_rect.collidepoint(mx, my):
                        menu_open = True
                        # don't send this click to game
                        continue

            # If we reach here, either dropdown is closed,
            # or a click outside the dropdown should still go to the game
            if not running_game:
                break

            if not menu_open:
                game.handle_event(e)
            else:
                # When menu is open, only clicks outside dropdown get here
                # (from the "click outside" path above)
                # You can choose to *not* forward them; for now, we do:
                game.handle_event(e)

        if not running_game:
            break

        # ------------- update + draw -------------
        if not menu_open:
            game.update(dt)

        game.draw()

        # --- draw "Menu" button ---
        pg.draw.rect(screen, (40, 40, 50), menu_button_rect, border_radius=8)
        pg.draw.rect(screen, (200, 200, 220), menu_button_rect, width=2, border_radius=8)
        label = ui_font.render("Menu", True, (240, 240, 250))
        screen.blit(label, label.get_rect(center=menu_button_rect.center))

        # --- draw dropdown under the button ---
        if menu_open:
            for key, opt_label, r in option_rects:
                pg.draw.rect(screen, (35, 40, 55), r, border_radius=6)
                pg.draw.rect(screen, (210, 210, 230), r, width=1, border_radius=6)
                txt = ui_font.render(opt_label, True, (240, 240, 250))
                screen.blit(txt, txt.get_rect(center=r.center))

        pg.display.flip()

    return True  # go back to main menu


def main():
    pg.init()
    MENU_SIZE = (960, 540)
    pg.display.set_caption("codejacket.io - Solitaire")

    app_running = True
    while app_running:
        # --- fixed-size menu window ---
        screen = pg.display.set_mode(MENU_SIZE, 0)
        menu = Menu(screen)
        choice = menu.run()

        if choice == MenuResult.START:
            # Use the variant chosen in the menu
            variant = menu.selected_variant

            # Single game window size
            flags, w, h = config.set_window_preset(WindowPreset.MEDIUM)
            screen = pg.display.set_mode((w, h), flags)

            # Run one game session
            app_running = run_one_game_session(screen, variant)
        else:
            app_running = False

    pg.quit()


if __name__ == "__main__":
    main()
