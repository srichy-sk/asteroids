import pygame, sys, random
pygame.init()

# -------------------------------------
# WINDOW
# -------------------------------------
WIDTH, HEIGHT = 700, 700
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Breakout Ultimate")
clock = pygame.time.Clock()

# -------------------------------------
# COLORS                                          
# -------------------------------------
WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,80,80)
ORANGE = (255,150,70)
YELLOW = (245,245,70)
GREEN = (80,255,80)
BLUE = (80,150,255)
PURPLE = (180,80,255)

ROW_COLORS = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE]



# -------------------------------------
# FONT
# -------------------------------------
font = pygame.font.SysFont("Comic Sans MS", 30)
big_font = pygame.font.SysFont("Comic Sans MS", 55)

# -------------------------------------
# PADDLE
# -------------------------------------
paddle = pygame.Rect(WIDTH//2 - 60, HEIGHT - 40, 120, 15)
paddle_speed = 16
paddle_normal_width = 120

# -------------------------------------
# BALL
# -------------------------------------
ball = pygame.Rect(WIDTH//2 - 10, HEIGHT//2, 20, 20)
ball_dx, ball_dy = 10, -10
ball_speed_base = 5

# -------------------------------------
# BRICKS + LEVELS
# -------------------------------------
def generate_bricks(level):
    bricks = []
    rows = min(6 + level, 10)
    cols = 10
    bw = WIDTH // cols
    bh = 30

    for r in range(rows):
        for c in range(cols):
            rect = pygame.Rect(c * bw, r * bh + 50, bw - 2, bh - 2)
            bricks.append((rect, ROW_COLORS[r % len(ROW_COLORS)]))
    return bricks

level = 1
bricks = generate_bricks(level)

# -------------------------------------
# PARTICLES
# -------------------------------------
particles = []

def spawn_particles(x, y, color):
    for i in range(10):
        particles.append([x, y, random.randint(-3, 3), random.randint(-3, 3), color, 20])

def update_particles():
    for p in particles[:]:
        p[0] += p[2]
        p[1] += p[3]
        p[5] -= 1
        if p[5] <= 0:
            particles.remove(p)
        else:
            pygame.draw.circle(win, p[4], (int(p[0]), int(p[1])), max(1, p[5]//4))

# -------------------------------------
# POWER-UPS
# -------------------------------------
powerups = []
power_types = ["big", "slow", "life"]

def spawn_powerup(x, y):
    if random.random() < 0.2:
        t = random.choice(power_types)
        powerups.append([pygame.Rect(x, y, 25, 25), t])

def apply_powerup(t):
    global paddle, ball_dx, ball_dy, ball_speed_base, lives

    if t == "big":
        paddle.width = paddle_normal_width * 1.5
    elif t == "Fast":
        ball_dx *= 2
        ball_dy *= 2
    elif t == "life":
        lives += 1

# -------------------------------------
# GAME STATE
# -------------------------------------
score = 0
lives = 3
game_state = "menu"   # menu, playing, gameover

# -------------------------------------
# DRAW TEXT
# -------------------------------------
def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    win.blit(img, (x, y))

# -------------------------------------
# MAIN GAME LOOP
# -------------------------------------
running = True
while running:
    clock.tick(60)
    win.fill(BLACK) 

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # ================================
    # MENU
    # ================================
    if game_state == "menu":
        draw_text("BREAKOUT ULTIMATE", big_font, WHITE, 60, 200)
        draw_text("Press SPACE to Start", font, WHITE, 150, 330)
        if pygame.key.get_pressed()[pygame.K_SPACE]:
            game_state = "playing"
        pygame.display.update()
        continue

    # ================================
    # GAME OVER
    # ================================
    if game_state == "gameover":
        draw_text("GAME OVER", big_font, RED, 150, 250)
        draw_text(f"Final Score: {score}", font, WHITE, 210, 330)
        draw_text("Press SPACE to Restart", font, WHITE, 150, 380)
        if pygame.key.get_pressed()[pygame.K_SPACE]:
            # reset everything
            paddle = pygame.Rect(WIDTH//2 - 60, HEIGHT - 40, 120, 15)
            ball.x, ball.y = WIDTH//2, HEIGHT//2
            ball_dx, ball_dy = 10, -10
            score = 0
            lives = 3
            level = 1
            bricks = generate_bricks(level)
            powerups = []
            particles = []
            game_state = "playing"
        pygame.display.update()
        continue

    # ================================
    # GAMEPLAY
    # ================================
    keys = pygame.key.get_pressed()

    # Paddle movement
    if keys[pygame.K_LEFT] and paddle.left > 0:
        paddle.x -= paddle_speed
    if keys[pygame.K_RIGHT] and paddle.right < WIDTH:
        paddle.x += paddle_speed

    # Move ball
    ball.x += ball_dx
    ball.y += ball_dy

    # Wall bounce
    if ball.left <= 0 or ball.right >= WIDTH:
        ball_dx *= -1
    if ball.top <= 0:
        ball_dy *= -1

    # Ball falls
    if ball.bottom >= HEIGHT:
        lives -= 1
        ball.x, ball.y = WIDTH//2, HEIGHT//2
        paddle.width = paddle_normal_width
        ball_dx, ball_dy = 10, -10
        if lives <= 0:
            game_state = "gameover"

    # Paddle bounce with angle change
    if ball.colliderect(paddle):
        offset = (ball.centerx - paddle.centerx) / (paddle.width // 2)
        ball_dx = offset * 10
        ball_dy = -abs(ball_dy)

    # Brick collision
    for b, color in bricks[:]:
        if ball.colliderect(b):
            spawn_particles(ball.centerx, ball.centery, color)
            bricks.remove((b, color))
            score += 10
            ball_dy *= -1
            spawn_powerup(b.x, b.y)
            break

    # Level up
    if len(bricks) == 0:
        level += 1
        bricks = generate_bricks(level)
        ball.x, ball.y = WIDTH//2, HEIGHT//2

    # Powerups falling
    for p in powerups[:]:
        rect, t = p
        rect.y += 4

        if rect.colliderect(paddle):
            apply_powerup(t)
            powerups.remove(p)
        elif rect.top > HEIGHT:
            powerups.remove(p)

        # Draw powerups
        color = BLUE if t == "big" else YELLOW if t == "slow" else GREEN
        pygame.draw.rect(win, color, rect)

    # Draw paddle, ball, bricks
    pygame.draw.rect(win, BLUE, paddle)
    pygame.draw.ellipse(win, WHITE, ball)

    for b, color in bricks:
        pygame.draw.rect(win, color, b)

    # Draw particles
    update_particles()

    # HUD
    draw_text(f"Score: {score}", font, WHITE, 20, HEIGHT - 40)
    draw_text(f"Lives: {lives}", font, WHITE, 480, HEIGHT - 40)
    draw_text(f"Level: {level}", font, WHITE, 250, HEIGHT - 40)

    pygame.display.update()

pygame.quit()
