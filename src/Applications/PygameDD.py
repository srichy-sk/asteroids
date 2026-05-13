import pygame
import random

pygame.init()


WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Drawing Tool")

clock = pygame.time.Clock()
running = True

active_box = None

boxes = []
for i in range(15):
    x = random.randint(50, 700)
    y = random.randint(50, 350)
    box = pygame.Rect(x, y, 50, 50)
    boxes.append(box)

while running:

    screen.fill("#006eff")

    for box in boxes:
        pygame.draw.rect(screen, "#ffe608", box)

    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for num, box in enumerate(boxes):
                    if box.collidepoint(event.pos):
                        active_box = num

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                active_box = None



        if event.type == pygame.MOUSEMOTION:
            if active_box != None:
                boxes[active_box].move_ip(event.rel)


        if event.type == pygame.QUIT:
            running = False
        

    pygame.display.update()
    clock.tick(60)

pygame.quit()
