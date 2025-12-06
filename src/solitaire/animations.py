# --- animations.py
import pygame
import random
import math

# ---------------------------------------------------------------------------------------------------
# --- Object Blue Print: WinAnimation
class WinAnimation:

    """
    Minimalist win animation:
      - each card floats up with a cosine ease and fades out
      - leaves soft trailing sparkles that drift upward and fade
      - dims the scene with a translucent overlay and draws 'YOU WIN'
    Usage:
      win = WinAnimation(screen, [(img, rect), ...])
      ...
      if win and not win.finished:
          win.draw()   # updates & renders on top of your normal scene
    """

    DURATION_MS = 2000          # per-card animation time
    PER_CARD_DELAY_MS = 150     # staggering
    OVERLAY_ALPHA = 170         # 0..255
    TRAIL_SPAWN_ALPHA = (180, 220)
    TRAIL_FADE = 4              # alpha per frame
    TRAIL_RISE = 1.0            # px per frame
    TRAIL_RADIUS = 3
    MAX_Y_OFFSET = 500          # peak float distance (px)

# ---------------------------------------------------------------------------------------------------
    def __init__(self, screen, cards):

        """
        cards: list of (image_surface, rect) for visible cards.
               rects are only read to capture base positions (not mutated).
        """

        self.screen = screen
        self.finished = False

        # cache card snapshots & schedule
        now = pygame.time.get_ticks()
        self.start_time = now
        self.cards = []  # list of dicts with base state
        delay = 0
        for img, rect in cards:
            self.cards.append({
                "img": img.convert_alpha(),
                "base_center": rect.center,   # immutable base
                "w": rect.width,
                "h": rect.height,
                "delay": delay,               # ms
            })
            delay += self.PER_CARD_DELAY_MS

        self.trails = []  # list of (x, y, alpha)
        self._trail_circle = self._make_trail_circle(self.TRAIL_RADIUS)
        self._overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)

        # pre-allocate a rect to avoid churn
        self._work_rect = pygame.Rect(0, 0, 0, 0)

# ---------------------------------------------------------------------------------------------------
    # ---------- helpers ----------
    def _make_trail_circle(self, r):
        s = pygame.Surface((2*r, 2*r), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 255, 255, 255), (r, r), r)
        return s

    def _card_progress(self, now_ms, delay_ms):
        t = (now_ms - self.start_time) - delay_ms
        if t <= 0:
            return 0.0
        return min(1.0, t / self.DURATION_MS)

    def _ease_cos(self, p):
        # 0..1 -> 0..1 smooth (cosine)
        return (1.0 - math.cos(p * math.pi)) * 0.5
    
# ---------------------------------------------------------------------------------------------------
    # ---------- API ----------
    def draw(self):
        """Update positions and render the whole celebration on top of the scene."""
        if self.finished:
            # Still draw the overlay text one last time so it stays visible.
            self._draw_overlay_and_text()
            return

        now = pygame.time.get_ticks()
        all_done = True

        # cards
        for c in self.cards:
            p = self._card_progress(now, c["delay"])
            if p < 1.0:
                all_done = False

            if p <= 0.0:
                continue

            # eased vertical travel and alpha fade
            eased = self._ease_cos(p)
            y_off = -self.MAX_Y_OFFSET * eased
            alpha = max(0, 255 - int(p * 255))

            # position relative to base center
            cx, cy = c["base_center"]
            x = int(cx - c["w"] // 2)
            y = int(cy - c["h"] // 2 + y_off)

            # glow behind the card (cheaper than blur)
            glow = pygame.Surface((c["w"], c["h"]), pygame.SRCALPHA)
            glow.fill((255, 255, 255, int(alpha * 0.5)))
            self.screen.blit(glow, (x, y))

            # card itself with fade
            img = c["img"]
            if alpha < 255:
                img = img.copy()
                img.set_alpha(alpha)
            self.screen.blit(img, (x, y))

            # spawn a sparkle at the current center
            if alpha > 0 and (p < 1.0):
                tx = int(cx)
                ty = int(cy + y_off)
                self.trails.append((
                    tx,
                    ty,
                    random.randint(*self.TRAIL_SPAWN_ALPHA)
                ))

        # trails (render to screen with alpha via pre-made circle)
        if self.trails:
            next_trails = []
            for (x, y, a) in self.trails:
                if a <= 0:
                    continue
                s = self._trail_circle.copy()
                s.set_alpha(a)
                self.screen.blit(s, (x - self.TRAIL_RADIUS, y - self.TRAIL_RADIUS))
                a2 = a - self.TRAIL_FADE
                y2 = y - self.TRAIL_RISE
                if a2 > 0:
                    next_trails.append((x, y2, a2))
            self.trails = next_trails
            if next_trails:
                all_done = False

        # overlay + text last
        self._draw_overlay_and_text()

        # finished?
        if all_done:
            self.finished = True

# ---------------------------------------------------------------------------------------------------
    def _draw_overlay_and_text(self):
        # dim without erasing your scene
        self._overlay.fill((0, 0, 0, self.OVERLAY_ALPHA))
        self.screen.blit(self._overlay, (0, 0))

        # centered text
        font_big = pygame.font.Font(None, 80)
        font_small = pygame.font.Font(None, 28)
        r = self.screen.get_rect()

        t1 = font_big.render("YOU WIN", True, (255, 255, 255))
        t2 = font_small.render("Press N to deal a new game", True, (230, 230, 230))

        self.screen.blit(t1, t1.get_rect(center=(r.centerx, r.centery - 24)))
        self.screen.blit(t2, t2.get_rect(center=(r.centerx, r.centery + 26)))
