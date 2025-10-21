import pygame
import time
import random

# Initialize Pygame and fonts
pygame.init()
pygame.font.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Meteor Rush")

# Load background image (make sure Space.png is in the same folder)
BG = pygame.image.load("../../.venv/Game1/Space2.png")

# Constants
PLAYER_HEIGHT = 60
PLAYER_WIDTH = 40
PLAYER_VEL = 10
STAR_WIDTH = 10
STAR_HEIGHT = 20
STAR_VEL = 10

FONT = pygame.font.SysFont("Comic Sans MS", 30)

# Health bar class
class Damage:
    def __init__(self, x, y, w, h, max_hp):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.hp = max_hp
        self.max_hp = max_hp

    def draw(self, surface):
        ratio = self.hp / self.max_hp
        pygame.draw.rect(surface, "red", (self.x, self.y, self.w, self.h))
        pygame.draw.rect(surface, "green", (self.x, self.y, self.w * ratio, self.h))

# Draw all elements
def draw(player, elapsed_time, stars, healthbar):
    WIN.blit(BG, (0, 0))

    time_text = FONT.render(f'Time: {round(elapsed_time)}s', 1, "white")
    WIN.blit(time_text, (10, 10))

    pygame.draw.rect(WIN, (15, 117, 219), player)  # Draw player
    for star in stars:
        pygame.draw.rect(WIN, (67, 68, 69), star)   # Draw meteors

    healthbar.draw(WIN)  # Draw health bar
    pygame.display.update()

# Main game function
def main():
    run = True
    player = pygame.Rect(0, HEIGHT - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT)
    clock = pygame.time.Clock()

    start_time = time.time()
    elapsed_time = 0

    star_add_increment = 2000
    star_count = 0
    stars = []
    music = pygame.mixer.Sound("../../.venv/Game1/Sound.mp3")
    healthbar = Damage(700, 10, 75, 25, 100)

    while run:
        star_count += clock.tick(60)
        elapsed_time = time.time() - start_time

        # Add stars periodically
        if star_count > star_add_increment:
            for _ in range(5):
                star_x = random.randint(0, WIDTH - STAR_WIDTH)
                star = pygame.Rect(star_x, -STAR_HEIGHT, STAR_WIDTH, STAR_HEIGHT)
                stars.append(star)

            star_add_increment = max(200, star_add_increment - 50)
            star_count = 0

        # Quit event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x - PLAYER_VEL >= 0:
            player.x -= PLAYER_VEL
        if keys[pygame.K_RIGHT] and player.x + PLAYER_VEL + player.width <= WIDTH:
            player.x += PLAYER_VEL

        # Move stars and check for collision
        for star in stars[:]:
            star.y += STAR_VEL
            if star.y > HEIGHT:
                stars.remove(star)
            elif star.y + star.height >= player.y and star.colliderect(player):
                stars.remove(star)
                healthbar.hp -= 20
                music.play()
                break


        # If health is 0 or less, show final health bar before game over
        if healthbar.hp <= 0:
            draw(player, elapsed_time, stars, healthbar)
            pygame.display.update()
            pygame.time.delay(1000)

            lost_text = FONT.render("You Lost!", 1, "white")
            WIN.blit(lost_text, (WIDTH / 2 - lost_text.get_width() / 2,
                                 HEIGHT / 2 - lost_text.get_height() / 2))
            pygame.display.update()
            pygame.time.delay(3000)
            break

        # Draw everything
        draw(player, elapsed_time, stars, healthbar)

    pygame.quit()

if __name__ == "__main__":
    main()
