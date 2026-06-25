"""
🐧 Penguin Platformer
=====================
Controls:
  Arrow Left / Right  — Move
  Space / Up Arrow    — Jump (double jump supported)
  E                   — Grab / release nearest box
  R                   — Restart level
  Q                   — Quit

Goals per level:
  Collect all coins, then find the door (green arch) to advance!
"""

import pygame
import sys
import math

pygame.init()

# ── Constants ──────────────────────────────────────────────────────────────────
SCREEN_W, SCREEN_H = 900, 600
FPS        = 60
TILE       = 40
GRAVITY    = 0.55
JUMP_POWER = -13
MAX_FALL   = 18

# Colours
SKY        = (135, 206, 235)
SKY2       = (170, 220, 255)
C_WHITE    = (255, 255, 255)
C_BLACK    = (0,   0,   0)
C_COIN     = (255, 215,  0)
C_COIN_IN  = (255, 240, 100)
C_DOOR     = (34, 139,  34)
C_DOOR_IN  = (80, 200,  80)
C_BOX      = (180, 120,  60)
C_BOX_D    = (140,  90,  40)
C_GROUND   = (100, 160,  80)
C_GROUND_D = ( 80, 100,  50)
C_PLAT     = (160, 110,  60)
C_PLAT_D   = (120,  80,  40)
C_SHADOW   = (0, 0, 0, 80)
C_UI_BG    = (0, 0, 0, 140)
C_STAR     = (255, 255, 200)

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("🐧 Penguin Platformer")
clock = pygame.time.Clock()

font_big   = pygame.font.SysFont("segoeui", 48, bold=True)
font_med   = pygame.font.SysFont("segoeui", 28, bold=True)
font_small = pygame.font.SysFont("segoeui", 20)


# ── Drawing helpers ────────────────────────────────────────────────────────────
def draw_rounded_rect(surf, color, rect, radius=8):
    pygame.draw.rect(surf, color, rect, border_radius=radius)

def draw_text_shadow(surf, text, font, color, x, y, shadow_color=(0,0,0), offset=2):
    s = font.render(text, True, shadow_color)
    surf.blit(s, (x+offset, y+offset))
    t = font.render(text, True, color)
    surf.blit(t, (x, y))

def draw_background(scroll_x):
    """Parallax sky + distant mountains."""
    screen.fill(SKY)
    # Sun
    pygame.draw.circle(screen, (255, 240, 100), (750, 80), 50)
    pygame.draw.circle(screen, (255, 255, 180), (750, 80), 42)
    # Distant mountains (parallax 0.2)
    px = int(scroll_x * 0.2) % SCREEN_W
    for mx in range(-200, SCREEN_W + 400, 220):
        bx = mx - px
        pts = [(bx, SCREEN_H), (bx+110, SCREEN_H-160), (bx+220, SCREEN_H)]
        pygame.draw.polygon(screen, (160, 180, 200), pts)
        pts2 = [(bx+30, SCREEN_H), (bx+110, SCREEN_H-110), (bx+190, SCREEN_H)]
        pygame.draw.polygon(screen, (190, 210, 220), pts2)
    # Clouds (parallax 0.1)
    cx = int(scroll_x * 0.1)
    for ox, oy, size in [(100,80,60),(350,50,45),(600,90,55),(800,60,40),
                          (-150,70,50),(1050,85,65)]:
        bx2 = (ox - cx) % (SCREEN_W + 200) - 100
        for dx, dy, r in [(0,0,size),(size//2,-size//4,size*3//4),(size,0,size//2)]:
            pygame.draw.circle(screen, C_WHITE, (bx2+dx, oy+dy), r)


def draw_tile(surf, rect, top_color, side_color):
    """Draw a 3-D-ish tile."""
    pygame.draw.rect(surf, side_color, rect, border_radius=4)
    top = pygame.Rect(rect.x, rect.y, rect.w, 10)
    pygame.draw.rect(surf, top_color, top, border_radius=4)


def draw_penguin(surf, x, y, facing, anim, grabbed):
    """Draw an ASCII-art-style pixel penguin."""
    # Body (white belly, black back)
    # Scale: body ~36x40 px
    bx, by = int(x), int(y)

    # Shadow
    shadow = pygame.Surface((36, 10), pygame.SRCALPHA)
    shadow.fill((0,0,0,0))
    pygame.draw.ellipse(shadow, (0,0,0,60), (0,0,36,10))
    surf.blit(shadow, (bx, by+36))

    # Flip surface for direction
    penguin_surf = pygame.Surface((36, 40), pygame.SRCALPHA)
    penguin_surf.fill((0,0,0,0))

    # Black body outline
    pygame.draw.ellipse(penguin_surf, (20,20,20),   (3, 6, 30, 32))
    # White belly
    pygame.draw.ellipse(penguin_surf, (240,240,240), (8, 12, 20, 22))
    # Head
    pygame.draw.circle(penguin_surf, (20,20,20), (18, 8), 10)
    # White face patch
    pygame.draw.ellipse(penguin_surf, (240,240,240), (11, 4, 14, 12))
    # Eyes
    eye_x = 22 if facing == 1 else 14
    pygame.draw.circle(penguin_surf, C_BLACK,    (eye_x, 6), 3)
    pygame.draw.circle(penguin_surf, C_WHITE,    (eye_x, 6), 1)
    # Beak
    beak_x = 27 if facing == 1 else 5
    pygame.draw.polygon(penguin_surf, (255,160,0),
        [(beak_x, 9),(beak_x+(4 if facing==1 else -4),11),(beak_x,13)])

    # Feet (animated bob)
    bob = int(math.sin(anim * 0.3) * 3) if grabbed == 0 else 0
    pygame.draw.ellipse(penguin_surf, (255,140,0), (4,  34+bob, 10, 6))
    pygame.draw.ellipse(penguin_surf, (255,140,0), (22, 34-bob, 10, 6))

    # Wings (arms)
    wing_bob = int(math.sin(anim * 0.4) * 4)
    if grabbed:
        # Arms out when carrying
        pygame.draw.ellipse(penguin_surf, (20,20,20), (0, 14, 8, 16))
        pygame.draw.ellipse(penguin_surf, (20,20,20), (28, 14, 8, 16))
    else:
        pygame.draw.ellipse(penguin_surf, (20,20,20), (0, 16+wing_bob, 8, 12))
        pygame.draw.ellipse(penguin_surf, (20,20,20), (28, 16-wing_bob, 8, 12))

    if facing == -1:
        penguin_surf = pygame.transform.flip(penguin_surf, True, False)

    surf.blit(penguin_surf, (bx, by))


# ── Level definitions ──────────────────────────────────────────────────────────
# Each level: list of tiles (type, col, row), coins, boxes, door
#  type: 'G'=ground, 'P'=platform
# Tiles are 40px; level coords in tile units

LEVELS = [
    # ── Level 1: Tutorial ─────────────────────────────────────────────────────
    {
        "name": "Frosty Fields",
        "bg_color": SKY,
        "tiles": (
            # Ground floor
            [(  'G', c, 13) for c in range(0, 30)]
            + [('G', c, 14) for c in range(0, 30)]
            # Platforms
            + [('P', c, 10) for c in range(3, 7)]
            + [('P', c,  8) for c in range(8, 12)]
            + [('P', c, 10) for c in range(13, 17)]
            + [('P', c,  7) for c in range(18, 22)]
            + [('P', c,  9) for c in range(23, 27)]
        ),
        "coins": [
            (4.5, 9), (5.5, 9),
            (9.5, 7), (10.5, 7),
            (14.5, 9), (15.5, 9),
            (19.5, 6), (20.5, 6),
            (24.5, 8),
        ],
        "boxes": [(6, 12), (15, 12)],
        "door": (26, 12),
        "spawn": (1, 12),
    },

    # ── Level 2: Box Puzzle ───────────────────────────────────────────────────
    {
        "name": "Box Canyon",
        "bg_color": (180, 200, 230),
        "tiles": (
            [(  'G', c, 13) for c in range(0, 32)]
            + [('G', c, 14) for c in range(0, 32)]
            + [('P', c, 10) for c in range(2, 6)]
            + [('P', c,  7) for c in range(7, 11)]
            + [('P', c, 11) for c in range(12, 14)]   # small ledge (needs box)
            + [('P', c,  8) for c in range(16, 20)]
            + [('P', c,  5) for c in range(21, 26)]
            + [('P', c,  8) for c in range(26, 30)]
        ),
        "coins": [
            (3, 9), (4, 9),
            (8, 6), (9, 6), (10, 6),
            (13, 10),
            (17, 7), (18, 7),
            (22, 4), (23, 4), (24, 4),
            (27, 7),
        ],
        "boxes": [(1, 12), (5, 12), (10, 12)],
        "door": (28, 7),
        "spawn": (0, 12),
    },

    # ── Level 3: Sky High ─────────────────────────────────────────────────────
    {
        "name": "Cloud Summit",
        "bg_color": (100, 160, 220),
        "tiles": (
            [(  'G', c, 14) for c in range(0, 3)]
            + [('P', c, 11) for c in range(3,  7)]
            + [('P', c,  8) for c in range(6,  10)]
            + [('P', c,  5) for c in range(9,  13)]
            + [('P', c,  8) for c in range(13, 17)]
            + [('P', c, 11) for c in range(17, 21)]
            + [('P', c,  8) for c in range(20, 24)]
            + [('P', c,  5) for c in range(24, 28)]
            + [('P', c,  3) for c in range(27, 32)]
            + [('G', c, 14) for c in range(29, 35)]
        ),
        "coins": [
            (3.5,10),(4.5,10),(5.5,10),
            (6.5,7),(7.5,7),(8.5,7),
            (9.5,4),(10.5,4),(11.5,4),
            (14,7),(15,7),
            (18,10),(19,10),
            (21,7),(22,7),(23,7),
            (25,4),(26,4),(27,4),
            (28,2),(29,2),(30,2),
        ],
        "boxes": [(1, 13), (8, 7)],
        "door": (31, 13),
        "spawn": (0, 13),
    },
]


# ── Game classes ───────────────────────────────────────────────────────────────
class Tile:
    def __init__(self, kind, col, row):
        self.kind = kind
        self.rect = pygame.Rect(col * TILE, row * TILE, TILE, TILE)

    def draw(self, surf, offset_x):
        r = self.rect.move(-offset_x, 0)
        if r.right < -10 or r.left > SCREEN_W + 10:
            return
        if self.kind == 'G':
            draw_tile(surf, r, C_GROUND, C_GROUND_D)
            # Grass tufts on top
            for gx in range(r.x + 4, r.x + TILE, 8):
                pygame.draw.line(surf, (60,180,60), (gx, r.y), (gx+2, r.y-5), 2)
        else:
            draw_tile(surf, r, C_PLAT, C_PLAT_D)


class Coin:
    def __init__(self, cx, cy):
        self.x = cx * TILE
        self.y = cy * TILE
        self.radius = 10
        self.collected = False
        self.anim = 0

    def update(self):
        self.anim += 1

    def draw(self, surf, offset_x):
        if self.collected:
            return
        sx = int(self.x - offset_x)
        sy = int(self.y + math.sin(self.anim * 0.1) * 4)
        if sx < -20 or sx > SCREEN_W + 20:
            return
        # Outer ring
        pygame.draw.circle(surf, C_COIN, (sx, sy), self.radius)
        pygame.draw.circle(surf, C_COIN_IN, (sx, sy), self.radius - 3)
        # $ symbol hint
        pygame.draw.circle(surf, C_COIN, (sx, sy), 3)

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius,
                           self.radius*2, self.radius*2)


class Box:
    SIZE = 36
    def __init__(self, cx, cy):
        self.rect = pygame.Rect(cx * TILE + 2, cy * TILE + (TILE - self.SIZE),
                                self.SIZE, self.SIZE)
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.grabbed = False

    def draw(self, surf, offset_x):
        r = self.rect.move(-offset_x, 0)
        draw_rounded_rect(surf, C_BOX, r, 5)
        # Wood grain lines
        for i in range(1, 3):
            lx = r.x + r.w * i // 3
            pygame.draw.line(surf, C_BOX_D, (lx, r.y+4), (lx, r.bottom-4), 2)
        pygame.draw.line(surf, C_BOX_D, (r.x+4, r.y + r.h//2), (r.right-4, r.y+r.h//2), 2)
        draw_rounded_rect(surf, C_BOX_D, r, 5)
        pygame.draw.rect(surf, C_BOX_D, r, 3, border_radius=5)

    def apply_gravity(self, tiles):
        if self.grabbed:
            return
        self.vel_y = min(self.vel_y + GRAVITY, MAX_FALL)
        self.rect.y += self.vel_y
        self.on_ground = False
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.vel_y > 0:
                    self.rect.bottom = tile.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = tile.rect.bottom
                    self.vel_y = 0


class Door:
    W, H = 48, 64
    def __init__(self, cx, cy):
        self.rect = pygame.Rect(cx * TILE - 4, cy * TILE - (self.H - TILE), self.W, self.H)
        self.open = False
        self.anim = 0

    def draw(self, surf, offset_x):
        r = self.rect.move(-offset_x, 0)
        if r.right < 0 or r.left > SCREEN_W:
            return
        self.anim += 1
        # Frame
        pygame.draw.rect(surf, (40, 100, 40), r, border_radius=24)
        # Door body
        inner = r.inflate(-8, -4)
        inner.height -= 4
        inner.top += 4
        col = (80,200,80) if self.open else (40,160,40)
        pygame.draw.rect(surf, col, inner, border_radius=20)
        # Arrow / star pulse when open
        if self.open:
            pulse = abs(math.sin(self.anim * 0.1)) * 20
            star_col = (255, 255, int(100 + pulse))
            pygame.draw.polygon(surf, star_col, [
                (r.centerx, r.y + 10),
                (r.centerx + 8, r.y + 28),
                (r.centerx + 24, r.y + 28),
                (r.centerx + 12, r.y + 38),
                (r.centerx + 18, r.y + 55),
                (r.centerx,     r.y + 45),
                (r.centerx - 18, r.y + 55),
                (r.centerx - 12, r.y + 38),
                (r.centerx - 24, r.y + 28),
                (r.centerx - 8, r.y + 28),
            ])
        else:
            # Lock icon
            lc = r.centerx
            ly = r.centery + 5
            pygame.draw.rect(surf, C_COIN, pygame.Rect(lc-8, ly-2, 16, 14), border_radius=3)
            pygame.draw.arc(surf, C_COIN, pygame.Rect(lc-7, ly-12, 14, 14), 0, math.pi, 3)
        # Label
        label = font_small.render("EXIT" if self.open else "LOCKED", True, C_WHITE)
        surf.blit(label, (r.centerx - label.get_width()//2, r.bottom + 4))


class Player:
    W, H = 36, 40
    def __init__(self, cx, cy):
        self.rect = pygame.Rect(cx * TILE, cy * TILE - self.H, self.W, self.H)
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.on_ground = False
        self.jumps_left = 2
        self.facing = 1
        self.anim = 0
        self.grabbed_box = None   # reference to grabbed Box
        self.alive = True
        self.spawn = (cx * TILE, cy * TILE - self.H)

    def handle_input(self, keys, boxes):
        speed = 4.5
        self.vel_x = 0
        if keys[pygame.K_LEFT]:
            self.vel_x = -speed
            self.facing = -1
        if keys[pygame.K_RIGHT]:
            self.vel_x = speed
            self.facing = 1

        # Grab / release
        if keys[pygame.K_e]:
            if self.grabbed_box is None:
                # Try to grab nearest box
                for box in boxes:
                    if abs(box.rect.centerx - self.rect.centerx) < 60 and \
                       abs(box.rect.centery - self.rect.centery) < 80:
                        self.grabbed_box = box
                        box.grabbed = True
                        break
        else:
            if self.grabbed_box:
                self.grabbed_box.grabbed = False
                self.grabbed_box = None

    def jump(self):
        if self.jumps_left > 0:
            self.vel_y = JUMP_POWER * (1.0 if self.jumps_left == 2 else 0.82)
            self.jumps_left -= 1

    def update(self, tiles, boxes):
        # Gravity
        self.vel_y = min(self.vel_y + GRAVITY, MAX_FALL)
        self.rect.x += int(self.vel_x)
        self._collide_x(tiles)

        self.rect.y += int(self.vel_y)
        self.on_ground = False
        self._collide_y(tiles)

        # Box interactions (can stand on box)
        for box in boxes:
            if box is self.grabbed_box:
                continue
            if self.rect.colliderect(box.rect):
                if self.vel_y > 0 and self.rect.bottom - int(self.vel_y) <= box.rect.top + 8:
                    self.rect.bottom = box.rect.top
                    self.vel_y = 0
                    self.on_ground = True

        if self.on_ground:
            self.jumps_left = 2

        # Move grabbed box
        if self.grabbed_box:
            bx = self.grabbed_box
            bx.rect.centerx = self.rect.centerx + self.facing * 38
            bx.rect.bottom   = self.rect.bottom

        # Anim
        if abs(self.vel_x) > 0.5:
            self.anim += 1
        # Fall death
        if self.rect.top > SCREEN_H + 100:
            self.alive = False

    def _collide_x(self, tiles):
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.vel_x > 0:
                    self.rect.right = tile.rect.left
                elif self.vel_x < 0:
                    self.rect.left = tile.rect.right

    def _collide_y(self, tiles):
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.vel_y > 0:
                    self.rect.bottom = tile.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = tile.rect.bottom
                    self.vel_y = 0

    def draw(self, surf, offset_x):
        sx = self.rect.x - offset_x
        draw_penguin(surf, sx, self.rect.y, self.facing,
                     self.anim, self.grabbed_box is not None)


# ── HUD ────────────────────────────────────────────────────────────────────────
def draw_hud(surf, level_name, coins_left, total_coins, level_idx, total_levels):
    # Top bar
    bar = pygame.Surface((SCREEN_W, 44), pygame.SRCALPHA)
    bar.fill((0, 0, 0, 110))
    surf.blit(bar, (0, 0))

    # Coin count
    pygame.draw.circle(surf, C_COIN, (30, 22), 12)
    pygame.draw.circle(surf, C_COIN_IN, (30, 22), 8)
    collected = total_coins - coins_left
    txt = font_med.render(f"{collected}/{total_coins}", True, C_COIN)
    surf.blit(txt, (50, 8))

    # Level name + index
    lname = font_med.render(f"Level {level_idx+1}: {level_name}", True, C_WHITE)
    surf.blit(lname, (SCREEN_W//2 - lname.get_width()//2, 8))

    # Controls hint (bottom)
    hint = font_small.render("← → Move   SPACE Jump   E Grab/Drop   R Restart", True, (220,220,220))
    hbar = pygame.Surface((hint.get_width()+20, 28), pygame.SRCALPHA)
    hbar.fill((0,0,0,90))
    surf.blit(hbar, (SCREEN_W//2 - hint.get_width()//2 - 10, SCREEN_H - 30))
    surf.blit(hint, (SCREEN_W//2 - hint.get_width()//2, SCREEN_H - 26))


# ── Particle system ────────────────────────────────────────────────────────────
class Particle:
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        self.vx = (pygame.time.get_ticks() % 7 - 3) * 0.8
        self.vy = -(2 + (pygame.time.get_ticks() % 4))
        self.color = color
        self.life = 40

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.18
        self.life -= 1

    def draw(self, surf, offset_x):
        if self.life > 0:
            alpha = int(255 * self.life / 40)
            s = pygame.Surface((8, 8), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (4,4), 4)
            surf.blit(s, (int(self.x - offset_x), int(self.y)))


particles = []

def spawn_coin_particles(x, y):
    for _ in range(8):
        particles.append(Particle(x, y, C_COIN))

def update_particles(offset_x):
    for p in particles[:]:
        p.update()
        p.draw(screen, offset_x)
        if p.life <= 0:
            particles.remove(p)


# ── Screen overlays ────────────────────────────────────────────────────────────
def show_message(surf, title, subtitle, color=(255,255,100)):
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    surf.blit(overlay, (0,0))
    draw_text_shadow(surf, title,    font_big,  color,
                     SCREEN_W//2 - font_big.size(title)[0]//2,
                     SCREEN_H//2 - 60)
    draw_text_shadow(surf, subtitle, font_med, C_WHITE,
                     SCREEN_W//2 - font_med.size(subtitle)[0]//2,
                     SCREEN_H//2 + 10)


def show_win_screen(surf):
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0,0,60,180))
    surf.blit(overlay, (0,0))
    # Stars
    import random
    random.seed(42)
    for _ in range(80):
        sx = random.randint(0, SCREEN_W)
        sy = random.randint(0, SCREEN_H)
        r  = random.randint(1,3)
        pygame.draw.circle(surf, C_STAR, (sx,sy), r)
    msg  = "🎉 YOU WIN! 🎉"
    msg2 = "All levels complete! Press R to play again or Q to quit."
    draw_text_shadow(surf, "YOU WIN!", font_big, (255,220,50),
                     SCREEN_W//2 - font_big.size("YOU WIN!")[0]//2,
                     SCREEN_H//2 - 80, offset=3)
    draw_text_shadow(surf, "All levels complete!",  font_med, C_WHITE,
                     SCREEN_W//2 - font_med.size("All levels complete!")[0]//2,
                     SCREEN_H//2)
    draw_text_shadow(surf, "Press R to restart  |  Q to quit", font_small, (200,200,200),
                     SCREEN_W//2 - font_small.size("Press R to restart  |  Q to quit")[0]//2,
                     SCREEN_H//2 + 50)


# ── Level loader ───────────────────────────────────────────────────────────────
def load_level(idx):
    data    = LEVELS[idx]
    tiles   = [Tile(k, c, r) for (k,c,r) in data["tiles"]]
    coins   = [Coin(cx, cy)  for (cx,cy)  in data["coins"]]
    boxes   = [Box(cx, cy)   for (cx, cy) in data["boxes"]]
    door    = Door(*data["door"])
    sp      = data["spawn"]
    player  = Player(*sp)
    particles.clear()
    return tiles, coins, boxes, door, player, data["name"]


# ── Main game loop ─────────────────────────────────────────────────────────────
def main():
    level_idx   = 0
    tiles, coins, boxes, door, player, level_name = load_level(level_idx)

    state       = "play"   # "play" | "dead" | "win_level" | "win_game"
    death_timer = 0
    win_timer   = 0
    scroll_x    = 0

    running = True
    while running:
        dt = clock.tick(FPS)

        # ── Events ──────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
                if event.key == pygame.K_r:
                    level_idx = 0
                    tiles, coins, boxes, door, player, level_name = load_level(level_idx)
                    state = "play"
                if event.key in (pygame.K_SPACE, pygame.K_UP):
                    if state == "play":
                        player.jump()

        keys = pygame.key.get_pressed()

        # ── Update ──────────────────────────────────────────────────────────
        if state == "play":
            player.handle_input(keys, boxes)
            player.update(tiles, boxes)
            for box in boxes:
                box.apply_gravity(tiles)
            for coin in coins:
                coin.update()

            # Coin collection
            for coin in coins:
                if not coin.collected and player.rect.colliderect(coin.get_rect()):
                    coin.collected = True
                    spawn_coin_particles(coin.x, coin.y)

            # Door logic
            coins_left = sum(1 for c in coins if not c.collected)
            door.open = (coins_left == 0)

            if door.open and player.rect.colliderect(door.rect):
                state = "win_level"
                win_timer = 90

            if not player.alive:
                state = "dead"
                death_timer = 90

        elif state == "dead":
            death_timer -= 1
            if death_timer <= 0:
                # Respawn
                sp = LEVELS[level_idx]["spawn"]
                player = Player(*sp)
                state = "play"

        elif state == "win_level":
            win_timer -= 1
            if win_timer <= 0:
                level_idx += 1
                if level_idx >= len(LEVELS):
                    state = "win_game"
                else:
                    tiles, coins, boxes, door, player, level_name = load_level(level_idx)
                    state = "play"

        # Scroll camera
        target_x = player.rect.centerx - SCREEN_W // 2
        scroll_x += (target_x - scroll_x) * 0.12
        scroll_x  = max(0, scroll_x)

        # ── Draw ────────────────────────────────────────────────────────────
        draw_background(scroll_x)

        for tile in tiles:
            tile.draw(screen, scroll_x)
        for box in boxes:
            box.draw(screen, scroll_x)
        door.draw(screen, scroll_x)
        for coin in coins:
            coin.draw(screen, scroll_x)

        update_particles(scroll_x)
        player.draw(screen, scroll_x)

        coins_left = sum(1 for c in coins if not c.collected)
        draw_hud(screen, level_name, coins_left, len(coins), level_idx, len(LEVELS))

        if state == "dead":
            show_message(screen, "OOPS!", "Respawning…", (255,100,100))
        elif state == "win_level" and level_idx < len(LEVELS):
            show_message(screen, "LEVEL CLEAR!", "Get ready…", (100,255,150))
        elif state == "win_game":
            show_win_screen(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()