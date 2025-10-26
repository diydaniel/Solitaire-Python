# main.py
import pygame as pg
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from game import Game

def main():
    pg.init()
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pg.display.set_caption("Solitaire")
    clock = pg.time.Clock()

    game = Game(screen)
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for e in pg.event.get():
            if e.type == pg.QUIT:
                running = False
            else:
                game.handle_event(e)

        game.draw()
        pg.display.flip()

    pg.quit()

if __name__ == "__main__":
    main()