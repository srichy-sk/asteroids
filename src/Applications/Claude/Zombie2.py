import pygame
import random
import math

pygame.init()

# ---------------- SETTINGS ----------------
WIDTH, HEIGHT = 1200, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fortnite Zombie Survival")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

WHITE = (255,255,255)
BLACK = (0,0,0)
GREEN = (0,200,0)
RED = (220,50,50)
BLUE = (50,100,255)
YELLOW = (255,255,0)
PURPLE = (180,50,255)

# ---------------- PLAYER ----------------
player_x = WIDTH//2
player_y = HEIGHT//2
player_speed = 5
player_health = 100

# ---------------- GUNS ----------------
guns = {
    "Pistol": {"damage":20,"cooldown":15,"color":YELLOW},
    "Rifle": {"damage":10,"cooldown":5,"color":BLUE},
    "Shotgun": {"damage":15,"cooldown":25,"color":PURPLE}
}

current_gun = "Pistol"
shoot_timer = 0

# ---------------- BULLETS ----------------
bullets = []

# ---------------- ZOMBIES ----------------
zombies = []
score = 0

# ---------------- HEALTH JUICE ----------------
juices = []

# ---------------- FUNCTIONS ----------------
def spawn_zombie():
    side = random.randint(0,3)

    if side == 0:
        x = random.randint(0, WIDTH)
        y = -50
    elif side == 1:
        x = WIDTH+50
        y = random.randint(0, HEIGHT)
    elif side == 2:
        x = random.randint(0, WIDTH)
        y = HEIGHT+50
    else:
        x = -50
        y = random.randint(0, HEIGHT)

    zombies.append({
        "x": x,
        "y": y,
        "health": 50,
        "speed": random.uniform(1.5,2.5)
    })

def spawn_juice():
    juices.append({
        "x": random.randint(50, WIDTH-50),
        "y": random.randint(50, HEIGHT-50)
    })

for _ in range(5):
    spawn_zombie()

spawn_juice()

# ---------------- GAME LOOP ----------------
running = True

while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                current_gun = "Pistol"

            if event.key == pygame.K_2:
                current_gun = "Rifle"

            if event.key == pygame.K_3:
                current_gun = "Shotgun"

    keys = pygame.key.get_pressed()

    if keys[pygame.K_w]:
        player_y -= player_speed
    if keys[pygame.K_s]:
        player_y += player_speed
    if keys[pygame.K_a]:
        player_x -= player_speed
    if keys[pygame.K_d]:
        player_x += player_speed

    player_x = max(20, min(WIDTH-20, player_x))
    player_y = max(20, min(HEIGHT-20, player_y))

    # Shooting
    if shoot_timer > 0:
        shoot_timer -= 1

    mouse_pressed = pygame.mouse.get_pressed()[0]

    if mouse_pressed and shoot_timer == 0:

        mx, my = pygame.mouse.get_pos()

        angle = math.atan2(my-player_y, mx-player_x)

        if current_gun == "Shotgun":

            for spread in [-0.2, 0, 0.2]:
                bullets.append({
                    "x": player_x,
                    "y": player_y,
                    "dx": math.cos(angle+spread)*10,
                    "dy": math.sin(angle+spread)*10,
                    "damage": guns[current_gun]["damage"]
                })
        else:
            bullets.append({
                "x": player_x,
                "y": player_y,
                "dx": math.cos(angle)*12,
                "dy": math.sin(angle)*12,
                "damage": guns[current_gun]["damage"]
            })

        shoot_timer = guns[current_gun]["cooldown"]

    # Update bullets
    for bullet in bullets[:]:
        bullet["x"] += bullet["dx"]
        bullet["y"] += bullet["dy"]

        if (
            bullet["x"] < 0 or bullet["x"] > WIDTH or
            bullet["y"] < 0 or bullet["y"] > HEIGHT
        ):
            bullets.remove(bullet)

    # Update zombies
    for zombie in zombies[:]:

        dx = player_x - zombie["x"]
        dy = player_y - zombie["y"]

        dist = math.hypot(dx, dy)

        if dist > 0:
            zombie["x"] += dx/dist * zombie["speed"]
            zombie["y"] += dy/dist * zombie["speed"]

        if dist < 25:
            player_health -= 0.1

        # Bullet collisions
        for bullet in bullets[:]:

            bdist = math.hypot(
                bullet["x"] - zombie["x"],
                bullet["y"] - zombie["y"]
            )

            if bdist < 20:

                zombie["health"] -= bullet["damage"]

                if bullet in bullets:
                    bullets.remove(bullet)

                if zombie["health"] <= 0:
                    zombies.remove(zombie)
                    score += 1
                    spawn_zombie()

                    if random.random() < 0.3:
                        spawn_juice()

                    break

    # Health Juice
    for juice in juices[:]:

        dist = math.hypot(
            player_x - juice["x"],
            player_y - juice["y"]
        )

        if dist < 25:
            player_health = min(100, player_health + 25)
            juices.remove(juice)

    # Draw
    screen.fill((30,120,30))

    # Bullets
    for bullet in bullets:
        pygame.draw.circle(
            screen,
            WHITE,
            (int(bullet["x"]), int(bullet["y"])),
            4
        )

    # Zombies
    for zombie in zombies:
        pygame.draw.circle(
            screen,
            RED,
            (int(zombie["x"]), int(zombie["y"])),
            20
        )

    # Health Juice
    for juice in juices:
        pygame.draw.rect(
            screen,
            BLUE,
            (juice["x"]-10, juice["y"]-10, 20, 20)
        )

    # Player
    pygame.draw.circle(
        screen,
        GREEN,
        (int(player_x), int(player_y)),
        20
    )

    # Health Bar
    pygame.draw.rect(screen, RED, (20,20,200,25))
    pygame.draw.rect(
        screen,
        GREEN,
        (20,20,int(player_health*2),25)
    )

    gun_text = font.render(
        f"Gun: {current_gun}",
        True,
        WHITE
    )

    score_text = font.render(
        f"Score: {score}",
        True,
        WHITE
    )

    screen.blit(gun_text, (20,60))
    screen.blit(score_text, (20,100))

    if player_health <= 0:
        game_over = font.render(
            "GAME OVER",
            True,
            WHITE
        )
        screen.blit(
            game_over,
            (WIDTH//2-100, HEIGHT//2)
        )
        pygame.display.flip()
        pygame.time.wait(3000)
        running = False

    pygame.display.flip()

pygame.quit()