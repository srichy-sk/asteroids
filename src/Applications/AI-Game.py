import pygame, random
pygame.init()

w, h = 600, 600
win = pygame.display.set_mode((w, h))
clock = pygame.time.Clock()

player = pygame.Rect(w//2 - 15, h - 40, 30, 30)

enemy = pygame.Rect(random.randint(0, w-30), 0, 30, 30)

class Bullet:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 4, 10)
        self.speed = -8  # goes upward

    def move(self):
        self.rect.y += self.speed

    def draw(self, surf):
        pygame.draw.rect(surf, (0, 255, 225), self.rect)

bullets = []
health = 3
running = True

while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player.x -= 10
    if keys[pygame.K_RIGHT]:
        player.x += 10

    # --- KEEP PLAYER INSIDE THE SCREEN ---
    if player.x < 0:
        player.x = 0
    if player.x > w - player.width:
        player.x = w - player.width

    # Shoot bullets
    if keys[pygame.K_SPACE] and len(bullets) < 5:
        bullets.append(Bullet(player.x + 13, player.y))

    if health == 1:    
        if keys[pygame.K_b] and len(bullets) < 10:
            bullets.append(Bullet(player.x + 13, player.y))

    # Move enemy
    enemy.y += 20
    if enemy.y > h:
        enemy.x = random.randint(0, w - 30)
        enemy.y = 0

    # PLAYER COLLIDES WITH ENEMY
    if player.colliderect(enemy):
        health -= 1
        enemy.x = random.randint(0, w - 30)
        enemy.y = 0
        if health == 0:
            running = False



    # Move bullets & check collision with enemy
    for b in bullets[:]:
        b.move()
        if b.rect.y < -20:
            bullets.remove(b)
        elif b.rect.colliderect(enemy):
            bullets.remove(b)
            enemy.x = random.randint(0, w - 30)
            enemy.y = 0

    # DRAW
    win.fill((0, 0, 0))
    pygame.draw.rect(win, (0, 255, 0), player)
    pygame.draw.rect(win, (255, 0, 0), enemy)

    for b in bullets:
        b.draw(win)

    # HEALTH TEXT
    font = pygame.font.SysFont(None, 36)
    health_text = font.render(f'Health: {health}', True, (255, 255, 255))
    win.blit(health_text, (10, 10))

    pygame.display.update()
    clock.tick(60)

pygame.quit()
