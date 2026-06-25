import pygame
import math
import random
import sys

pygame.init()

WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Zombie Shooter")

clock = pygame.time.Clock()

# ── Colors ──────────────────────────────────────────────────────────────────
BG_COLOR       = (15, 20, 10)
GRID_COLOR     = (25, 35, 18)
PLAYER_COLOR   = (80, 200, 120)
PLAYER_OUTLINE = (140, 255, 160)
BULLET_COLOR   = (255, 230, 80)
ZOMBIE_COLOR   = (160, 60, 30)
ZOMBIE_OUTLINE = (220, 90, 40)
BLOOD_COLOR    = (180, 20, 20)
UI_BG          = (10, 14, 8)
HP_COLOR       = (60, 220, 80)
HP_LOW_COLOR   = (220, 60, 40)
TEXT_COLOR     = (200, 240, 180)
TITLE_COLOR    = (100, 255, 120)
FLASH_COLOR    = (255, 80, 40)

# ── Fonts ────────────────────────────────────────────────────────────────────
font_big   = pygame.font.SysFont("Consolas", 52, bold=True)
font_med   = pygame.font.SysFont("Consolas", 28, bold=True)
font_small = pygame.font.SysFont("Consolas", 20)

# ── Particle system ──────────────────────────────────────────────────────────
particles = []

def spawn_particles(x, y, color, count=12, speed=4):
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        spd   = random.uniform(1, speed)
        particles.append({
            "x": x, "y": y,
            "vx": math.cos(angle) * spd,
            "vy": math.sin(angle) * spd,
            "life": random.randint(15, 35),
            "color": color,
            "size": random.randint(2, 5),
        })

def update_draw_particles(surface):
    for p in particles[:]:
        p["x"] += p["vx"]
        p["y"] += p["vy"]
        p["life"] -= 1
        alpha = max(0, p["life"] / 35)
        r = int(p["color"][0] * alpha)
        g = int(p["color"][1] * alpha)
        b = int(p["color"][2] * alpha)
        if p["size"] >= 2:
            pygame.draw.circle(surface, (r, g, b),
                               (int(p["x"]), int(p["y"])), p["size"])
        if p["life"] <= 0:
            particles.remove(p)

# ── Player ───────────────────────────────────────────────────────────────────
class Player:
    RADIUS   = 18
    SPEED    = 4
    MAX_HP   = 5
    SHOOT_CD = 15          # frames between shots

    def __init__(self):
        self.x = WIDTH  // 2
        self.y = HEIGHT // 2
        self.hp        = self.MAX_HP
        self.shoot_cd  = 0
        self.flash     = 0            # hurt flash timer

    def move(self, keys):
        dx = dy = 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:    dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += 1
        if dx and dy:
            dx *= 0.7071; dy *= 0.7071
        self.x = max(self.RADIUS, min(WIDTH  - self.RADIUS, self.x + dx * self.SPEED))
        self.y = max(self.RADIUS, min(HEIGHT - self.RADIUS, self.y + dy * self.SPEED))

    def try_shoot(self, mx, my, bullets):
        if self.shoot_cd > 0:
            return
        angle = math.atan2(my - self.y, mx - self.x)
        bullets.append(Bullet(self.x, self.y, angle))
        self.shoot_cd = self.SHOOT_CD

    def update(self):
        if self.shoot_cd > 0: self.shoot_cd -= 1
        if self.flash  > 0: self.flash   -= 1

    def take_damage(self):
        self.hp    -= 1
        self.flash  = 12
        spawn_particles(self.x, self.y, FLASH_COLOR, 10, 5)

    def draw(self, surface):
        # hurt flash overlay
        col = FLASH_COLOR if self.flash > 0 else PLAYER_COLOR
        out = PLAYER_OUTLINE if self.flash == 0 else (255, 200, 180)
        pygame.draw.circle(surface, col, (int(self.x), int(self.y)), self.RADIUS)
        pygame.draw.circle(surface, out, (int(self.x), int(self.y)), self.RADIUS, 3)
        # direction dot
        mx, my = pygame.mouse.get_pos()
        angle  = math.atan2(my - self.y, mx - self.x)
        ex = self.x + math.cos(angle) * (self.RADIUS - 4)
        ey = self.y + math.sin(angle) * (self.RADIUS - 4)
        pygame.draw.circle(surface, out, (int(ex), int(ey)), 4)

# ── Bullet ───────────────────────────────────────────────────────────────────
class Bullet:
    RADIUS = 5
    SPEED  = 11

    def __init__(self, x, y, angle):
        self.x     = x
        self.y     = y
        self.vx    = math.cos(angle) * self.SPEED
        self.vy    = math.sin(angle) * self.SPEED
        self.alive = True

    def update(self):
        self.x += self.vx
        self.y += self.vy
        if not (0 < self.x < WIDTH and 0 < self.y < HEIGHT):
            self.alive = False

    def draw(self, surface):
        # glow trail
        pygame.draw.circle(surface, (180, 140, 20),
                           (int(self.x), int(self.y)), self.RADIUS + 3)
        pygame.draw.circle(surface, BULLET_COLOR,
                           (int(self.x), int(self.y)), self.RADIUS)

# ── Zombie ───────────────────────────────────────────────────────────────────
class Zombie:
    RADIUS = 20
    HP     = 2             # takes 2 hits to kill

    def __init__(self, wave):
        edge = random.choice(["top", "bottom", "left", "right"])
        if edge == "top":
            self.x, self.y = random.uniform(0, WIDTH), -self.RADIUS
        elif edge == "bottom":
            self.x, self.y = random.uniform(0, WIDTH), HEIGHT + self.RADIUS
        elif edge == "left":
            self.x, self.y = -self.RADIUS, random.uniform(0, HEIGHT)
        else:
            self.x, self.y = WIDTH + self.RADIUS, random.uniform(0, HEIGHT)
        self.speed = random.uniform(1.2, 1.6 + wave * 0.12)
        self.hp    = self.HP
        self.alive = True
        self.stagger = 0

    def update(self, px, py):
        if self.stagger > 0:
            self.stagger -= 1
            return
        angle = math.atan2(py - self.y, px - self.x)
        self.x += math.cos(angle) * self.speed
        self.y += math.sin(angle) * self.speed

    def hit(self):
        self.hp     -= 1
        self.stagger = 6
        if self.hp <= 0:
            self.alive = False
            spawn_particles(self.x, self.y, BLOOD_COLOR, 18, 6)
        else:
            spawn_particles(self.x, self.y, ZOMBIE_OUTLINE, 8, 3)

    def draw(self, surface):
        shade = ZOMBIE_COLOR if self.hp == self.HP else (200, 80, 40)
        pygame.draw.circle(surface, shade,
                           (int(self.x), int(self.y)), self.RADIUS)
        pygame.draw.circle(surface, ZOMBIE_OUTLINE,
                           (int(self.x), int(self.y)), self.RADIUS, 3)
        # X eyes
        ex, ey = int(self.x), int(self.y) - 4
        for ox in (-6, 6):
            pygame.draw.line(surface, (240, 220, 180),
                             (ex + ox - 3, ey - 3), (ex + ox + 3, ey + 3), 2)
            pygame.draw.line(surface, (240, 220, 180),
                             (ex + ox + 3, ey - 3), (ex + ox - 3, ey + 3), 2)

# ── HUD helpers ──────────────────────────────────────────────────────────────
def draw_hud(surface, player, score, wave, kills_left):
    # bottom bar
    pygame.draw.rect(surface, UI_BG, (0, HEIGHT - 48, WIDTH, 48))
    pygame.draw.line(surface, (40, 80, 30), (0, HEIGHT - 48), (WIDTH, HEIGHT - 48), 2)

    # HP hearts
    for i in range(Player.MAX_HP):
        col = (HP_COLOR if i < player.hp else (50, 50, 50))
        pygame.draw.circle(surface, col, (26 + i * 36, HEIGHT - 24), 12)
        pygame.draw.circle(surface, (0, 0, 0), (26 + i * 36, HEIGHT - 24), 12, 2)

    # Score
    s = font_small.render(f"SCORE  {score:05d}", True, TEXT_COLOR)
    surface.blit(s, (WIDTH // 2 - s.get_width() // 2, HEIGHT - 40))

    # Wave & kills
    w = font_small.render(f"WAVE {wave}   ZOMBIES {kills_left}", True, TEXT_COLOR)
    surface.blit(w, (WIDTH - w.get_width() - 16, HEIGHT - 40))

def draw_grid(surface):
    for x in range(0, WIDTH, 50):
        pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, HEIGHT - 48))
    for y in range(0, HEIGHT - 48, 50):
        pygame.draw.line(surface, GRID_COLOR, (0, y), (WIDTH, y))

def draw_overlay(surface, title, subtitle):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    surface.blit(overlay, (0, 0))
    t = font_big.render(title, True, TITLE_COLOR)
    s = font_med.render(subtitle, True, TEXT_COLOR)
    surface.blit(t, (WIDTH // 2 - t.get_width() // 2, HEIGHT // 2 - 70))
    surface.blit(s, (WIDTH // 2 - s.get_width() // 2, HEIGHT // 2 + 10))

# ── Wave config ──────────────────────────────────────────────────────────────
def zombies_for_wave(wave):
    return 6 + (wave - 1) * 4

# ── Main game loop ────────────────────────────────────────────────────────────
def main():
    state         = "title"   # title | playing | dead | wave_clear
    player        = Player()
    bullets: list[Bullet] = []
    zombies: list[Zombie] = []
    particles.clear()

    score         = 0
    wave          = 1
    total_wave    = zombies_for_wave(wave)
    spawned       = 0
    spawn_timer   = 0
    SPAWN_INTERVAL= 60         # frames between spawns

    while True:
        clock.tick(60)
        keys = pygame.key.get_pressed()
        mx, my = pygame.mouse.get_pos()

        # ── Events ──────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                if state in ("title", "dead", "wave_clear") and event.key == pygame.K_RETURN:
                    if state in ("title", "dead"):
                        # full reset
                        player  = Player()
                        bullets.clear()
                        zombies.clear()
                        particles.clear()
                        score   = 0
                        wave    = 1
                    else:
                        # next wave
                        wave   += 1
                        bullets.clear()
                        zombies.clear()
                        particles.clear()
                    total_wave    = zombies_for_wave(wave)
                    spawned       = 0
                    spawn_timer   = 0
                    state         = "playing"

            if event.type == pygame.MOUSEBUTTONDOWN and state == "playing":
                if event.button == 1:
                    player.try_shoot(mx, my, bullets)

        # ── Draw background ──────────────────────────────────────────────────
        screen.fill(BG_COLOR)
        draw_grid(screen)

        # ── Playing state ────────────────────────────────────────────────────
        if state == "playing":
            player.move(keys)
            player.update()

            # continuous fire while holding mouse
            if pygame.mouse.get_pressed()[0]:
                player.try_shoot(mx, my, bullets)

            # spawn zombies
            if spawned < total_wave:
                spawn_timer += 1
                if spawn_timer >= SPAWN_INTERVAL:
                    zombies.append(Zombie(wave))
                    spawned     += 1
                    spawn_timer  = 0

            # update bullets
            for b in bullets[:]:
                b.update()
                if not b.alive:
                    bullets.remove(b)

            # update zombies
            for z in zombies[:]:
                z.update(player.x, player.y)

                # bullet collision
                for b in bullets[:]:
                    dist = math.hypot(b.x - z.x, b.y - z.y)
                    if dist < z.RADIUS + b.RADIUS:
                        z.hit()
                        b.alive = False
                        if b in bullets: bullets.remove(b)
                        if not z.alive:
                            score += 10 * wave
                            zombies.remove(z)
                            break

                # player collision
                if z.alive:
                    dist = math.hypot(player.x - z.x, player.y - z.y)
                    if dist < player.RADIUS + z.RADIUS:
                        player.take_damage()
                        z.alive = False
                        zombies.remove(z)
                        if player.hp <= 0:
                            state = "dead"
                            spawn_particles(player.x, player.y,
                                            FLASH_COLOR, 30, 8)

            # wave clear?
            if spawned == total_wave and len(zombies) == 0 and state == "playing":
                state = "wave_clear"
                score += 50 * wave

            # draw
            for b in bullets:  b.draw(screen)
            for z in zombies:  z.draw(screen)
            update_draw_particles(screen)
            player.draw(screen)

            kills_left = (total_wave - spawned) + len(zombies)
            draw_hud(screen, player, score, wave, kills_left)

        # ── Overlays ─────────────────────────────────────────────────────────
        elif state == "title":
            update_draw_particles(screen)
            draw_overlay(screen,
                         "ZOMBIE  SHOOTER",
                         "WASD / Arrows = move   Mouse = aim & shoot   ENTER to start")

        elif state == "dead":
            update_draw_particles(screen)
            draw_overlay(screen,
                         "YOU  DIED",
                         f"Score: {score}   Wave: {wave}   ENTER to restart")

        elif state == "wave_clear":
            draw_overlay(screen,
                         f"WAVE  {wave}  CLEARED!",
                         f"Score: {score}   ENTER for next wave")

        pygame.display.flip()

if __name__ == "__main__":
    main()