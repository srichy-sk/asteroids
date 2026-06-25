"""
GEOMETRY DASH — WAVE SPAM
=========================
Hold SPACE (or click) to fly the wave UP.
Release to fly DOWN.
Dodge the spikes and walls.
The game speeds up over time.

Controls:
  SPACE / Left Click  — hold to go up, release to go down
  R                   — restart after death
  Q / Escape          — quit
"""

import pygame
import sys
import math
import random

pygame.init()

# ── Constants ──────────────────────────────────────────────────────────────────
SW, SH   = 900, 540
FPS      = 60
GRAVITY  = 0.55        # diagonal speed change per frame
MAX_SPD  = 10           # max diagonal velocity
TRAIL_LEN = 22
WAVE_SPEED = 8

# Colours
C_BG       = (15,  10,  30)
C_BG2      = (20,  15,  40)
C_WAVE     = (0,  220, 255)
C_WAVE2    = (120, 60, 255)
C_SPIKE    = (255, 60,  80)
C_SPIKE2   = (200, 20,  40)
C_WALL     = (255, 80,  30)
C_WALL2    = (180, 40,  10)
C_FLOOR    = (60,  40, 120)
C_FLOOR_L  = (90,  65, 160)
C_GRID     = (255, 255, 255)
C_WHITE    = (255, 255, 255)
C_GOLD     = (255, 200,  50)
C_SCORE    = (200, 255, 255)
C_DEAD     = (255,  60,  60)
C_GLOW     = (0,  180, 255)

FLOOR_H = 60   # floor/ceiling thickness

screen = pygame.display.set_mode((SW, SH))
pygame.display.set_caption("Wave Spam — Geometry Dash")
clock  = pygame.time.Clock()

font_big  = pygame.font.SysFont("consolas", 52, bold=True)
font_med  = pygame.font.SysFont("consolas", 30, bold=True)
font_sm   = pygame.font.SysFont("consolas", 18)


# ── Helpers ────────────────────────────────────────────────────────────────────
def lerp_color(a, b, t):
    return tuple(int(a[i] + (b[i]-a[i])*t) for i in range(3))

def draw_text_glow(surf, text, font, color, glow_color, x, y):
    for dx, dy in [(-2,0),(2,0),(0,-2),(0,2)]:
        s = font.render(text, True, glow_color)
        surf.blit(s, (x+dx, y+dy))
    surf.blit(font.render(text, True, color), (x, y))

def draw_glow_circle(surf, color, pos, radius, alpha=80):
    s = pygame.Surface((radius*4, radius*4), pygame.SRCALPHA)
    pygame.draw.circle(s, (*color, alpha), (radius*2, radius*2), radius*2)
    surf.blit(s, (pos[0]-radius*2, pos[1]-radius*2))

def draw_glow_rect(surf, color, rect, alpha=70):
    s = pygame.Surface((rect[2]+20, rect[3]+20), pygame.SRCALPHA)
    pygame.draw.rect(s, (*color, alpha), (10, 10, rect[2], rect[3]), border_radius=4)
    surf.blit(s, (rect[0]-10, rect[1]-10))


# ── Spike obstacle ─────────────────────────────────────────────────────────────
class Spike:
    """Triangle spike from floor or ceiling."""
    SIZE = 65

    def __init__(self, x, from_top=False):
        self.x = float(x)
        self.from_top = from_top
        if from_top:
            self.y = FLOOR_H
        else:
            self.y = SH - FLOOR_H - self.SIZE

    def update(self, speed):
        self.x -= speed

    def draw(self, surf):
        s = self.SIZE
        x = int(self.x)
        if self.from_top:
            pts = [(x, self.y), (x+s, self.y), (x+s//2, self.y+s)]
        else:
            pts = [(x, self.y+s), (x+s, self.y+s), (x+s//2, self.y)]
        draw_glow_rect(surf, C_SPIKE, (x, int(self.y), s, s), alpha=50)
        pygame.draw.polygon(surf, C_SPIKE2, pts)
        pygame.draw.polygon(surf, C_SPIKE,  pts, 2)

    def hitbox(self):
        shrink = 8
        s = self.SIZE - shrink*2
        if self.from_top:
            return pygame.Rect(self.x+shrink, self.y+shrink, s, s-shrink)
        else:
            return pygame.Rect(self.x+shrink, self.y+shrink//2, s, s-shrink//2)

    def offscreen(self):
        return self.x < -self.SIZE - 20


# ── Wall obstacle ──────────────────────────────────────────────────────────────
class Wall:
    """Vertical wall with a gap to fly through."""
    WIDTH = 60
    MIN_GAP = 100

    def __init__(self, x, gap_y, gap_h):
        self.x     = float(x)
        self.gap_y = gap_y
        self.gap_h = gap_h

    def update(self, speed):
        self.x -= speed

    def draw(self, surf):
        x = int(self.x)
        playH = SH - FLOOR_H*2
        # top segment
        top_h = self.gap_y - FLOOR_H
        if top_h > 0:
            r = pygame.Rect(x, FLOOR_H, self.WIDTH, top_h)
            draw_glow_rect(surf, C_WALL, (x, FLOOR_H, self.WIDTH, top_h), alpha=50)
            pygame.draw.rect(surf, C_WALL2, r)
            pygame.draw.rect(surf, C_WALL,  r, 2)
        # bottom segment
        bot_y = self.gap_y + self.gap_h
        bot_h = SH - FLOOR_H - bot_y
        if bot_h > 0:
            r2 = pygame.Rect(x, bot_y, self.WIDTH, bot_h)
            draw_glow_rect(surf, C_WALL, (x, bot_y, self.WIDTH, bot_h), alpha=50)
            pygame.draw.rect(surf, C_WALL2, r2)
            pygame.draw.rect(surf, C_WALL,  r2, 2)

    def hitboxes(self):
        x = self.x
        playH = SH - FLOOR_H*2
        top_h = self.gap_y - FLOOR_H
        bot_y = self.gap_y + self.gap_h
        bot_h = SH - FLOOR_H - bot_y
        boxes = []
        if top_h > 0:
            boxes.append(pygame.Rect(x+3, FLOOR_H, self.WIDTH-6, top_h))
        if bot_h > 0:
            boxes.append(pygame.Rect(x+3, bot_y, self.WIDTH-6, bot_h))
        return boxes

    def offscreen(self):
        return self.x < -self.WIDTH - 20


# ── Particle ───────────────────────────────────────────────────────────────────
class Particle:
    def __init__(self, x, y, color, size=5, vel=None):
        self.x, self.y = float(x), float(y)
        self.color = color
        self.size  = size
        self.life  = 1.0
        if vel:
            self.vx, self.vy = vel
        else:
            angle = random.uniform(0, math.pi*2)
            spd   = random.uniform(1, 4)
            self.vx = math.cos(angle)*spd
            self.vy = math.sin(angle)*spd

    def update(self):
        self.x   += self.vx
        self.y   += self.vy
        self.life -= 0.03

    def draw(self, surf):
        if self.life <= 0:
            return
        alpha = int(self.life * 255)
        s = pygame.Surface((self.size*2+2, self.size*2+2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (self.size+1, self.size+1), int(self.size*self.life)+1)
        surf.blit(s, (int(self.x)-self.size, int(self.y)-self.size))

    @property
    def dead(self):
        return self.life <= 0


# ── Wave player ────────────────────────────────────────────────────────────────
class Wave:
    SIZE = 14

    def __init__(self):
        self.x   = 180.0
        self.y   = SH / 2.0
        self.vel = 0.0        # vertical velocity (positive = down)
        self.alive = True
        self.trail = []       # list of (x, y) positions
        self.anim  = 0

    def update(self, holding):
        if holding:
            self.y -= WAVE_SPEED
        else:
            self.y += WAVE_SPEED

        self.anim += 1

        self.trail.append((self.x, self.y))
        if len(self.trail) > TRAIL_LEN:
            self.trail.pop(0)

        if self.y - self.SIZE < FLOOR_H or self.y + self.SIZE > SH - FLOOR_H:
            self.alive = False

    def draw(self, surf):
        # Trail
        for i, (tx, ty) in enumerate(self.trail):
            t = i / TRAIL_LEN
            r = int(self.SIZE * 0.6 * t)
            if r < 1:
                continue
            alpha = int(t * 180)
            color = lerp_color(C_WAVE2, C_WAVE, t)
            s = pygame.Surface((r*2+2, r*2+2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*color, alpha), (r+1, r+1), r)
            surf.blit(s, (int(tx)-r, int(ty)-r))

        # Glow
        draw_glow_circle(surf, C_GLOW, (int(self.x), int(self.y)), self.SIZE+8, 60)

        # Diamond shape (wave icon)
        cx, cy = int(self.x), int(self.y)
        s      = self.SIZE
        rot    = math.atan2(self.vel, 6)  # tilt with velocity
        pts_raw = [(0, -s), (s, 0), (0, s), (-s, 0)]
        cos_r, sin_r = math.cos(rot), math.sin(rot)
        pts = [(cx + int(px*cos_r - py*sin_r),
                cy + int(px*sin_r + py*cos_r)) for px, py in pts_raw]

        pygame.draw.polygon(surf, C_WAVE2, pts)
        pygame.draw.polygon(surf, C_WAVE,  pts, 2)

        # Inner diamond
        inner = [(cx + int(px*0.5*cos_r - py*0.5*sin_r),
                  cy + int(px*0.5*sin_r + py*0.5*cos_r)) for px, py in pts_raw]
        pygame.draw.polygon(surf, C_WAVE, inner)

    def hitbox(self):
        r = self.SIZE - 5
        return pygame.Rect(self.x - r, self.y - r, r*2, r*2)


# ── Background ────────────────────────────────────────────────────────────────
def draw_background(scroll, speed):
    screen.fill(C_BG)
    # Moving grid
    grid_spacing = 80
    offset = int(scroll * 0.6) % grid_spacing
    for gx in range(-offset, SW + grid_spacing, grid_spacing):
        s = pygame.Surface((1, SH), pygame.SRCALPHA)
        s.fill((255,255,255,12))
        screen.blit(s, (gx, 0))
    for gy in range(FLOOR_H, SH - FLOOR_H, grid_spacing):
        s = pygame.Surface((SW, 1), pygame.SRCALPHA)
        s.fill((255,255,255,12))
        screen.blit(s, (0, gy))

    # Pulse lines (speed indicator)
    pulse_alpha = int(40 + 30 * math.sin(pygame.time.get_ticks() * 0.004))
    for gy in range(FLOOR_H + 40, SH - FLOOR_H, 60):
        s = pygame.Surface((SW, 1), pygame.SRCALPHA)
        col = lerp_color(C_WAVE2, C_WAVE, 0.5)
        s.fill((*col, pulse_alpha))
        screen.blit(s, (0, gy))


def draw_floor_ceiling():
    # Ceiling
    pygame.draw.rect(screen, C_FLOOR,   (0, 0, SW, FLOOR_H))
    pygame.draw.rect(screen, C_FLOOR_L, (0, FLOOR_H-4, SW, 4))
    # Floor
    pygame.draw.rect(screen, C_FLOOR,   (0, SH-FLOOR_H, SW, FLOOR_H))
    pygame.draw.rect(screen, C_FLOOR_L, (0, SH-FLOOR_H, SW, 4))

    # Animated neon edge lines
    t = pygame.time.get_ticks()
    for i in range(0, SW, 40):
        bright = int(150 + 100 * math.sin((t*0.003 + i*0.05)))
        col = (bright//2, 0, bright)
        pygame.draw.rect(screen, col, (i, FLOOR_H-2, 20, 2))
        pygame.draw.rect(screen, col, (i, SH-FLOOR_H, 20, 2))


# ── HUD ────────────────────────────────────────────────────────────────────────
def draw_hud(score, best, speed_mult, attempts):
    # Score
    draw_text_glow(screen, f"{score:06d}", font_med, C_SCORE, C_GLOW, 16, 12)
    # Best
    best_txt = font_sm.render(f"BEST {best:06d}", True, (140,140,200))
    screen.blit(best_txt, (16, 48))
    # Speed
    spd_txt = font_sm.render(f"SPEED x{speed_mult:.2f}", True, (180,120,255))
    screen.blit(spd_txt, (SW - 160, 12))
    # Attempts
    att_txt = font_sm.render(f"ATT {attempts}", True, (120,120,160))
    screen.blit(att_txt, (SW - 120, 34))
    # Hold hint
    hint = font_sm.render("HOLD SPACE to go UP", True, (80,80,120))
    screen.blit(hint, (SW//2 - hint.get_width()//2, SH - FLOOR_H + 18))


def draw_dead(score, best):
    ov = pygame.Surface((SW, SH), pygame.SRCALPHA)
    ov.fill((0, 0, 0, 160))
    screen.blit(ov, (0,0))
    draw_text_glow(screen, "YOU DIED", font_big, C_DEAD, (120,0,0),
                   SW//2 - font_big.size("YOU DIED")[0]//2, SH//2 - 80)
    draw_text_glow(screen, f"SCORE  {score:06d}", font_med, C_SCORE, C_GLOW,
                   SW//2 - font_med.size(f"SCORE  {score:06d}")[0]//2, SH//2)
    draw_text_glow(screen, f"BEST   {best:06d}", font_med, C_GOLD, (120,80,0),
                   SW//2 - font_med.size(f"BEST   {best:06d}")[0]//2, SH//2 + 40)
    r_txt = font_sm.render("[ R ] Restart    [ Q ] Quit", True, (180,180,220))
    screen.blit(r_txt, (SW//2 - r_txt.get_width()//2, SH//2 + 100))


# ── Obstacle generator ─────────────────────────────────────────────────────────
def gen_obstacle(score, difficulty):
    """Return a list of Spike/Wall objects to add."""
    kind = random.random()
    # As difficulty grows, wall/double-spike chance increases
    if kind < 0.40:
        # single spike
        from_top = random.random() < 0.5
        return [Spike(SW + 20, from_top)]
    elif kind < 0.65:
        # double spike (both top + bottom)
        return [Spike(SW + 20, True), Spike(SW + 20, False)]
    elif kind < 0.80:
        # cluster of 2 spikes same side
        side = random.random() < 0.5
        sep  = Spike.SIZE + random.randint(4, 14)
        return [Spike(SW + 20, side), Spike(SW + 20 + sep, side)]
    
    elif kind < 0.85:
        side = random.random() < 0.5

        return [
            Spike(SW+20, side),
            Spike(SW+90, side),
            Spike(SW+160, side)
        ]
    
    elif kind < 0.95:
        obs = []

        for i in range(4):
            obs.append(Spike(SW + 20 + i*70, True))
            obs.append(Spike(SW + 20 + i*70, False))

        return obs
    else:
        # wall with gap
        play_h = SH - FLOOR_H*2
        gap_h  = max(Wall.MIN_GAP, int(play_h * 0.42 - difficulty * 25))
        gap_h  = max(gap_h, 80)
        gap_y  = FLOOR_H + random.randint(10, max(11, play_h - gap_h - 10))
        return [Wall(SW + 20, gap_y, gap_h)]


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    best     = 0
    attempts = 0

    def new_game():
        nonlocal attempts
        attempts += 1
        wave_      = Wave()
        obstacles_ = []
        particles_ = []
        scroll_    = 0.0
        score_     = 0
        speed_     = 5.0          # pixel scroll speed
        next_obs_  = SW + random.randint(200, 360)
        dead_      = False
        death_particles_ = []
        return (wave_, obstacles_, particles_, scroll_,
                score_, speed_, next_obs_, dead_, death_particles_)

    (wave, obstacles, particles, scroll,
     score, speed, next_obs, dead, death_particles) = new_game()

    holding = False
    running = True

    while running:
        clock.tick(FPS)

        # ── Events ──────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    running = False
                if event.key == pygame.K_r and dead:
                    (wave, obstacles, particles, scroll,
                     score, speed, next_obs, dead, death_particles) = new_game()
                if event.key == pygame.K_SPACE:
                    holding = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    holding = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                holding = True
            if event.type == pygame.MOUSEBUTTONUP:
                holding = False

        # ── Update ──────────────────────────────────────────────────────────
        if not dead:
            scroll += speed
            score  += int(speed * 0.5)
            # Gradually speed up
            speed = min(5.0 + score / 4000, 14.0)
            difficulty = (speed - 5.0) / 9.0

            wave.update(holding)

            # Spawn obstacles
            if scroll + SW > next_obs:
                for obs in gen_obstacle(score, difficulty):
                    obstacles.append(obs)
                gap = random.randint(int(280 - difficulty*80), int(450 - difficulty*100))
                gap = max(gap, 120)
                next_obs = int(scroll) + SW + gap

            # Update obstacles
            for obs in obstacles[:]:
                obs.update(speed)
                if obs.offscreen():
                    obstacles.remove(obs)

            # Trail particles (every 3 frames)
            if pygame.time.get_ticks() % 3 == 0:
                particles.append(Particle(wave.x - 10, wave.y,
                    lerp_color(C_WAVE2, C_WAVE, random.random()), size=4,
                    vel=(-random.uniform(1,3), random.uniform(-1,1))))

            # Collision detection
            wave_hb = wave.hitbox()
            hit = False
            if not wave.alive:
                hit = True
            if not hit:
                for obs in obstacles:
                    if isinstance(obs, Spike):
                        if wave_hb.colliderect(obs.hitbox()):
                            hit = True; break
                    elif isinstance(obs, Wall):
                        for hb in obs.hitboxes():
                            if wave_hb.colliderect(hb):
                                hit = True; break
                    if hit:
                        break

            if hit:
                dead = True
                if score > best:
                    best = score
                # Explosion particles
                for _ in range(40):
                    death_particles.append(
                        Particle(wave.x, wave.y,
                                 random.choice([C_WAVE, C_WAVE2, C_WHITE, C_DEAD]),
                                 size=random.randint(4,10)))

        # ── Draw ────────────────────────────────────────────────────────────
        draw_background(scroll, speed)
        draw_floor_ceiling()

        for obs in obstacles:
            obs.draw(screen)

        # Particles
        for p in particles[:]:
            p.update()
            p.draw(screen)
            if p.dead:
                particles.remove(p)

        for p in death_particles[:]:
            p.update()
            p.draw(screen)
            if p.dead:
                death_particles.remove(p)

        if not dead:
            wave.draw(screen)

        speed_mult = speed / 5.0
        draw_hud(score, best, speed_mult, attempts)

        if dead:
            draw_dead(score, best)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()