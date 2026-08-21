"""Twenty-level coin platformer. Run with: python3 platformer.py"""

import math
import sys
import pygame

WIDTH, HEIGHT = 1000, 600
FPS = 60
GRAVITY = 0.72
PLAYER_SPEED = 5.2
JUMP_SPEED = -14.5

SKY = (112, 202, 255)
INK = (28, 39, 54)
GROUND = (70, 125, 70)
DIRT = (123, 79, 47)
GOLD = (255, 211, 62)


def rect(x, y, w, h):
    return pygame.Rect(int(x), int(y), int(w), int(h))


class Player:
    def __init__(self, x, y):
        self.box = rect(x, y, 34, 44)
        self.x, self.y = float(x), float(y)
        self.vx = self.vy = 0.0
        self.on_ground = False
        self.facing = 1
        self.lives = 3

    def respawn(self, x, y):
        self.x, self.y = float(x), float(y)
        self.vx = self.vy = 0.0
        self.box.topleft = (int(x), int(y))

    def update(self, keys, platforms):
        move = (
            int(keys[pygame.K_RIGHT] or keys[pygame.K_d])
            - int(keys[pygame.K_LEFT] or keys[pygame.K_a])
        )
        self.vx = move * PLAYER_SPEED

        if move:
            self.facing = move

        if (
            keys[pygame.K_SPACE]
            or keys[pygame.K_UP]
            or keys[pygame.K_w]
        ) and self.on_ground:
            self.vy = JUMP_SPEED
            self.on_ground = False

        self.x += self.vx
        self.box.x = round(self.x)

        for platform in platforms:
            if self.box.colliderect(platform):
                if self.vx > 0:
                    self.box.right = platform.left
                elif self.vx < 0:
                    self.box.left = platform.right
                self.x = self.box.x

        self.vy = min(self.vy + GRAVITY, 18)
        self.y += self.vy
        self.box.y = round(self.y)
        self.on_ground = False

        for platform in platforms:
            if self.box.colliderect(platform):
                if self.vy > 0:
                    self.box.bottom = platform.top
                    self.on_ground = True
                elif self.vy < 0:
                    self.box.top = platform.bottom

                self.y = self.box.y
                self.vy = 0

    def draw(self, surface):
        b = self.box
        pygame.draw.rect(surface, (236, 78, 73), b, border_radius=8)
        pygame.draw.rect(
            surface,
            (255, 236, 189),
            (b.x + 6, b.y + 8, 22, 17),
            border_radius=6,
        )

        eye_x = b.x + (22 if self.facing > 0 else 10)
        pygame.draw.circle(surface, INK, (eye_x, b.y + 15), 3)
        pygame.draw.rect(
            surface,
            (47, 100, 207),
            (b.x + 5, b.y + 29, 24, 12),
            border_radius=3,
        )


class Monster:
    def __init__(self, x, y, left, right, speed):
        self.box = rect(x, y, 38, 32)
        self.x = float(x)
        self.left = left
        self.right = right
        self.speed = speed
        self.alive = True

    def update(self):
        if not self.alive:
            return

        self.x += self.speed

        if self.x < self.left or self.x + self.box.width > self.right:
            self.speed *= -1
            self.x = max(
                self.left,
                min(self.x, self.right - self.box.width),
            )

        self.box.x = round(self.x)

    def draw(self, surface):
        if not self.alive:
            return

        b = self.box
        pygame.draw.ellipse(surface, (143, 73, 183), b)
        pygame.draw.circle(surface, (255, 255, 255), (b.x + 12, b.y + 12), 5)
        pygame.draw.circle(surface, (255, 255, 255), (b.x + 27, b.y + 12), 5)
        pygame.draw.circle(surface, INK, (b.x + 12, b.y + 13), 2)
        pygame.draw.circle(surface, INK, (b.x + 27, b.y + 13), 2)
        pygame.draw.line(surface, INK, (b.x + 12, b.y + 24), (b.x + 27, b.y + 24), 2)


def make_level(number):
    """Create one of 20 progressively harder platform layouts."""
    n = number - 1
    floor_y = 545

    platforms = [rect(0, floor_y, WIDTH, 55)]

    ledges = []
    columns = 4 + n % 4

    for i in range(columns):
        width = 150 - (n % 3) * 10
        x = 75 + i * (850 - width) / max(1, columns - 1)
        y = 425 - ((i * 67 + n * 23) % 230)
        ledges.append(rect(x, y, width, 22))

    platforms.extend(ledges)

    exit_platform = rect(850, 360 - (n % 3) * 55, 120, 22)
    platforms.append(exit_platform)

    spikes = []

    for i in range(1 + n // 3):
        x = 170 + ((i * 211 + n * 47) % 610)
        spikes.append(rect(x, floor_y - 24, 64, 24))

    spikes = [
        spike
        for spike in spikes
        if not spike.colliderect(rect(0, 480, 120, 65))
        and not spike.colliderect(rect(830, 480, 150, 65))
    ]

    coins = []

    for i, platform in enumerate(ledges):
        count = 1 + ((i + n) % 2)

        for coin_number in range(count):
            coins.append(
                rect(
                    platform.x + 24 + coin_number * 38,
                    platform.y - 31,
                    19,
                    19,
                )
            )

    coins.append(rect(exit_platform.x + 50, exit_platform.y - 31, 19, 19))

    monsters = []

    for i, platform in enumerate(ledges[1 : 1 + min(1 + n // 5, 3)]):
        if platform.width >= 100:
            monsters.append(
                Monster(
                    platform.x + 58,
                    platform.y - 32,
                    platform.x + 8,
                    platform.right - 8,
                    1.25 + n * 0.035,
                )
            )

    portal = rect(exit_platform.x + 44, exit_platform.y - 54, 34, 54)

    return {
        "platforms": platforms,
        "spikes": spikes,
        "coins": coins,
        "monsters": monsters,
        "spawn": (45, 475),
        "portal": portal,
    }


def draw_platform(surface, platform):
    pygame.draw.rect(surface, DIRT, platform)
    pygame.draw.rect(
        surface,
        GROUND,
        (platform.x, platform.y, platform.width, 7),
        border_radius=3,
    )
    pygame.draw.line(
        surface,
        (90, 56, 36),
        (platform.x + 8, platform.y + 14),
        (platform.right - 8, platform.y + 14),
        1,
    )


def draw_spikes(surface, spike):
    tooth_width = 16

    for x in range(spike.x, spike.right, tooth_width):
        points = [
            (x, spike.bottom),
            (x + tooth_width // 2, spike.y),
            (min(x + tooth_width, spike.right), spike.bottom),
        ]
        pygame.draw.polygon(surface, (222, 230, 235), points)
        pygame.draw.lines(surface, INK, True, points, 1)


def draw_coin(surface, coin, current_time):
    bob = int(math.sin(current_time * 0.005 + coin.x) * 2)
    coin_rect = coin.move(0, bob)

    pygame.draw.ellipse(surface, (205, 139, 24), coin_rect)
    pygame.draw.ellipse(
        surface,
        GOLD,
        (
            coin_rect.x + 3,
            coin_rect.y,
            coin_rect.width - 6,
            coin_rect.height - 2,
        ),
    )
    pygame.draw.line(
        surface,
        (255, 241, 140),
        (coin_rect.centerx, coin_rect.y + 4),
        (coin_rect.centerx, coin_rect.bottom - 4),
        2,
    )


def draw_background(surface, level):
    surface.fill(SKY)
    pygame.draw.circle(surface, (255, 237, 145), (840, 90), 42)

    for x in range(-30, WIDTH + 60, 100):
        hill_height = 90 + ((x * 7 + level * 23) % 80)
        pygame.draw.polygon(
            surface,
            (90, 173, 131),
            [
                (x, 545),
                (x + 70, 545),
                (x + 35, 545 - hill_height),
            ],
        )

    pygame.draw.rect(surface, (62, 151, 110), (0, 525, WIDTH, 20))


def draw_hud(surface, font, small_font, level, score, total, lives, message):
    pygame.draw.rect(
        surface,
        (255, 255, 255),
        (18, 14, 360, 58),
        border_radius=12,
    )

    surface.blit(font.render(f"LEVEL {level}/20", True, INK), (32, 23))
    surface.blit(
        small_font.render(
            f"Coins: {score}/{total}    Lives: {lives}",
            True,
            INK,
        ),
        (188, 31),
    )

    if message:
        panel = pygame.Rect(0, 0, 570, 72)
        panel.center = (WIDTH // 2, 112)

        pygame.draw.rect(surface, (255, 255, 255), panel, border_radius=14)

        text = font.render(message, True, INK)
        surface.blit(text, text.get_rect(center=panel.center))


def main():
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Coinbound: 20-Level Platformer")

    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 30)
    small_font = pygame.font.Font(None, 24)

    level_number = 1
    score = 0
    level = make_level(level_number)

    player = Player(*level["spawn"])
    state = "playing"
    message = ""
    message_until = 0

    def reset_level(keep_lives=True):
        nonlocal level, score

        level = make_level(level_number)
        score = 0
        player.respawn(*level["spawn"])

        if not keep_lives:
            player.lives = 3

    while True:
        now = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and state != "won":
                    reset_level()
                    state = "playing"
                    message = ""

                if event.key == pygame.K_RETURN and state == "won":
                    level_number = 1
                    score = 0
                    state = "playing"
                    reset_level(False)

        keys = pygame.key.get_pressed()

        if state == "playing":
            player.update(keys, level["platforms"])

            for monster in level["monsters"]:
                monster.update()

            for coin in level["coins"][:]:
                if player.box.colliderect(coin):
                    level["coins"].remove(coin)
                    score += 1

            dead = (
                player.box.top > HEIGHT + 40
                or any(player.box.colliderect(spike) for spike in level["spikes"])
            )

            for monster in level["monsters"]:
                if monster.alive and player.box.colliderect(monster.box):
                    # Stomping from above defeats the monster.
                    if player.vy > 0 and player.box.bottom - monster.box.top < 25:
                        monster.alive = False
                        player.vy = -10
                    else:
                        dead = True

            if dead:
                player.lives -= 1

                if player.lives <= 0:
                    reset_level(False)
                    message = "Out of lives — level restarted!"
                    message_until = now + 1800
                else:
                    player.respawn(*level["spawn"])
                    message = "Ouch! Try again."
                    message_until = now + 1000

            # The portal is only active after collecting all coins.
            if not level["coins"] and player.box.colliderect(level["portal"]):
                if level_number == 20:
                    state = "won"
                else:
                    level_number += 1
                    reset_level()
                    message = f"Level {level_number}!"
                    message_until = now + 1100

        draw_background(screen, level_number)

        for platform in level["platforms"]:
            draw_platform(screen, platform)

        for spike in level["spikes"]:
            draw_spikes(screen, spike)

        for coin in level["coins"]:
            draw_coin(screen, coin, now)

        portal_color = (95, 232, 151) if not level["coins"] else (112, 91, 139)

        pygame.draw.rect(
            screen,
            portal_color,
            level["portal"],
            border_radius=16,
        )
        pygame.draw.rect(
            screen,
            (255, 255, 255),
            level["portal"],
            2,
            border_radius=16,
        )

        for monster in level["monsters"]:
            monster.draw(screen)

        player.draw(screen)

        shown_message = message if now < message_until else ""

        if state == "won":
            shown_message = "YOU BEAT ALL 20 LEVELS! Press Enter to play again"

        draw_hud(
            screen,
            font,
            small_font,
            level_number,
            score,
            score + len(level["coins"]),
            player.lives,
            shown_message,
        )

        controls = small_font.render(
            "Move: A/D or arrows   Jump: Space/W/Up   Restart: R",
            True,
            (255, 255, 255),
        )
        screen.blit(controls, (20, 572))

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()