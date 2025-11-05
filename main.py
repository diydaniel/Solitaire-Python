# --- main.py
import pygame as pg
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from game import Game
from menu import Menu, MenuResult

# ---------------------------------------------------------------------------------------------------
# --- Function:
def run_one_game_session(screen):

    """
    Runs one game session using your existing Game API,
    returns when the player exits or presses ESC.
    """

    clock = pg.time.Clock()
    game = Game(screen)
    running_game = True

    while running_game:

        dt = clock.tick(60) / 1000.0

        for e in pg.event.get():
            if e.type == pg.QUIT:
                return False  # exit app entirely
            elif e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
                # ESC returns to menu
                running_game = False
                break
            else:
                game.handle_event(e)

        # If you have an update method, call it here:

        game.update(dt)
        game.draw()
        pg.display.flip()

    return True  # finished game, go back to menu

# ---------------------------------------------------------------------------------------------------
# --- Function:
def main():
    pg.init()
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pg.display.set_caption("Solitaire") # --- Title at top grey bar

    app_running = True
    while app_running:
        # Show menu
        menu = Menu(screen)
        choice = menu.run()

        if choice == MenuResult.START:
            # Run one game; if it returns False, user closed window
            app_running = run_one_game_session(screen)
        else:
            # Quit from menu
            app_running = False

    pg.quit()

if __name__ == "__main__":
    main()