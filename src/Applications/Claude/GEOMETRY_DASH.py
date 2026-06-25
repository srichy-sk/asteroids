import pygame
import sys
import random
import math

# ── Init ──────────────────────────────────────────────────────────────────────
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 900, 500
FPS = 60
GROUND_Y = 400

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Geometry Dash")
clock = pygame.time.Clock()

# ── Palette ───────────────────────────────────────────────────────────────────
BG_TOP    = (10, 5, 30)
BG_BOT    = (25, 10, 60)
GROUND_C  = (40, 20, 80)
GRID_C    = (50, 30, 100)
PLAYER_C  = (0, 220, 255)
PLAYER_HL = (150, 240, 255)
SPIKE_C   = (255, 60, 100)
BLOCK_C   = (80, 60, 200)
BLOCK_HL  = (120, 100, 255)
COIN_C    = (255, 210, 50)
PORTAL_C1 = (0, 255, 180)
PORTAL_C2 = (255, 100, 0)
TEXT_C    = (255, 255, 255)
SHADOW_C  = (0, 0, 0, 120)
STAR_C    = (255, 255, 255)

# ── Fonts ─────────────────────────────────────────────────────────────────────
try:
    font_big   = pygame.font.SysFont("consolas", 48, bold=True)
    font_med   = pygame.font.SysFont("consolas", 28, bold=True)
    font_small = pygame.font.SysFont("consolas", 18)
except:
    font_big   = pygame.font.Font(None, 52)
    font_med   = pygame.font.Font(None, 32)
    font_small = pygame.font.Font(None, 20)

# ── Helpers ───────────────────────────────────────────────────────────────────

def lerp_color(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))

def draw_gradient_rect(surf, rect, top_col, bot_col):
    for i in range(rect.height):
        t = i / max(rect.height - 1, 1)
        pygame.draw.line(surf, lerp_color(top_col, bot_col, t),
                         (rect.x, rect.y + i), (rect.right, rect.y + i))

# ── Stars ─────────────────────────────────────────────────────────────────────
stars = [(random.randint(0, WIDTH), random.randint(0, GROUND_Y),
          random.uniform(0.5, 2.5), random.uniform(0.3, 1.0)) for _ in range(120)]

def draw_stars(surf, offset):
    for x, y, size, speed in stars:
        sx = int((x - offset * speed) % WIDTH)
        alpha = random.randint(160, 255)
        c = (255, 255, 255)
        pygame.draw.circle(surf, c, (sx, y), int(size))

# ── Particle system ───────────────────────────────────────────────────────────
particles = []

def emit_particles(x, y, count=8, color=PLAYER_C):
    for _ in range(count):
        angle = random.uniform(0, math.tau)
        speed = random.uniform(2, 6)
        particles.append({
            "x": x, "y": y,
            "vx": math.cos(angle) * speed,
            "vy": math.sin(angle) * speed - 2,
            "life": random.randint(15, 30),
            "color": color,
            "size": random.randint(2, 5),
        })

def update_draw_particles(surf):
    for p in particles[:]:
        p["x"] += p["vx"]
        p["y"] += p["vy"]
        p["vy"] += 0.3
        p["life"] -= 1
        if p["life"] <= 0:
            particles.remove(p)
            continue
        alpha_frac = p["life"] / 30
        r, g, b = p["color"]
        col = (min(255, r), min(255, g), min(255, b))
        pygame.draw.circle(surf, col, (int(p["x"]), int(p["y"])), p["size"])

# ── Level generator ───────────────────────────────────────────────────────────
TILE = 50

def generate_level(length=120):
    """Returns list of obstacle dicts."""
    obs = []
    x = 20  # tiles from start
    while x < length:
        kind = random.choices(["gap", "spike", "block", "double_spike", "tall_block"],
                              weights=[2, 4, 3, 2, 1])[0]
        if kind == "spike":
            obs.append({"type": "spike", "tx": x, "h": 1})
            x += random.randint(4, 8)
        elif kind == "double_spike":
            obs.append({"type": "spike", "tx": x, "h": 1})
            obs.append({"type": "spike", "tx": x + 1, "h": 1})
            x += random.randint(5, 9)
        elif kind == "block":
            obs.append({"type": "block", "tx": x, "h": 1})
            x += random.randint(4, 8)
        elif kind == "tall_block":
            obs.append({"type": "block", "tx": x, "h": 2})
            x += random.randint(5, 10)
        else:
            x += random.randint(3, 6)
    # End portal
    obs.append({"type": "portal", "tx": x + 2})
    return obs, x + 6

def build_rects(obs):
    """Convert tile obstacles to pixel rects for collision."""
    rects = []
    for o in obs:
        px = o["tx"] * TILE
        if o["type"] == "spike":
            # Triangle – use bounding rect for collision approx
            h = TILE
            rects.append({"type": "spike", "rect": pygame.Rect(px + 5, GROUND_Y - h, TILE - 10, h), "raw": o})
        elif o["type"] == "block":
            h = o["h"] * TILE
            rects.append({"type": "block", "rect": pygame.Rect(px, GROUND_Y - h, TILE, h), "raw": o})
        elif o["type"] == "portal":
            rects.append({"type": "portal", "rect": pygame.Rect(px, GROUND_Y - TILE * 3, TILE // 2, TILE * 3), "raw": o})
    return rects

# ── Drawing obstacles ──────────────────────────────────────────────────────────

def draw_spike(surf, px, cam_x):
    sx = px - cam_x
    pts = [(sx, GROUND_Y), (sx + TILE, GROUND_Y), (sx + TILE // 2, GROUND_Y - TILE)]
    pygame.draw.polygon(surf, SPIKE_C, pts)
    pygame.draw.polygon(surf, (255, 150, 170), pts, 2)

def draw_block(surf, px, h, cam_x):
    sx = px - cam_x
    ph = h * TILE
    rect = pygame.Rect(sx, GROUND_Y - ph, TILE, ph)
    draw_gradient_rect(surf, rect, BLOCK_HL, BLOCK_C)
    pygame.draw.rect(surf, (100, 80, 220), rect, 2)
    # Shine
    pygame.draw.line(surf, (200, 180, 255), (rect.x + 4, rect.y + 4), (rect.right - 4, rect.y + 4), 2)

def draw_portal(surf, px, cam_x, tick):
    sx = px - cam_x
    w, ph = TILE // 2, TILE * 3
    r = pygame.Rect(sx, GROUND_Y - ph, w, ph)
    t = (math.sin(tick * 0.08) + 1) / 2
    col = lerp_color(PORTAL_C1, PORTAL_C2, t)
    draw_gradient_rect(surf, r, col, (255, 255, 255))
    pygame.draw.rect(surf, (255, 255, 255), r, 2)
    # Glow rings
    for i in range(3):
        a = tick * 0.05 + i * math.pi * 2 / 3
        cx = sx + w // 2 + int(math.cos(a) * 8)
        cy = GROUND_Y - ph // 2 + int(math.sin(a) * 20)
        pygame.draw.circle(surf, (255, 255, 255), (cx, cy), 4)

# ── Player ────────────────────────────────────────────────────────────────────
GRAVITY   = 0.7
JUMP_VEL  = -14
PLAYER_W  = 38
PLAYER_H  = 38

class Player:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = 150
        self.y = float(GROUND_Y - PLAYER_H)
        self.vy = 0
        self.on_ground = False
        self.angle = 0
        self.dead = False
        self.trail = []

    def jump(self):
        if self.on_ground:
            self.vy = JUMP_VEL
            self.on_ground = False
            emit_particles(self.x + PLAYER_W // 2, self.y + PLAYER_H, 6)

    def update(self, obstacle_rects):
        if self.dead:
            return

        self.vy += GRAVITY
        self.y += self.vy

        # Ground collision
        if self.y >= GROUND_Y - PLAYER_H:
            self.y = GROUND_Y - PLAYER_H
            self.vy = 0
            self.on_ground = True
        else:
            self.on_ground = False

        # Block top-collision
        pr = pygame.Rect(self.x, int(self.y), PLAYER_W, PLAYER_H)
        for o in obstacle_rects:
            if o["type"] != "block":
                continue
            br = o["rect"]
            # Shift rect to world coords (already world)
            if pr.colliderect(br):
                # Landing on top
                if self.vy > 0 and pr.bottom - self.vy <= br.top + 5:
                    self.y = br.top - PLAYER_H
                    self.vy = 0
                    self.on_ground = True
                else:
                    self.dead = True
                    emit_particles(self.x + PLAYER_W // 2, int(self.y) + PLAYER_H // 2, 20)
                    return

        # Spike / death collision
        for o in obstacle_rects:
            if o["type"] == "spike":
                # Tighter hitbox
                tight = pygame.Rect(o["rect"].x + 8, o["rect"].y + 10,
                                    o["rect"].width - 16, o["rect"].height - 10)
                if pr.colliderect(tight):
                    self.dead = True
                    emit_particles(self.x + PLAYER_W // 2, int(self.y) + PLAYER_H // 2, 20, SPIKE_C)
                    return

        # Angle spin when airborne
        if not self.on_ground:
            self.angle = (self.angle + 5) % 360
        else:
            # Snap to nearest 90°
            snapped = round(self.angle / 90) * 90
            self.angle = snapped % 360

        # Trail
        self.trail.append((self.x + PLAYER_W // 2, int(self.y) + PLAYER_H // 2))
        if len(self.trail) > 12:
            self.trail.pop(0)

    def check_portal(self, obstacle_rects):
        pr = pygame.Rect(self.x, int(self.y), PLAYER_W, PLAYER_H)
        for o in obstacle_rects:
            if o["type"] == "portal" and pr.colliderect(o["rect"]):
                return True
        return False

    def draw(self, surf, cam_x):
        sx = self.x - cam_x
        sy = int(self.y)
        # Trail
        for i, (tx, ty) in enumerate(self.trail):
            alpha = int(200 * i / len(self.trail))
            r, g, b = PLAYER_C
            col = (r, g, b)
            size = max(2, int(6 * i / len(self.trail)))
            pygame.draw.circle(surf, col, (tx - cam_x, ty), size)

        # Rotated cube
        cx, cy = sx + PLAYER_W // 2, sy + PLAYER_H // 2
        hw, hh = PLAYER_W // 2, PLAYER_H // 2
        angle_r = math.radians(self.angle)
        corners = [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]
        rotated = []
        for dx, dy in corners:
            rx = dx * math.cos(angle_r) - dy * math.sin(angle_r)
            ry = dx * math.sin(angle_r) + dy * math.cos(angle_r)
            rotated.append((cx + rx, cy + ry))

        pygame.draw.polygon(surf, PLAYER_C, rotated)
        pygame.draw.polygon(surf, PLAYER_HL, rotated, 3)

        # Inner X detail
        p = rotated
        pygame.draw.line(surf, PLAYER_HL,
                         ((p[0][0] + p[2][0]) / 2, (p[0][1] + p[2][1]) / 2),
                         ((p[1][0] + p[3][0]) / 2, (p[1][1] + p[3][1]) / 2), 2)
        pygame.draw.line(surf, PLAYER_HL,
                         ((p[0][0] + p[1][0]) / 2, (p[0][1] + p[1][1]) / 2),
                         ((p[2][0] + p[3][0]) / 2, (p[2][1] + p[3][1]) / 2), 2)


# ── Background ────────────────────────────────────────────────────────────────

def draw_background(surf, cam_x, tick):
    draw_gradient_rect(surf, pygame.Rect(0, 0, WIDTH, GROUND_Y), BG_TOP, BG_BOT)
    draw_stars(surf, cam_x)

def draw_ground(surf, cam_x):
    # Ground fill
    pygame.draw.rect(surf, GROUND_C, (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
    # Grid lines
    offset = int(cam_x) % TILE
    for gx in range(-offset, WIDTH + TILE, TILE):
        pygame.draw.line(surf, GRID_C, (gx, GROUND_Y), (gx, HEIGHT), 1)
    for gy in range(GROUND_Y, HEIGHT, TILE):
        pygame.draw.line(surf, GRID_C, (0, gy), (WIDTH, gy), 1)
    # Ground border
    pygame.draw.rect(surf, (100, 60, 200), (0, GROUND_Y, WIDTH, 3))


# ── HUD ───────────────────────────────────────────────────────────────────────

def draw_hud(surf, progress, attempts, best):
    # Progress bar
    bar_w = WIDTH - 40
    pygame.draw.rect(surf, (40, 40, 80), (20, 14, bar_w, 14), border_radius=7)
    fill = int(bar_w * max(0, min(1, progress)))
    if fill > 0:
        pygame.draw.rect(surf, PLAYER_C, (20, 14, fill, 14), border_radius=7)
    pygame.draw.rect(surf, (100, 80, 200), (20, 14, bar_w, 14), 2, border_radius=7)
    pct = int(progress * 100)
    label = font_small.render(f"{pct}%", True, TEXT_C)
    surf.blit(label, (WIDTH // 2 - label.get_width() // 2, 10))

    # Attempt counter
    atxt = font_small.render(f"Attempt {attempts}", True, (180, 160, 255))
    surf.blit(atxt, (20, 38))
    btxt = font_small.render(f"Best {best}%", True, (200, 200, 100))
    surf.blit(btxt, (WIDTH - btxt.get_width() - 20, 38))

    # Controls hint (first 3 secs handled externally)


# ── Screens ───────────────────────────────────────────────────────────────────

def draw_overlay(surf, title, subtitle, color=(0, 220, 255)):
    s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    s.fill((0, 0, 0, 160))
    surf.blit(s, (0, 0))
    t = font_big.render(title, True, color)
    surf.blit(t, (WIDTH // 2 - t.get_width() // 2, HEIGHT // 2 - 60))
    s2 = font_med.render(subtitle, True, TEXT_C)
    surf.blit(s2, (WIDTH // 2 - s2.get_width() // 2, HEIGHT // 2 + 10))

# ── Game states ───────────────────────────────────────────────────────────────
STATE_MENU   = "menu"
STATE_PLAY   = "play"
STATE_DEAD   = "dead"
STATE_WIN    = "win"

def main():
    state = STATE_MENU
    seed = random.randint(0, 99999)
    random.seed(seed)
    obs_raw, level_len = generate_level(length=100)
    obs_rects = build_rects(obs_raw)

    player = Player()
    cam_x = 0.0
    CAM_SPEED_BASE = 5.0
    cam_speed = CAM_SPEED_BASE

    attempts = 1
    best = 0
    tick = 0

    dead_timer = 0
    win_timer  = 0

    hint_timer = 180  # frames to show hint

    while True:
        dt = clock.tick(FPS)
        tick += 1

        # ── Events ────────────────────────────────────────────────────────────
        jump_pressed = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                    if state == STATE_PLAY:
                        jump_pressed = True
                    elif state in (STATE_MENU, STATE_DEAD, STATE_WIN):
                        # Restart
                        random.seed(seed + attempts)
                        obs_raw, level_len = generate_level(length=100)
                        obs_rects = build_rects(obs_raw)
                        player.reset()
                        cam_x = 0.0
                        particles.clear()
                        if state == STATE_WIN:
                            seed = random.randint(0, 99999)
                            attempts = 1
                            best = 0
                        else:
                            attempts += 1
                        state = STATE_PLAY
                if event.key == pygame.K_r:
                    # Full reset
                    seed = random.randint(0, 99999)
                    random.seed(seed)
                    obs_raw, level_len = generate_level(length=100)
                    obs_rects = build_rects(obs_raw)
                    player.reset()
                    cam_x = 0.0
                    particles.clear()
                    attempts = 1
                    best = 0
                    state = STATE_PLAY
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

        # Mouse / touch
        if pygame.mouse.get_pressed()[0]:
            if state == STATE_PLAY:
                jump_pressed = True

        # ── Update ────────────────────────────────────────────────────────────
        if state == STATE_PLAY:
            if jump_pressed:
                player.jump()

            # Shift obstacle rects to follow world coords (they stay world-space; we shift cam)
            # Pass world-space rects with cam offset applied for collision
            world_rects = []
            for o in obs_rects:
                shifted_rect = o["rect"].move(-int(cam_x), 0)
                world_rects.append({"type": o["type"], "rect": shifted_rect, "raw": o.get("raw")})

            player.update(world_rects)

            # Scroll camera to follow player (locked x advance)
            cam_x += cam_speed
            player.x = 150  # player stays fixed on screen, world scrolls

            progress = cam_x / (level_len * TILE)
            best = max(best, int(progress * 100))

            if player.dead:
                state = STATE_DEAD
                dead_timer = 90

            if player.check_portal(world_rects):
                state = STATE_WIN
                win_timer = 150
                emit_particles(player.x + PLAYER_W // 2,
                               int(player.y) + PLAYER_H // 2, 40, PORTAL_C1)

        elif state == STATE_DEAD:
            dead_timer -= 1

        elif state == STATE_WIN:
            win_timer -= 1

        elif state == STATE_MENU:
            # Animate background only
            cam_x += 1.5

        if hint_timer > 0:
            hint_timer -= 1

        # ── Draw ──────────────────────────────────────────────────────────────
        draw_background(screen, cam_x, tick)
        draw_ground(screen, cam_x)

        # Draw obstacles
        for o in obs_raw:
            px = o["tx"] * TILE - int(cam_x)
            if -TILE < px < WIDTH + TILE:
                if o["type"] == "spike":
                    draw_spike(screen, o["tx"] * TILE, int(cam_x))
                elif o["type"] == "block":
                    draw_block(screen, o["tx"] * TILE, o["h"], int(cam_x))
                elif o["type"] == "portal":
                    draw_portal(screen, o["tx"] * TILE, int(cam_x), tick)

        update_draw_particles(screen)

        if state != STATE_MENU:
            player.draw(screen, 0 if state == STATE_MENU else 0)
            # player x is already screen-space (150)
            # Re-draw using screen x
            sx = player.x
            sy = int(player.y)
            # (Player.draw handles it)

        if state == STATE_PLAY or state == STATE_DEAD or state == STATE_WIN:
            progress = cam_x / (level_len * TILE)
            draw_hud(screen, progress, attempts, best)

        if hint_timer > 0 and state == STATE_PLAY:
            hint = font_small.render("SPACE / CLICK to jump  |  R to restart  |  ESC to quit", True, (160, 140, 220))
            screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 30))

        if state == STATE_MENU:
            draw_overlay(screen, "GEOMETRY DASH", "Press SPACE to start", PLAYER_C)

        if state == STATE_DEAD:
            draw_overlay(screen, "YOU DIED", "Press SPACE to retry", SPIKE_C)

        if state == STATE_WIN:
            draw_overlay(screen, "LEVEL COMPLETE!", "Press SPACE for new level", PORTAL_C1)
            # Celebration particles
            if tick % 3 == 0:
                emit_particles(random.randint(0, WIDTH),
                               random.randint(0, HEIGHT),
                               4, random.choice([PORTAL_C1, COIN_C, PLAYER_C]))

        pygame.display.flip()

if __name__ == "__main__":
    main()