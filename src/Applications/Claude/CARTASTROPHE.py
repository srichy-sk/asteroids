import math
import random
import sys
import pygame

WIDTH, HEIGHT = 1000, 700
FPS = 60
ROAD_WIDTH = 240


def clamp(value, low, high):
    return max(low, min(high, value))


def forward(angle):
    return pygame.Vector2(math.sin(angle), -math.cos(angle))


def side(angle):
    return pygame.Vector2(math.cos(angle), math.sin(angle))


class Track:
    def __init__(self, level):
        self.level = level
        self.points = self.make_points(level)
        self.lengths = [0]
        total = 0

        for a, b in zip(self.points, self.points[1:]):
            total += a.distance_to(b)
            self.lengths.append(total)

        self.total_length = total
        self.finish_progress = self.lengths[-8]
        self.road_width = ROAD_WIDTH - min(level * 8, 55)

    def make_points(self, level):
        random.seed(1000 + level)
        points = [pygame.Vector2(0, 0)]
        heading = 0

        for i in range(95 + level * 10):
            turn = math.sin(i * 0.22) * 0.08
            turn += random.uniform(-0.04, 0.04)

            if i % 17 in (7, 8, 9):
                turn += random.choice([-1, 1]) * 0.08

            heading = clamp(heading + turn, -1.25, 1.25)
            points.append(points[-1] + forward(heading) * 95)

        return points

    def sample(self, progress):
        progress = clamp(progress, 0, self.total_length)

        for i in range(1, len(self.lengths)):
            if self.lengths[i] >= progress:
                a = self.points[i - 1]
                b = self.points[i]
                span = self.lengths[i] - self.lengths[i - 1]
                t = 0 if span == 0 else (progress - self.lengths[i - 1]) / span
                pos = a.lerp(b, t)
                d = b - a
                heading = math.atan2(d.x, -d.y)
                return pos, heading

        d = self.points[-1] - self.points[-2]
        return self.points[-1], math.atan2(d.x, -d.y)

    def nearest(self, pos):
        best_dist = 999999
        best_progress = 0

        for i, (a, b) in enumerate(zip(self.points, self.points[1:])):
            ab = b - a
            t = clamp((pos - a).dot(ab) / ab.length_squared(), 0, 1)
            closest = a + ab * t
            dist = pos.distance_to(closest)

            if dist < best_dist:
                best_dist = dist
                best_progress = self.lengths[i] + ab.length() * t

        return best_dist, best_progress

    def draw(self, screen, camera):
        center = pygame.Vector2(WIDTH / 2, HEIGHT / 2)
        shifted = [p - camera + center for p in self.points]

        pygame.draw.lines(screen, (190, 195, 200), False, shifted, self.road_width + 34)
        pygame.draw.lines(screen, (45, 48, 50), False, shifted, self.road_width + 10)
        pygame.draw.lines(screen, (72, 76, 78), False, shifted, self.road_width)

        for i in range(5, len(self.points) - 5, 5):
            pos, heading = self.sample(self.lengths[i])
            screen_pos = pos - camera + center
            n = side(heading)

            left = screen_pos - n * (self.road_width / 2 - 20)
            right = screen_pos + n * (self.road_width / 2 - 20)
            pygame.draw.line(screen, (220, 225, 225), left, right, 3)

        finish_pos, finish_heading = self.sample(self.finish_progress)
        finish_screen = finish_pos - camera + center
        n = side(finish_heading)

        for i in range(10):
            color = (255, 255, 255) if i % 2 == 0 else (10, 10, 10)
            a = finish_screen - n * (self.road_width / 2) + n * (i * self.road_width / 10)
            b = finish_screen - n * (self.road_width / 2) + n * ((i + 1) * self.road_width / 10)
            pygame.draw.line(screen, color, a, b, 10)


class RivalCar:
    def __init__(self, progress, lane, speed, color):
        self.progress = progress
        self.lane = lane
        self.speed = speed
        self.color = color

    def update(self, dt, track):
        self.progress += self.speed * dt

        if self.progress > track.finish_progress - 100:
            self.progress = random.randint(600, 1800)

    def position(self, track):
        pos, heading = track.sample(self.progress)
        return pos + side(heading) * self.lane, heading


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("CARTASTROPHE")

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        self.font = pygame.font.Font(None, 32)
        self.big_font = pygame.font.Font(None, 76)

        self.level = 1
        self.reset_level()

    def reset_level(self):
        self.track = Track(self.level)

        start_pos, start_heading = self.track.sample(40)
        self.player_pos = pygame.Vector2(start_pos)
        self.heading = start_heading
        self.speed = 0
        self.nitro = 100
        self.camera = pygame.Vector2(self.player_pos)
        self.state = "playing"
        self.next_level_timer = 0

        self.rivals = []
        lanes = [-70, 0, 70, -35, 35]
        colors = [
            (220, 50, 50),
            (60, 130, 230),
            (240, 180, 40),
            (150, 80, 220),
            (30, 180, 120),
        ]

        for i in range(5 + self.level):
            progress = 600 + i * 430 + random.randint(-80, 80)
            lane = lanes[i % len(lanes)]
            speed = 90 + self.level * 8 + random.randint(-10, 20)
            color = colors[i % len(colors)]
            self.rivals.append(RivalCar(progress, lane, speed, color))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                if event.key == pygame.K_r and self.state == "crashed":
                    self.reset_level()

    def update(self, dt):
        keys = pygame.key.get_pressed()

        if self.state == "playing":
            acceleration = 0

            if keys[pygame.K_UP]:
                acceleration += 230

            if keys[pygame.K_DOWN]:
                acceleration -= 100

            braking = keys[pygame.K_LALT] or keys[pygame.K_RALT]
            if braking:
                self.speed *= max(0, 1 - 3 * dt)

            nitro_on = (
                keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
            ) and self.nitro > 0 and self.speed > 40

            if nitro_on:
                acceleration += 430
                self.nitro -= 35 * dt
            else:
                self.nitro += 12 * dt

            self.nitro = clamp(self.nitro, 0, 100)

            self.speed += acceleration * dt
            self.speed *= max(0, 1 - 0.55 * dt)

            max_speed = 360 + self.level * 20
            if nitro_on:
                max_speed += 120

            self.speed = clamp(self.speed, 0, max_speed)

            steer = 0
            if keys[pygame.K_LEFT]:
                steer -= 1
            if keys[pygame.K_RIGHT]:
                steer += 1

            steer_power = 2.4 * (0.35 + min(self.speed, 260) / 260)
            self.heading += steer * steer_power * dt

            self.player_pos += forward(self.heading) * self.speed * dt

            road_dist, progress = self.track.nearest(self.player_pos)

            if road_dist > self.track.road_width / 2:
                self.speed *= max(0, 1 - 2.5 * dt)

            for rival in self.rivals:
                rival.update(dt, self.track)
                rival_pos, rival_heading = rival.position(self.track)

                if self.player_pos.distance_to(rival_pos) < 42:
                    self.state = "crashed"
                    self.speed = 0

            if progress >= self.track.finish_progress:
                self.state = "finished"
                self.next_level_timer = 1.3
                self.speed = 0

        elif self.state == "finished":
            self.next_level_timer -= dt

            if self.next_level_timer <= 0:
                self.level += 1
                self.reset_level()

        self.camera += (self.player_pos - self.camera) * min(1, 7 * dt)

    def draw_car(self, pos, heading, color, label=None):
        center = pygame.Vector2(WIDTH / 2, HEIGHT / 2)
        screen_pos = pos - self.camera + center

        car = pygame.Surface((34, 58), pygame.SRCALPHA)
        pygame.draw.rect(car, (20, 20, 24), (4, 5, 26, 50), border_radius=7)
        pygame.draw.rect(car, color, (6, 7, 22, 46), border_radius=6)
        pygame.draw.rect(car, (25, 40, 55), (9, 14, 16, 12), border_radius=3)
        pygame.draw.rect(car, (15, 20, 25), (9, 36, 16, 10), border_radius=3)
        pygame.draw.line(car, (255, 255, 255), (17, 7), (17, 53), 2)
        pygame.draw.rect(car, (255, 230, 120), (8, 4, 6, 4), border_radius=2)
        pygame.draw.rect(car, (255, 230, 120), (20, 4, 6, 4), border_radius=2)

        rotated = pygame.transform.rotate(car, -math.degrees(heading))
        rect = rotated.get_rect(center=screen_pos)
        self.screen.blit(rotated, rect)

        if label:
            text = self.font.render(label, True, (255, 255, 255))
            text_rect = text.get_rect(center=(screen_pos.x, screen_pos.y - 45))
            self.screen.blit(text, text_rect)

    def draw_hud(self):
        road_dist, progress = self.track.nearest(self.player_pos)
        progress_percent = clamp(progress / self.track.finish_progress, 0, 1)

        pygame.draw.rect(self.screen, (10, 15, 20), (0, 0, WIDTH, 90))

        level_text = self.font.render(f"LEVEL {self.level}", True, (255, 255, 255))
        speed_text = self.font.render(f"{int(self.speed)} MPH", True, (255, 255, 255))
        controls_text = self.font.render(
            "Arrows: drive   Shift: nitro   Option/Alt: brake   R: restart",
            True,
            (210, 220, 230),
        )

        self.screen.blit(level_text, (25, 15))
        self.screen.blit(controls_text, (25, 52))
        self.screen.blit(speed_text, (WIDTH - 150, 15))

        pygame.draw.rect(self.screen, (30, 40, 50), (WIDTH - 260, 55, 180, 18), border_radius=5)
        pygame.draw.rect(
            self.screen,
            (70, 220, 255),
            (WIDTH - 260, 55, int(180 * self.nitro / 100), 18),
            border_radius=5,
        )

        pygame.draw.rect(self.screen, (30, 40, 50), (300, 22, 330, 22), border_radius=6)
        pygame.draw.rect(
            self.screen,
            (80, 230, 70),
            (300, 22, int(330 * progress_percent), 22),
            border_radius=6,
        )

    def draw_status(self):
        if self.state == "crashed":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((120, 0, 0, 160))
            self.screen.blit(overlay, (0, 0))

            text = self.big_font.render("CRASHED!", True, (255, 240, 230))
            hint = self.font.render("You hit another car. Press R to restart.", True, (255, 240, 230))

            self.screen.blit(text, text.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 35)))
            self.screen.blit(hint, hint.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 35)))

        elif self.state == "finished":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 80, 20, 150))
            self.screen.blit(overlay, (0, 0))

            text = self.big_font.render("FINISH!", True, (235, 255, 235))
            hint = self.font.render(f"Loading level {self.level + 1}...", True, (235, 255, 235))

            self.screen.blit(text, text.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 35)))
            self.screen.blit(hint, hint.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 35)))

    def draw(self):
        self.screen.fill((40, 95, 65))

        self.track.draw(self.screen, self.camera)

        for rival in self.rivals:
            rival_pos, rival_heading = rival.position(self.track)
            self.draw_car(rival_pos, rival_heading, rival.color)

        self.draw_car(self.player_pos, self.heading, (25, 30, 38), "YOU")

        self.draw_hud()
        self.draw_status()

        pygame.display.flip()

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000
            self.handle_events()
            self.update(dt)
            self.draw()


if __name__ == "__main__":
    Game().run()