import math
import random
from dataclasses import dataclass

import pygame


WIDTH, HEIGHT = 1100, 650
FPS = 60
GROUND_Y = 545
GRAVITY = 0.72
FRICTION = 0.985
AIR_DRAG = 0.996
MAX_SPEED = 13.0


SKY = (132, 194, 225)
SKY_DARK = (88, 148, 186)
INK = (28, 34, 44)
CONCRETE = (93, 97, 105)
CONCRETE_DARK = (60, 63, 70)
PIPE = (220, 226, 226)
PIPE_DARK = (126, 137, 140)
YELLOW = (250, 205, 82)
PINK = (232, 83, 133)
GREEN = (91, 202, 142)
BLUE = (70, 119, 216)
WHITE = (245, 247, 244)
RED = (231, 78, 74)


def clamp(value, low, high):
    return max(low, min(high, value))


def draw_text(surface, font, text, pos, color=WHITE, shadow=True, center=False):
    x, y = pos
    if shadow:
        img = font.render(text, True, (0, 0, 0))
        rect = img.get_rect()
        rect.center = (x + 2, y + 2) if center else rect.move(x + 2, y + 2).topleft
        if not center:
            rect.topleft = (x + 2, y + 2)
        surface.blit(img, rect)

    img = font.render(text, True, color)
    rect = img.get_rect()
    rect.center = (x, y) if center else rect.move(x, y).topleft
    if not center:
        rect.topleft = (x, y)
    surface.blit(img, rect)


@dataclass
class PipeRail:
    x1: float
    y1: float
    x2: float
    y2: float
    name: str

    @property
    def left(self):
        return min(self.x1, self.x2)

    @property
    def right(self):
        return max(self.x1, self.x2)

    @property
    def slope(self):
        return (self.y2 - self.y1) / (self.x2 - self.x1)

    def y_at(self, x):
        t = (x - self.x1) / (self.x2 - self.x1)
        return self.y1 + (self.y2 - self.y1) * t

    def draw(self, surface, camera_x):
        p1 = (int(self.x1 - camera_x), int(self.y1))
        p2 = (int(self.x2 - camera_x), int(self.y2))
        pygame.draw.line(surface, PIPE_DARK, (p1[0], p1[1] + 7), (p2[0], p2[1] + 7), 16)
        pygame.draw.line(surface, PIPE, p1, p2, 11)
        pygame.draw.circle(surface, PIPE, p1, 7)
        pygame.draw.circle(surface, PIPE, p2, 7)


class Skater:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = 150.0
        self.y = GROUND_Y - 42
        self.vx = 4.0
        self.vy = 0.0
        self.angle = 0.0
        self.spin = 0.0
        self.on_ground = True
        self.grinding = False
        self.rail = None
        self.balance = 0.0
        self.combo = []
        self.combo_points = 0
        self.score = 0
        self.best_combo = 0
        self.trick_timer = 0
        self.message = "Push, pop, trick, grind."
        self.message_timer = 180
        self.bailed = False
        self.bail_timer = 0
        self.combo_timeout = 0
        self.spark_timer = 0
        self.direction = 1

    def add_trick(self, name, points):
        self.combo.append(name)
        self.combo_points += points
        self.trick_timer = 22
        self.combo_timeout = 135
        self.message = f"{name}! +{points}"
        self.message_timer = 95

    def land_combo(self):
        if self.combo_points > 0:
            multiplier = 1 + max(0, len(self.combo) - 1) * 0.35
            landed = int(self.combo_points * multiplier)
            self.score += landed
            self.best_combo = max(self.best_combo, landed)
            self.message = f"Landed {' + '.join(self.combo[:4])}{'...' if len(self.combo) > 4 else ''}  {landed} pts"
            self.message_timer = 130
        self.combo.clear()
        self.combo_points = 0
        self.combo_timeout = 0

    def bail(self, reason):
        lost = self.combo_points
        self.combo.clear()
        self.combo_points = 0
        self.combo_timeout = 0
        self.bailed = True
        self.bail_timer = 90
        self.grinding = False
        self.rail = None
        self.vx *= 0.25
        self.vy = -3
        self.angle = random.choice([-70, 70])
        self.message = f"Bailed: {reason}" + (f" - lost {lost}" if lost else "")
        self.message_timer = 120

    def try_grind(self, rails):
        if self.grinding or self.on_ground or self.vy < -1:
            return

        board_y = self.y + 6
        for rail in rails:
            if rail.left - 10 <= self.x <= rail.right + 10:
                rail_y = rail.y_at(clamp(self.x, rail.left, rail.right))
                if abs(board_y - rail_y) < 22 and abs(self.vx) > 2.0:
                    self.grinding = True
                    self.rail = rail
                    self.y = rail_y - 6
                    self.vy = 0
                    self.balance = random.uniform(-12, 12)
                    self.angle = math.degrees(math.atan(rail.slope))
                    self.spark_timer = 8
                    self.add_trick(f"{rail.name} Grind", 350)
                    return

    def update(self, keys, rails):
        if self.bailed:
            self.bail_timer -= 1
            self.x += self.vx
            self.y += self.vy
            self.vy += GRAVITY
            if self.y >= GROUND_Y - 42:
                self.y = GROUND_Y - 42
                self.vy = 0
                self.angle *= 0.75
                if self.bail_timer <= 0:
                    self.bailed = False
                    self.on_ground = True
            return

        if self.message_timer > 0:
            self.message_timer -= 1

        if self.combo_timeout > 0:
            self.combo_timeout -= 1
            if self.combo_timeout == 0 and self.on_ground and not self.grinding:
                self.land_combo()

        push = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a])
        crouch = keys[pygame.K_DOWN] or keys[pygame.K_s]

        if push:
            self.direction = 1 if push > 0 else -1

        if self.grinding:
            self.update_grind(keys, push)
        else:
            if self.on_ground:
                accel = 0.25 if not crouch else 0.08
                self.vx += push * accel
                self.vx *= FRICTION
                if crouch:
                    self.message = "Crouched: bigger pop ready"
                    self.message_timer = 18
                self.angle *= 0.82
            else:
                self.vx += push * 0.07
                self.vx *= AIR_DRAG
                self.vy += GRAVITY
                self.angle += self.spin
                self.spin *= 0.985
                self.try_grind(rails)

            self.vx = clamp(self.vx, -MAX_SPEED, MAX_SPEED)
            self.x += self.vx
            self.y += self.vy

            if self.y >= GROUND_Y - 42:
                hard_landing = abs(self.angle) % 360
                hard_landing = min(hard_landing, 360 - hard_landing)
                self.y = GROUND_Y - 42
                self.vy = 0
                if not self.on_ground:
                    if hard_landing > 65 and abs(self.vx) > 3:
                        self.bail("landed sideways")
                    else:
                        self.land_combo()
                        self.angle = 0
                self.on_ground = True

        if self.x < 50:
            self.x = 50
            self.vx = abs(self.vx) * 0.5

    def jump(self, high=False):
        if self.bailed:
            return

        if self.on_ground:
            self.vy = -15.5 if high else -12.3
            self.on_ground = False
            self.grinding = False
            self.rail = None
            self.add_trick("Ollie" if not high else "Boned Ollie", 90 if not high else 140)
        elif self.grinding:
            self.vy = -11.8
            self.on_ground = False
            self.grinding = False
            self.rail = None
            self.add_trick("Pop Out", 160)

    def do_flip(self):
        if not self.on_ground and not self.bailed:
            self.spin += 6.2 * self.direction
            self.add_trick(random.choice(["Kickflip", "Heelflip", "Varial Flip"]), 260)

    def do_grab(self):
        if not self.on_ground and not self.bailed:
            self.vy += 0.55
            self.angle += 11 * self.direction
            self.add_trick(random.choice(["Method Grab", "Tail Grab", "Melon"]), 210)

    def do_spin(self):
        if not self.on_ground and not self.bailed:
            self.spin += 3.8 * self.direction
            self.add_trick("180 Spin", 180)

    def update_grind(self, keys, push):
        rail = self.rail
        self.on_ground = False
        self.vx += rail.slope * 0.11
        self.vx += push * 0.045
        self.vx *= 0.992
        self.vx = clamp(self.vx, -MAX_SPEED, MAX_SPEED)
        self.x += self.vx
        self.y = rail.y_at(clamp(self.x, rail.left, rail.right)) - 6
        self.angle = math.degrees(math.atan(rail.slope))

        self.balance += random.uniform(-1.7, 1.7) + push * 1.1
        if keys[pygame.K_q]:
            self.balance -= 2.6
        if keys[pygame.K_e]:
            self.balance += 2.6
        self.balance *= 0.965

        self.combo_points += 1
        self.spark_timer = (self.spark_timer + 1) % 12

        if abs(self.balance) > 48:
            self.bail("lost grind balance")
            return

        if self.x < rail.left or self.x > rail.right or abs(self.vx) < 1.0:
            self.grinding = False
            self.rail = None
            self.vy = -2.4
            self.on_ground = False
            self.add_trick("Clean Dismount", 120)

    def draw(self, surface, camera_x):
        sx = int(self.x - camera_x)
        sy = int(self.y)

        if self.bailed:
            pygame.draw.circle(surface, PINK, (sx, sy - 18), 12)
            pygame.draw.line(surface, INK, (sx - 22, sy - 4), (sx + 20, sy + 13), 5)
            pygame.draw.line(surface, BLUE, (sx - 8, sy - 8), (sx - 30, sy - 28), 5)
            pygame.draw.line(surface, BLUE, (sx + 8, sy - 3), (sx + 32, sy - 18), 5)
            pygame.draw.line(surface, INK, (sx - 26, sy + 25), (sx + 28, sy + 19), 4)
            return

        board_len = 58
        board_angle = math.radians(self.angle)
        dx = math.cos(board_angle) * board_len / 2
        dy = math.sin(board_angle) * board_len / 2
        board_a = (sx - dx, sy + 12 - dy)
        board_b = (sx + dx, sy + 12 + dy)

        pygame.draw.line(surface, YELLOW, board_a, board_b, 8)
        pygame.draw.circle(surface, INK, (int(board_a[0] + 7), int(board_a[1] + 7)), 4)
        pygame.draw.circle(surface, INK, (int(board_b[0] - 7), int(board_b[1] + 7)), 4)

        body_sway = math.sin(pygame.time.get_ticks() * 0.012) * 3
        pygame.draw.line(surface, INK, (sx, sy + 8), (sx + int(body_sway), sy - 28), 6)
        pygame.draw.circle(surface, PINK, (sx + int(body_sway), sy - 42), 11)
        pygame.draw.line(surface, BLUE, (sx, sy - 7), (sx - 19, sy + 9), 5)
        pygame.draw.line(surface, BLUE, (sx + 3, sy - 8), (sx + 23, sy + 8), 5)
        pygame.draw.line(surface, GREEN, (sx + int(body_sway), sy - 24), (sx - 21 * self.direction, sy - 12), 5)
        pygame.draw.line(surface, GREEN, (sx + int(body_sway), sy - 22), (sx + 23 * self.direction, sy - 18), 5)

        if self.grinding:
            for _ in range(5):
                ox = random.randint(-24, 24)
                oy = random.randint(4, 18)
                pygame.draw.circle(surface, random.choice([YELLOW, WHITE, RED]), (sx + ox, sy + oy), random.randint(1, 3))


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Pipe Dream Skater")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 30)
        self.small_font = pygame.font.Font(None, 23)
        self.skater = Skater()
        self.camera_x = 0
        self.running = True
        self.rails = [
            PipeRail(380, 470, 690, 420, "Downpipe"),
            PipeRail(900, 395, 1250, 395, "Neon Pipe"),
            PipeRail(1450, 478, 1840, 438, "Kinked Pipe"),
            PipeRail(2050, 385, 2430, 468, "Rainbow Pipe"),
            PipeRail(2700, 455, 3100, 420, "Long Pipe"),
        ]
        self.clouds = [(80, 90, 80), (350, 130, 115), (730, 75, 95), (1000, 155, 105)]
        self.camera_limit = 3300

    def reset(self):
        self.skater.reset()
        self.camera_x = 0

    def handle_events(self):
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                if event.key == pygame.K_r:
                    self.reset()
                if event.key == pygame.K_SPACE:
                    self.skater.jump(high=keys[pygame.K_DOWN] or keys[pygame.K_s])
                if event.key == pygame.K_z:
                    self.skater.do_flip()
                if event.key == pygame.K_x:
                    self.skater.do_grab()
                if event.key == pygame.K_c:
                    self.skater.do_spin()

        return keys

    def update(self):
        keys = self.handle_events()
        self.skater.update(keys, self.rails)

        target = clamp(self.skater.x - WIDTH * 0.34, 0, self.camera_limit - WIDTH)
        self.camera_x += (target - self.camera_x) * 0.08

        if self.skater.x > self.camera_limit - 80:
            bonus = 1500 + self.skater.score // 10
            self.skater.score += bonus
            self.skater.message = f"Line complete! bonus {bonus}. Press R for another run."
            self.skater.message_timer = 9999
            self.skater.x = self.camera_limit - 80
            self.skater.vx = 0

    def draw_background(self):
        self.screen.fill(SKY)

        for y in range(0, HEIGHT, 3):
            mix = y / HEIGHT
            color = (
                int(SKY[0] * (1 - mix) + SKY_DARK[0] * mix),
                int(SKY[1] * (1 - mix) + SKY_DARK[1] * mix),
                int(SKY[2] * (1 - mix) + SKY_DARK[2] * mix),
            )
            pygame.draw.line(self.screen, color, (0, y), (WIDTH, y))

        for base_x, y, w in self.clouds:
            x = int((base_x - self.camera_x * 0.22) % (WIDTH + 260) - 130)
            pygame.draw.ellipse(self.screen, (236, 245, 245), (x, y, w, 28))
            pygame.draw.ellipse(self.screen, (236, 245, 245), (x + w * 0.25, y - 18, w * 0.45, 38))

        for i in range(-1, 8):
            bx = i * 180 - int(self.camera_x * 0.35) % 180
            height = 115 + (i % 3) * 28
            pygame.draw.rect(self.screen, (72, 91, 113), (bx, GROUND_Y - height, 112, height))
            for wy in range(GROUND_Y - height + 18, GROUND_Y - 16, 28):
                for wx in range(bx + 13, bx + 92, 28):
                    pygame.draw.rect(self.screen, (244, 213, 111), (wx, wy, 11, 12))

        pygame.draw.rect(self.screen, CONCRETE_DARK, (0, GROUND_Y + 26, WIDTH, HEIGHT - GROUND_Y))
        pygame.draw.rect(self.screen, CONCRETE, (0, GROUND_Y, WIDTH, 34))

        for x in range(-100, WIDTH + 160, 72):
            sx = x - int(self.camera_x) % 72
            pygame.draw.line(self.screen, CONCRETE_DARK, (sx, GROUND_Y), (sx + 46, GROUND_Y + 34), 2)

    def draw_course(self):
        for rail in self.rails:
            rail.draw(self.screen, self.camera_x)
            if rail.left - self.camera_x < WIDTH and rail.right - self.camera_x > 0:
                draw_text(
                    self.screen,
                    self.small_font,
                    rail.name,
                    (rail.left - self.camera_x + 8, rail.y_at(rail.left) - 38),
                    INK,
                    shadow=False,
                )

        for x in range(260, self.camera_limit, 360):
            sx = int(x - self.camera_x)
            if -80 < sx < WIDTH + 80:
                pygame.draw.polygon(self.screen, (66, 78, 92), [(sx, GROUND_Y), (sx + 70, GROUND_Y), (sx + 35, GROUND_Y - 48)])
                pygame.draw.polygon(self.screen, (86, 98, 114), [(sx + 70, GROUND_Y), (sx + 120, GROUND_Y), (sx + 35, GROUND_Y - 48)])

    def draw_hud(self):
        pygame.draw.rect(self.screen, (23, 29, 38), (0, 0, WIDTH, 75))

        draw_text(self.screen, self.font, f"Score {self.skater.score}", (22, 14), YELLOW)
        draw_text(self.screen, self.font, f"Best Combo {self.skater.best_combo}", (22, 43), GREEN)

        combo = " + ".join(self.skater.combo[-3:]) if self.skater.combo else "none"
        draw_text(self.screen, self.font, f"Combo {self.skater.combo_points}: {combo}", (240, 14), WHITE)
        draw_text(
            self.screen,
            self.small_font,
            "Move A/D or arrows  Jump SPACE  Flip Z  Grab X  Spin C  Balance Q/E  Restart R",
            (240, 47),
            (202, 216, 226),
        )

        if self.skater.grinding:
            cx, cy = WIDTH - 170, 35
            pygame.draw.rect(self.screen, (7, 12, 18), (cx - 92, cy - 12, 184, 24), border_radius=4)
            pygame.draw.line(self.screen, WHITE, (cx - 78, cy), (cx + 78, cy), 3)
            bx = int(cx + clamp(self.skater.balance, -48, 48) / 48 * 76)
            pygame.draw.circle(self.screen, RED if abs(self.skater.balance) > 35 else YELLOW, (bx, cy), 9)
            draw_text(self.screen, self.small_font, "GRIND BALANCE", (cx - 70, cy + 18), WHITE)

        if self.skater.message_timer > 0:
            color = RED if "Bailed" in self.skater.message else WHITE
            draw_text(self.screen, self.font, self.skater.message, (WIDTH // 2, 105), color, center=True)

        if self.skater.x < 230 and self.skater.score == 0:
            lines = [
                "Hit SPACE near a pipe to pop onto it.",
                "While grinding, tap Q/E to keep balance centered.",
                "Chain Z, X, and C in the air, then land straight.",
            ]
            for i, line in enumerate(lines):
                draw_text(self.screen, self.small_font, line, (38, 112 + i * 25), INK, shadow=False)

    def draw(self):
        self.draw_background()
        self.draw_course()
        self.skater.draw(self.screen, self.camera_x)
        self.draw_hud()
        pygame.display.flip()

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.update()
            self.draw()

        pygame.quit()


if __name__ == "__main__":
    Game().run()