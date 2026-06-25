import pygame
import random
import sys

pygame.init()

WIDTH, HEIGHT = 500, 700
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Car Racing Game")
CLOCK = pygame.time.Clock()
FPS = 60

LANES = 5
LANE_WIDTH = WIDTH // LANES
CAR_WIDTH = LANE_WIDTH - 20
CAR_HEIGHT = 90

WHITE = (255, 255, 255)
GRAY = (60, 60, 60)
YELLOW = (255, 220, 0)
RED = (220, 30, 30)
BLUE = (30, 100, 220)
GREEN = (30, 200, 80)
BLACK = (0, 0, 0)

FONT = pygame.font.SysFont(None, 48)
SMALL_FONT = pygame.font.SysFont(None, 32)


def lane_x(lane):
    return lane * LANE_WIDTH + (LANE_WIDTH - CAR_WIDTH) // 2


class Player:
    def __init__(self):
        self.lane = LANES // 2
        self.y = HEIGHT - CAR_HEIGHT - 20
        self.rect = pygame.Rect(lane_x(self.lane), self.y, CAR_WIDTH, CAR_HEIGHT)

    def move(self, direction):
        new_lane = self.lane + direction
        if 0 <= new_lane < LANES:
            self.lane = new_lane
            self.rect.x = lane_x(self.lane)

    def draw(self):
        pygame.draw.rect(SCREEN, BLUE, self.rect, border_radius=8)
        pygame.draw.rect(SCREEN, BLACK, self.rect, 2, border_radius=8)


class EnemyCar:
    def __init__(self, speed):
        self.lane = random.randint(0, LANES - 1)
        self.rect = pygame.Rect(lane_x(self.lane), -CAR_HEIGHT, CAR_WIDTH, CAR_HEIGHT)
        self.speed = speed
        self.color = random.choice([RED, GREEN, YELLOW, (200, 100, 200)])

    def update(self):
        self.rect.y += self.speed

    def draw(self):
        pygame.draw.rect(SCREEN, self.color, self.rect, border_radius=8)
        pygame.draw.rect(SCREEN, BLACK, self.rect, 2, border_radius=8)

    def off_screen(self):
        return self.rect.y > HEIGHT


def draw_road():
    SCREEN.fill(GRAY)
    for i in range(1, LANES):
        x = i * LANE_WIDTH
        for y in range(0, HEIGHT, 40):
            pygame.draw.rect(SCREEN, WHITE, (x - 2, y, 4, 20))


def draw_text_center(text, font, color, y):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(WIDTH // 2, y))
    SCREEN.blit(surf, rect)


def main():
    player = Player()
    enemies = []
    spawn_timer = 0
    spawn_interval = 60  # frames
    enemy_speed = 5
    score = 0
    game_over = False

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if not game_over:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        player.move(-1)
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        player.move(1)
                else:
                    if event.key == pygame.K_r:
                        # Restart
                        player = Player()
                        enemies = []
                        spawn_timer = 0
                        spawn_interval = 60
                        enemy_speed = 5
                        score = 0
                        game_over = False

        if not game_over:
            # Spawn enemies
            spawn_timer += 1
            if spawn_timer >= spawn_interval:
                spawn_timer = 0
                enemies.append(EnemyCar(enemy_speed))

            # Update enemies
            for enemy in enemies:
                enemy.update()

            enemies = [e for e in enemies if not e.off_screen()]

            # Score and difficulty increase
            score += 1
            if score % 300 == 0:
                enemy_speed += 1
                spawn_interval = max(20, spawn_interval - 5)

            # Collision check
            for enemy in enemies:
                if player.rect.colliderect(enemy.rect):
                    game_over = True

        # Draw everything
        draw_road()
        player.draw()
        for enemy in enemies:
            enemy.draw()

        score_surf = SMALL_FONT.render(f"Score: {score}", True, WHITE)
        SCREEN.blit(score_surf, (10, 10))

        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            SCREEN.blit(overlay, (0, 0))
            draw_text_center("GAME OVER", FONT, RED, HEIGHT // 2 - 40)
            draw_text_center(f"Final Score: {score}", SMALL_FONT, WHITE, HEIGHT // 2 + 10)
            draw_text_center("Press R to Restart", SMALL_FONT, WHITE, HEIGHT // 2 + 50)

        pygame.display.flip()
        CLOCK.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()