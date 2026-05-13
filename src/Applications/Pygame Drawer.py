import pygame
import random

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Drawing Tool")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 22)

running = True
active_box = None
selected_box = None
draw_mode = False

boxes = []
draw_points = []

# Buttons
add_button = pygame.Rect(20, 20, 60, 35)
delete_button = pygame.Rect(85, 20, 70, 35)
draw_button = pygame.Rect(160, 20, 70, 35)

# Color buttons
color_buttons = {
    "red": (pygame.Rect(250, 20, 45, 35), (255, 0, 0)),
    "green": (pygame.Rect(300, 20, 45, 35), (0, 255, 0)),
    "blue": (pygame.Rect(350, 20, 45, 35), (0, 0, 255)),
    "yellow": (pygame.Rect(400, 20, 45, 35), (255, 255, 0)),
    "purple": (pygame.Rect(450, 20, 45, 35), (128, 0, 128)),
    "light blue": (pygame.Rect(500, 20, 45, 35), (173, 216, 230)),
    "dark green": (pygame.Rect(550, 20, 45, 35), (0, 100, 0)),
    "brown": (pygame.Rect(600, 20, 45, 35), (139, 69, 19))
}

selected_color = (255, 255, 0)

while running:
    screen.fill("#006eff")

    # Draw buttons
    pygame.draw.rect(screen, "white", add_button)
    screen.blit(font.render("Add", True, "black"), (30, 30))

    pygame.draw.rect(screen, "white", delete_button)
    screen.blit(font.render("Delete", True, "black"), (95, 30))

    # Draw mode button
    button_color = "lime" if draw_mode else "white"
    pygame.draw.rect(screen, button_color, draw_button)
    screen.blit(font.render("Draw", True, "black"), (175, 30))

    # Draw color buttons
    for name, (rect, color) in color_buttons.items():
        pygame.draw.rect(screen, color, rect)

        if color == selected_color:
            pygame.draw.rect(screen, "white", rect, 3)

    # Draw freehand lines
    if len(draw_points) > 1:
        pygame.draw.lines(screen, selected_color, False, draw_points, 3)

    # Draw boxes
    for i, box in enumerate(boxes):
        pygame.draw.rect(screen, box["color"], box["rect"])

        if i == selected_box:
            pygame.draw.rect(screen, "white", box["rect"], 3)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:

                # Toggle draw mode
                if draw_button.collidepoint(event.pos):
                    draw_mode = not draw_mode

                elif not draw_mode:

                    # Add box
                    if add_button.collidepoint(event.pos):
                        boxes.append({
                            "rect": pygame.Rect(
                                random.randint(50, 700),
                                random.randint(100, 500),
                                50,
                                50
                            ),
                            "color": selected_color
                        })

                    # Delete selected box
                    if delete_button.collidepoint(event.pos):
                        if selected_box is not None:
                            boxes.pop(selected_box)
                            selected_box = None

                    # Select color
                    for name, (rect, color) in color_buttons.items():
                        if rect.collidepoint(event.pos):
                            selected_color = color

                    # Select box
                    for num, box in enumerate(boxes):
                        if box["rect"].collidepoint(event.pos):
                            active_box = num
                            selected_box = num

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                active_box = None

        if event.type == pygame.MOUSEMOTION:

            if draw_mode and pygame.mouse.get_pressed()[0]:
                draw_points.append(event.pos)

            elif active_box is not None:
                boxes[active_box]["rect"].move_ip(event.rel)

    pygame.display.update()
    clock.tick(60)

pygame.quit()