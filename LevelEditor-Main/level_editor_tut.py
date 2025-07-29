import pygame
import button
import csv
import pickle
import os

pygame.init()

clock = pygame.time.Clock()
FPS = 60

# Game window settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 640
LOWER_MARGIN = 100
SIDE_MARGIN = 300

screen = pygame.display.set_mode((SCREEN_WIDTH + SIDE_MARGIN, SCREEN_HEIGHT + LOWER_MARGIN))
pygame.display.set_caption('Level Editor')

# Define game variables
ROWS = 16
MAX_COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 30
level = 0
current_tile = 0
scroll_left = False
scroll_right = False
scroll = 0
scroll_speed = 1


# Background selection: "original" or "new"
active_bg = "original"  # Default background

# -------------------------------
# Load images
# Original background layers
pine1_img = pygame.image.load('C:/Users/Rohit/Desktop/code/LevelEditor-main/img/Background/pine1.png').convert_alpha()
pine2_img = pygame.image.load('C:/Users/Rohit/Desktop/code/LevelEditor-main/img/Background/pine2.png').convert_alpha()
mountain_img = pygame.image.load('C:/Users/Rohit/Desktop/code/LevelEditor-main/img/Background/mountain.png').convert_alpha()
sky_img = pygame.image.load('C:/Users/Rohit/Desktop/code/LevelEditor-main/img/Background/sky_cloud.png').convert_alpha()

# New background images (1.png to 5.png)
new_bg_1 = pygame.image.load('C:/Users/Rohit/Desktop/Shooter-main/LevelEditor-main/1.png').convert_alpha()
new_bg_2 = pygame.image.load('C:/Users/Rohit/Desktop/Shooter-main/LevelEditor-main/2.png').convert_alpha()
new_bg_3 = pygame.image.load('C:/Users/Rohit/Desktop/Shooter-main/LevelEditor-main/3.png').convert_alpha()
new_bg_4 = pygame.image.load('C:/Users/Rohit/Desktop/Shooter-main/LevelEditor-main/4.png').convert_alpha()
new_bg_5 = pygame.image.load('C:/Users/Rohit/Desktop/Shooter-main/LevelEditor-main/5.png').convert_alpha()

# Load overlay image (for new background)
overlay_img = pygame.image.load('C:/Users/Rohit/Desktop/Shooter-main/LevelEditor-main/Overlay.png').convert_alpha()

# Save/Load button images
save_img = pygame.image.load('C:/Users/Rohit/Desktop/code/LevelEditor-main/img/save_btn.png').convert_alpha()
load_img = pygame.image.load('C:/Users/Rohit/Desktop/code/LevelEditor-main/img/load_btn.png').convert_alpha()

# Background toggle button image
switch_bg_img = pygame.image.load('C:/Users/Rohit/Desktop/code/LevelEditor-main/img/save_btn.png').convert_alpha()
switch_bg_button = button.Button(SCREEN_WIDTH // 2 + 400, SCREEN_HEIGHT + LOWER_MARGIN - 50, switch_bg_img, 1)

# Store tile images in a list
img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'C:/Users/Rohit/Desktop/Shooter-main/LevelEditor-main/img/tile/{x}.png').convert_alpha()
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)

# Define colours
GREEN = (144, 201, 120)
WHITE = (255, 255, 255)
RED = (200, 25, 25)

# Define font
font = pygame.font.SysFont('Futura', 30)

# Create an empty tile list for the world
world_data = []
for row in range(ROWS):
    r = [-1] * MAX_COLS
    world_data.append(r)

# Create ground
for tile in range(0, MAX_COLS):
    world_data[ROWS - 1][tile] = 0

# -------------------------------
# Functions

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def draw_bg():
    screen.fill(GREEN)
    if active_bg == "original":
        width = sky_img.get_width()
        for x in range(4):
            screen.blit(sky_img, ((x * width) - scroll * 0.5, 0))
            screen.blit(mountain_img, ((x * mountain_img.get_width()) - scroll * 0.6, SCREEN_HEIGHT - mountain_img.get_height() - 300))
            screen.blit(pine1_img, ((x * pine1_img.get_width()) - scroll * 0.7, SCREEN_HEIGHT - pine1_img.get_height() - 150))
            screen.blit(pine2_img, ((x * pine2_img.get_width()) - scroll * 0.8, SCREEN_HEIGHT - pine2_img.get_height()))
    elif active_bg == "new":
        num_tiles = (MAX_COLS * TILE_SIZE) // SCREEN_WIDTH + 2
        
        # Base layer: new_bg_1
        base_layer = pygame.transform.scale(new_bg_1, (SCREEN_WIDTH, SCREEN_HEIGHT))
        for i in range(num_tiles):
            screen.blit(base_layer, (i * SCREEN_WIDTH - scroll * 0.5, 0))
        
        # Background overlays: new_bg_2 and new_bg_3
        layer2 = pygame.transform.scale(new_bg_2, (SCREEN_WIDTH, SCREEN_HEIGHT))
        for i in range(num_tiles):
            screen.blit(layer2, (i * SCREEN_WIDTH - scroll * 0.55, 0))
        
        layer3 = pygame.transform.scale(new_bg_3, (SCREEN_WIDTH, SCREEN_HEIGHT))
        for i in range(num_tiles):
            screen.blit(layer3, (i * SCREEN_WIDTH - scroll * 0.6, 0))
        
        # Foreground overlays: new_bg_4 and new_bg_5
        layer4 = pygame.transform.scale(new_bg_4, (SCREEN_WIDTH, SCREEN_HEIGHT))
        for i in range(num_tiles):
            screen.blit(layer4, (i * SCREEN_WIDTH - scroll * 0.8, 0))
        
        layer5 = pygame.transform.scale(new_bg_5, (SCREEN_WIDTH, SCREEN_HEIGHT))
        for i in range(num_tiles):
            screen.blit(layer5, (i * SCREEN_WIDTH - scroll * 0.9, 0))
        
        # Overlay: draw the overlay image on top.
        # Scale overlay to screen size and set semi-transparency.
        overlay_scaled = pygame.transform.scale(overlay_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay_scaled.set_alpha(128)  # Adjust alpha (0-255) as needed.
        screen.blit(overlay_scaled, (0, 0))

def draw_grid():
    for c in range(MAX_COLS + 1):
        pygame.draw.line(screen, WHITE, (c * TILE_SIZE - scroll, 0), (c * TILE_SIZE - scroll, SCREEN_HEIGHT))
    for r in range(ROWS + 1):
        pygame.draw.line(screen, WHITE, (0, r * TILE_SIZE), (SCREEN_WIDTH, r * TILE_SIZE))

def draw_world():
    for y, row in enumerate(world_data):
        for x, tile in enumerate(row):
            if tile >= 0:
                screen.blit(img_list[tile], (x * TILE_SIZE - scroll, y * TILE_SIZE))

def save_level():
    # Save world_data and background setting to CSV.
    # The first row is a header containing the background setting.
    with open(f'level{level}_data.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(["background", active_bg])
        for row in world_data:
            writer.writerow(row)

def load_level():
    global active_bg, world_data, scroll
    scroll = 0
    with open(f'level{level}_data.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        rows = list(reader)
        if rows[0][0].strip().lower() == "background":
            active_bg = rows[0][1].strip().lower()
            tile_rows = rows[1:]
        else:
            tile_rows = rows
        world_data = []
        for row in tile_rows:
            world_data.append([int(tile) for tile in row])

# -------------------------------
# Create buttons

save_button = button.Button(SCREEN_WIDTH // 2, SCREEN_HEIGHT + LOWER_MARGIN - 50, save_img, 1)
load_button = button.Button(SCREEN_WIDTH // 2 + 200, SCREEN_HEIGHT + LOWER_MARGIN - 50, load_img, 1)

button_list = []
button_col = 0
button_row = 0
for i in range(len(img_list)):
    tile_button = button.Button(SCREEN_WIDTH + (75 * button_col) + 50, 75 * button_row + 50, img_list[i], 1)
    button_list.append(tile_button)
    button_col += 1
    if button_col == 3:
        button_row += 1
        button_col = 0

# -------------------------------
# Main loop

run = True
while run:
    clock.tick(FPS)
    
    draw_bg()
    draw_grid()
    draw_world()
    
    draw_text(f'Level: {level}', font, WHITE, 10, SCREEN_HEIGHT + LOWER_MARGIN - 90)
    draw_text('Press UP or DOWN to change level', font, WHITE, 10, SCREEN_HEIGHT + LOWER_MARGIN - 60)
    
    if save_button.draw(screen):
        save_level()
    if load_button.draw(screen):
        load_level()
    
    pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH, 0, SIDE_MARGIN, SCREEN_HEIGHT))
    for button_count, tile_button in enumerate(button_list):
        if tile_button.draw(screen):
            current_tile = button_count
    pygame.draw.rect(screen, RED, button_list[current_tile].rect, 3)
    
    if switch_bg_button.draw(screen):
        active_bg = "original" if active_bg == "new" else "new"
    
    if scroll_left and scroll > 0:
        scroll -= 5 * scroll_speed
    if scroll_right and scroll < (MAX_COLS * TILE_SIZE) - SCREEN_WIDTH:
        scroll += 5 * scroll_speed
    
    pos = pygame.mouse.get_pos()
    x = (pos[0] + scroll) // TILE_SIZE
    y = pos[1] // TILE_SIZE
    if pos[0] < SCREEN_WIDTH and pos[1] < SCREEN_HEIGHT:
        if 0 <= y < len(world_data) and 0 <= x < len(world_data[y]):
            if pygame.mouse.get_pressed()[0] == 1:
                if world_data[y][x] != current_tile:
                    world_data[y][x] = current_tile
        if pygame.mouse.get_pressed()[2] == 1:
            world_data[y][x] = -1

    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                level += 1
            if event.key == pygame.K_DOWN and level > 0:
                level -= 1
            if event.key == pygame.K_LEFT:
                scroll_left = True
            if event.key == pygame.K_RIGHT:
                scroll_right = True
            if event.key == pygame.K_RSHIFT:
                scroll_speed = 5
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                scroll_left = False
            if event.key == pygame.K_RIGHT:
                scroll_right = False
            if event.key == pygame.K_RSHIFT:
                scroll_speed = 1
    
    pygame.display.update()

pygame.quit()
