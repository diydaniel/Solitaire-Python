# --- animations.py
import pygame
import random
import math

class WinAnimation:
    """
    Card rain win animation.

    Usage:
        win = WinAnimation(screen, [(img, rect), ...])
        ...
        if win and not win.finished:
            win.draw()   # updates & renders on top of your normal scene
    """

    DURATION_MS = 30000          # total time of the animation
    NUM_DROPS = 80              # how many cards falling at once
    MIN_SPEED = 180             # px / second
    MAX_SPEED = 420             # px / second
    FADE_ALPHA = 35             # how much to darken each frame (0..255)

    def __init__(self, screen, cards):
        """
        cards: list of (image_surface, rect) for visible cards.
               We only need the surfaces; rects are ignored here.
        """
        self.screen = screen
        self.finished = False

        self.start_time = pygame.time.get_ticks()
        self.w, self.h = self.screen.get_size()

        # Extract card faces; fall back to simple white rect if none.
        self.card_surfs = [img.convert_alpha() for (img, _rect) in cards]
        if not self.card_surfs:
            dummy = pygame.Surface((80, 110), pygame.SRCALPHA)
            dummy.fill((255, 255, 255, 255))
            self.card_surfs = [dummy]

        # Semi-transparent overlay for trail / dim effect
        self.fade_surf = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        self.fade_surf.fill((0, 0, 0, self.FADE_ALPHA))

        # Precreate drops
        self.drops = []
        for _ in range(self.NUM_DROPS):
            self.drops.append(self._make_drop())

        # Fonts for center text
        self.font_big = pygame.font.Font(None, 80)
        self.font_small = pygame.font.Font(None, 28)

    # ------------------------------------------------------------------ helpers

    def _make_drop(self):
        """Create a single falling card."""
        img = random.choice(self.card_surfs)
        cw, ch = img.get_size()

        # Align x to a loose "column" grid to feel matrix-like
        column_width = cw + 10
        cols = max(1, self.w // column_width)
        col_index = random.randint(0, cols - 1)
        x = col_index * column_width + (column_width - cw) // 2

        # Start above the screen
        y = random.randint(-self.h, -ch)

        speed = random.uniform(self.MIN_SPEED, self.MAX_SPEED)
        return {
            "img": img,
            "x": float(x),
            "y": float(y),
            "speed": speed,
        }

    def _update_drops(self, dt):
        """Move each card down; respawn when it leaves the screen."""
        for d in self.drops:
            d["y"] += d["speed"] * dt
            if d["y"] > self.h:
                # respawn above
                new_drop = self._make_drop()
                d["img"] = new_drop["img"]
                d["x"] = new_drop["x"]
                d["y"] = new_drop["y"]
                d["speed"] = new_drop["speed"]

    def _draw_drops(self):
        """Draw all falling cards."""
        for d in self.drops:
            img = d["img"]
            self.screen.blit(img, (int(d["x"]), int(d["y"])))

    def _draw_overlay_text(self):
        """Draw 'YOU WIN' text in the center."""
        r = self.screen.get_rect()

        t1 = self.font_big.render("YOU WIN", True, (255, 255, 255))
        t2 = self.font_small.render("Press N for a new game", True, (220, 220, 220))

        self.screen.blit(t1, t1.get_rect(center=(r.centerx, r.centery - 24)))
        self.screen.blit(t2, t2.get_rect(center=(r.centerx, r.centery + 22)))

    # ------------------------------------------------------------------ main API

    def draw(self):
        """
        Update & render the win animation on top of whatever was already
        drawn to the screen (your game board).
        """
        if self.finished:
            # Draw a final dim + text pass so the message stays.
            self.screen.blit(self.fade_surf, (0, 0))
            self._draw_overlay_text()
            return

        now = pygame.time.get_ticks()
        elapsed = now - self.start_time

        # Convert ms to seconds for speed math
        dt = pygame.time.get_ticks() - getattr(self, "_last_ticks", now)
        self._last_ticks = now
        dt_sec = dt / 1000.0 if dt > 0 else 0.0

        # Slightly darken previous frame -> trail effect
        self.screen.blit(self.fade_surf, (0, 0))

        # Update and draw falling card faces
        self._update_drops(dt_sec)
        self._draw_drops()

        # Draw center text
        self._draw_overlay_text()

        # End condition
        if elapsed >= self.DURATION_MS:
            self.finished = True
