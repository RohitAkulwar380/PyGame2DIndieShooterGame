import pygame
from pygame import mixer
import os
import random
import csv

import pygame.mixer
import pygame.time
import button

# Initialize mixer and pygame
try:
    mixer.init()
except Exception as e:
    print("Error initializing mixer:", e)
pygame.init()

# Screen setup
SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Shooter')

clock = pygame.time.Clock()
FPS = 60

# Game variables
GRAVITY = 0.75
SCROLL_THRESH = 200
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 30  
MAX_LEVELS = 10
screen_scroll = 0
bg_scroll = 0
level = 1
start_game = False
start_intro = False
death_sound_played = False
victory_time = None
win_sound_played = False

# Victory variables
victory = False
boss_death_time = None  
win_sound_start_time = None  

# Player action variables
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False

# Global background setting variable.
active_bg = "original"  # default

# Helper functions for safe loading
def load_sound(path, volume=0.05):
    try:
        sound = pygame.mixer.Sound(path)
        sound.set_volume(volume)
        print(f"Loaded sound: {path}")
        return sound
    except Exception as e:
        print(f"Error loading sound {path}: {e}")
        return None

def load_image(path, convert_alpha=True):
    try:
        img = pygame.image.load(path)
        if convert_alpha:
            img = img.convert_alpha()
        else:
            img = img.convert()
        print(f"Loaded image: {path}")
        return img
    except Exception as e:
        print(f"Error loading image {path}: {e}")
        return pygame.Surface((50, 50))

# Set up absolute paths
BASE_DIR = "C:/Users/Rohit/Desktop/Shooter-main"  # Note: ensure folder name matches exactly (case-sensitive)
AUDIO_DIR = os.path.join(BASE_DIR, "audio")
IMG_DIR = os.path.join(BASE_DIR, "img")

# Load sounds
jump_fx    = load_sound(os.path.join(AUDIO_DIR, "jump.wav"), 0.5)
shot_fx    = load_sound(os.path.join(AUDIO_DIR, "shot.wav"), 0.5)
grenade_fx = load_sound(os.path.join(AUDIO_DIR, "grenade.wav"), 0.5)
death_fx   = load_sound(os.path.join(AUDIO_DIR, "death.mp3"), 0.5)
win_fx     = load_sound(os.path.join('C:/Users/Rohit/Desktop/Shooter-main/audio/Stage Win (Super Mario) - Sound Effect HD.mp3'), 0.5)

# Load button images
start_img   = load_image(os.path.join(IMG_DIR, "start_btn.png"))
exit_img    = load_image(os.path.join(IMG_DIR, "exit_btn.png"))
restart_img = load_image(os.path.join(IMG_DIR, "restart_btn.png"))
continue_img = load_image(os.path.join(IMG_DIR, "continue_btn.png"))
continue_button = button.Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 50, continue_img, 2)
# Load the continue button image and scale it to 150x50 pixels.
continue_img = load_image(os.path.join(IMG_DIR, "continue_btn.png"))
scaled_continue_img = pygame.transform.scale(continue_img, (150, 50))
continue_button = button.Button((SCREEN_WIDTH - 150) // 2, (SCREEN_HEIGHT - 50) // 2, scaled_continue_img, 2)
    
# Victory button (no longer used; we use continue_button instead)
victory_restart_button = button.Button(SCREEN_WIDTH//2 - 160, SCREEN_HEIGHT//2 + 100, restart_img, 2)

# Load background images
pine1_img    = load_image(os.path.join(IMG_DIR, "Background", "pine1.png"))
pine2_img    = load_image(os.path.join(IMG_DIR, "Background", "pine2.png"))
mountain_img = load_image(os.path.join(IMG_DIR, "Background", "mountain.png"))
sky_img      = load_image(os.path.join(IMG_DIR, "Background", "sky_cloud.png"))

# Load new background images from LevelEditor-main folder
new_bg_1 = load_image(os.path.join(BASE_DIR, "LevelEditor-main", "1.png"))
new_bg_2 = load_image(os.path.join(BASE_DIR, "LevelEditor-main", "2.png"))
new_bg_3 = load_image(os.path.join(BASE_DIR, "LevelEditor-main", "3.png"))
new_bg_4 = load_image(os.path.join(BASE_DIR, "LevelEditor-main", "4.png"))
new_bg_5 = load_image(os.path.join(BASE_DIR, "LevelEditor-main", "5.png"))

# Load tile images
img_list = []
for x in range(TILE_TYPES):
    path = os.path.join(BASE_DIR, "LevelEditor-main", "img", "tile", f"{x}.png")
    print("Loading tile from:", path)
    if not os.path.exists(path):
        print("ERROR: File not found!")
    img = load_image(path)
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)

bullet_img  = load_image(os.path.join(IMG_DIR, "icons", "bullet.png"))
grenade_img = load_image(os.path.join(IMG_DIR, "icons", "grenade.png"))

health_box_img  = load_image(os.path.join(IMG_DIR, "icons", "health_box.png"))
ammo_box_img    = load_image(os.path.join(IMG_DIR, "icons", "ammo_box.png"))
grenade_box_img = load_image(os.path.join(IMG_DIR, "icons", "grenade_box.png"))
item_boxes = {
    'Health': health_box_img,
    'Ammo': ammo_box_img,
    'Grenade': grenade_box_img
}

# Define colours and fonts
BG = (144, 201, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
PINK = (235, 65, 54)
font = pygame.font.SysFont('Futura', 30)
victory_font = pygame.font.Font("PressStart2P-Regular.ttf", 30)

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def draw_bg():
    screen.fill(BG)
    if active_bg == "new":
        num_tiles = (COLS * TILE_SIZE) // SCREEN_WIDTH + 2
        base_layer = pygame.transform.scale(new_bg_1, (SCREEN_WIDTH, SCREEN_HEIGHT))
        for i in range(num_tiles):
            screen.blit(base_layer, (i * SCREEN_WIDTH - bg_scroll * 0.5, 0))
        layer2 = pygame.transform.scale(new_bg_2, (SCREEN_WIDTH, SCREEN_HEIGHT))
        for i in range(num_tiles):
            screen.blit(layer2, (i * SCREEN_WIDTH - bg_scroll * 0.55, 0))
        layer3 = pygame.transform.scale(new_bg_3, (SCREEN_WIDTH, SCREEN_HEIGHT))
        for i in range(num_tiles):
            screen.blit(layer3, (i * SCREEN_WIDTH - bg_scroll * 0.6, 0))
        layer4 = pygame.transform.scale(new_bg_4, (SCREEN_WIDTH, SCREEN_HEIGHT))
        for i in range(num_tiles):
            screen.blit(layer4, (i * SCREEN_WIDTH - bg_scroll * 0.8, 0))
        layer5 = pygame.transform.scale(new_bg_5, (SCREEN_WIDTH, SCREEN_HEIGHT))
        for i in range(num_tiles):
            screen.blit(layer5, (i * SCREEN_WIDTH - bg_scroll * 0.9, 0))
    else:
        width = sky_img.get_width()
        for x in range(5):
            screen.blit(sky_img, ((x * width) - bg_scroll * 0.5, 0))
            screen.blit(mountain_img, ((x * width) - bg_scroll * 0.6, SCREEN_HEIGHT - mountain_img.get_height() - 300))
            screen.blit(pine1_img, ((x * width) - bg_scroll * 0.7, SCREEN_HEIGHT - pine1_img.get_height() - 150))
            screen.blit(pine2_img, ((x * width) - bg_scroll * 0.8, SCREEN_HEIGHT - pine2_img.get_height()))

def reset_level():
    enemy_group.empty()
    bullet_group.empty()
    grenade_group.empty()
    explosion_group.empty()
    item_box_group.empty()
    decoration_group.empty()
    water_group.empty()
    exit_group.empty()
    data = []
    for row in range(ROWS):
        r = [-1] * COLS
        data.append(r)
    return data

def play_music_for_level(level, music_path_lv1_2, music_path_lv3, music_path_lv4,):
    try:
        if level in [1, 2]:
            pygame.mixer.music.load(music_path_lv1_2)
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
        if level in [4, 5]:
            pygame.mixer.music.load(music_path_lv4)
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
        elif level == 3 or level == 6:
            pygame.mixer.music.load(music_path_lv3)
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
        print(f"Playing music for level {level}")
    except Exception as e:
        print("Error playing music:", e)

# ScreenFade class for fade/slide effects.
class ScreenFade():
    def __init__(self, direction, colour, speed):
        self.direction = direction  # 1: horizontal fade; 2: vertical slide-down fade
        self.colour = colour
        self.speed = speed
        self.fade_counter = 0

    def fade(self):
        fade_complete = False
        self.fade_counter += self.speed
        if self.direction == 1:
            pygame.draw.rect(screen, self.colour, (0 - self.fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.colour, (SCREEN_WIDTH // 2 + self.fade_counter, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        elif self.direction == 2:
            pygame.draw.rect(screen, self.colour, (0, 0 - self.fade_counter, SCREEN_WIDTH, self.fade_counter))
        if self.fade_counter >= SCREEN_HEIGHT:
            fade_complete = True
        return fade_complete

# Create fade objects
intro_fade = ScreenFade(1, (0,0,0), 4)
death_fade = ScreenFade(2, PINK, 4)
restart_fade = ScreenFade(2, PINK, 4)

# Boss class
class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y, scale, speed, ammo, grenades, boss_type="boss"):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = 'boss'
        self.boss_type = boss_type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.grenades = grenades
        self.health = 500
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        boss_anim_types = ['idle', 'run', 'shoot', 'throw', 'death']
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        self.grenade_spawned = False

        # Use the boss_type parameter to choose the sprite folder.
        base_path = os.path.join(IMG_DIR, boss_type)
        for anim in boss_anim_types:
            temp_list = []
            anim_path = os.path.join(base_path, anim)
            try:
                file_list = [f for f in os.listdir(anim_path) if f.endswith('.png')]
                file_list.sort(key=lambda fname: int(os.path.splitext(fname)[0]))
            except Exception as e:
                print(f"Error accessing folder {anim_path}: {e}")
                file_list = []
            for f_name in file_list:
                full_path = os.path.join(anim_path, f_name)
                try:
                    img = load_image(full_path)
                except Exception as e:
                    print(f"Error loading {full_path}: {e}")
                    continue
                # Scale the image by the given factor.
                w = int(img.get_width() * scale)
                h = int(img.get_height() * scale)
                img = pygame.transform.scale(img, (w, h))
                temp_list.append(img)
            self.animation_list.append(temp_list)
            print(f"{boss_type}/{anim}: {len(temp_list)} frames loaded")
        # Set the initial image.
        if self.animation_list[self.action]:
            self.image = self.animation_list[self.action][self.frame_index]
        else:
            self.image = pygame.Surface((50,50))
            self.image.fill((255,0,0))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()


    def update(self):
        print(f"[DEBUG] Updating boss: {self.boss_type}")
        print(f"[RENDER TEST] {self.boss_type} rect: {self.rect.topleft}")
        if not self.alive:
            self.update_animation()
            return
        self.update_animation()
        self.check_alive()
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right):
        dx = 0
        dy = 0
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom

        self.rect.x += dx
        self.rect.y += dy
        return 0

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.update_action(2)
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction),
                            self.rect.centery, self.direction)
            bullet_group.add(bullet)
            self.ammo -= 1
            if shot_fx:
                shot_fx.play()

    def update_animation(self):
        ANIMATION_COOLDOWN = 100

        # Ensure action is valid
        if self.action >= len(self.animation_list) or not self.animation_list[self.action]:
            print(f"[WARNING] {self.boss_type} is in invalid action {self.action}. Resetting to idle.")
            self.update_action(0)
            return

        frames = self.animation_list[self.action]

        if self.frame_index >= len(frames):
            self.frame_index = 0

        self.image = frames[self.frame_index]
        print(f"[DEBUG] {self.boss_type} animation {self.action}, frame {self.frame_index}, image size: {self.image.get_size()}")

        # Handle grenade logic
        if self.action == 3 and self.frame_index == 4 and not self.grenade_spawned:
            grenade_obj = Grenade(self.rect.centerx, self.rect.centery, self.direction)
            grenade_group.add(grenade_obj)
            self.grenade_spawned = True

        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

        if self.frame_index >= len(frames):
            if self.action == 4:
                self.frame_index = len(frames) - 1
            elif self.action == 3:
                self.grenade_spawned = False
                self.update_action(0)
            else:
                self.frame_index = 0

        self.image.set_alpha(255)


    def update_action(self, new_action):
        if self.boss_type == "boss2" and new_action == 3:
            print(f"[BLOCKED] Boss2 tried to use throw — forcing idle.")
            new_action = 0

        if new_action != self.action:
            print(f"[{self.boss_type}] Action change: {self.action} → {new_action}")
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()
            if self.action != 3:
                self.grenade_spawned = False
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()
            if self.action != 3:
                self.grenade_spawned = False

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(4)

    def ai(self):
        if self.action == 3:
            return
        if not self.alive:
            return
        if player.alive:
            if random.randint(1, 100) == 1 and self.action != 3:
                self.update_action(3)
            else:
                distance = player.rect.centerx - self.rect.centerx
                if abs(distance) > 100:
                    self.update_action(1)
                    if distance > 0:
                        self.move(False, True)
                    else:
                        self.move(True, False)
                else:
                    self.update_action(2)
                    self.shoot()
        if self.boss_type != "boss2" and random.randint(1, 100) == 1 and self.action != 3:
            self.update_action(3)


    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.grenades = grenades
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20)
        self.idling = False
        self.idling_counter = 0
        animation_types = ['Idle', 'Run', 'Jump', 'Death']
        for animation in animation_types:
            temp_list = []
            anim_path = os.path.join(BASE_DIR, "img", self.char_type, animation)
            try:
                num_of_frames = len(os.listdir(anim_path))
                print(f"Found {num_of_frames} frames for {self.char_type} {animation}")
            except Exception as e:
                print(f"Error accessing folder {anim_path}: {e}")
                num_of_frames = 0
            for i in range(num_of_frames):
                frame_path = os.path.join(anim_path, f"{i}.png")
                try:
                    img = load_image(frame_path)
                except Exception as e:
                    print(f"Error loading {frame_path}: {e}")
                    continue
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)
        if self.animation_list[self.action]:
            self.image = self.animation_list[self.action][self.frame_index]
        else:
            self.image = pygame.Surface((50,50))
            self.image.fill((255,0,0))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.update_animation()
        self.check_alive()
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right):
        screen_scroll = 0
        dx = 0
        dy = 0
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1
        if self.jump and not self.in_air:
            self.vel_y = -11
            self.jump = False
            self.in_air = True
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
                if self.char_type == 'enemy':
                    self.direction *= -1
                    self.move_counter = 0
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0
        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_complete = True
        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0
        if self.char_type == 'player':
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0
        self.rect.x += dx
        self.rect.y += dy
        if self.char_type == 'player' and level != 3:
            if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (world.level_length * TILE_SIZE) - SCREEN_WIDTH) or \
               (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx
        if level == 3 or level == 6:
            screen_scroll = 0
        return screen_scroll, level_complete

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction),
                            self.rect.centery, self.direction)
            bullet_group.add(bullet)
            self.ammo -= 1
            if shot_fx:
                shot_fx.play()

    def ai(self):
        if self.alive and player.alive:
            if not self.idling and random.randint(1, 200) == 1:
                self.update_action(0)
                self.idling = True
                self.idling_counter = 50
            if self.vision.colliderect(player.rect):
                self.update_action(0)
                self.shoot()
            else:
                if not self.idling:
                    ai_moving_right = True if self.direction == 1 else False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)
                    self.move_counter += 1
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)
                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False
        self.rect.x += screen_scroll

    def update_animation(self):
        ANIMATION_COOLDOWN = 100
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

class World():
    def __init__(self):
        self.obstacle_list = []
    def process_data(self, data):
        self.level_length = len(data[0])
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    # Always define tile_data for any valid tile.
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile <= 8:
                        self.obstacle_list.append(tile_data)
                    elif tile >= 9 and tile <= 10:
                        water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
                        water_group.add(water)
                    elif tile >= 11 and tile <= 14:
                        decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile == 15:
                        player = Soldier('player', x * TILE_SIZE, y * TILE_SIZE, 1.65, 5, 20, 5)
                        health_bar = HealthBar(10, 10, player.health, player.health)
                    elif tile == 16:
                        enemy = Soldier('enemy', x * TILE_SIZE, y * TILE_SIZE, 1.65, 2, 20, 0)
                        enemy_group.add(enemy)
                    elif tile == 17:
                        item_box = ItemBox('Ammo', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 18:
                        item_box = ItemBox('Grenade', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 19:
                        item_box = ItemBox('Health', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 20:
                        exit_obj = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
                        exit_group.add(exit_obj)
                    elif tile == 21:
                        # Boss spawn
                        boss = Boss(x * TILE_SIZE, y * TILE_SIZE, 1.0, 2, 150, 5, boss_type="boss")
                        boss.rect.bottom = y * TILE_SIZE + TILE_SIZE
                        enemy_group.add(boss)
                        print("Boss Spawned at:", boss.rect.topleft)
                    elif tile == 29:
                        boss = Boss(x * TILE_SIZE, y * TILE_SIZE, 1.0, 2, 150, 5, boss_type="boss2")
                        boss.rect.bottom = y * TILE_SIZE + TILE_SIZE
                        enemy_group.add(boss)
                    elif tile > 21:
                        # For any new tile indices above 21, treat them as obstacles.
                        self.obstacle_list.append(tile_data)
        return player, health_bar

    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])

class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
    def update(self):
        self.rect.x += screen_scroll

class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
    def update(self):
        self.rect.x += screen_scroll

class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
    def update(self):
        self.rect.x += screen_scroll

class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
    def update(self):
        self.rect.x += screen_scroll
        if pygame.sprite.collide_rect(self, player):
            if self.item_type == 'Health':
                player.health += 25
                if player.health > player.max_health:
                    player.health = player.max_health
            elif self.item_type == 'Ammo':
                player.ammo += 15
            elif self.item_type == 'Grenade':
                player.grenades += 3
            self.kill()

class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health
    def draw(self, health):
        self.health = health
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
    def update(self):
        self.rect.x += (self.direction * self.speed) + screen_scroll
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 5
                self.kill()
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -= 25
                    self.kill()

class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -11
        self.speed = 10
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.direction = direction
    def update(self):
        self.vel_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.vel_y
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                self.direction *= -1
                dx = self.direction * self.speed
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                self.speed = 0
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    dy = tile[1].top - self.rect.bottom
        self.rect.x += dx + screen_scroll
        self.rect.y += dy
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            if grenade_fx:
                grenade_fx.play()
            explosion = Explosion(self.rect.x, self.rect.y, 0.5)
            explosion_group.add(explosion)
            if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and \
               abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
                player.health -= 50
            for enemy in enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
                   abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
                    enemy.health -= 50

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 6):
            exp_path = os.path.join(IMG_DIR, "explosion", f"exp{num}.png")
            try:
                img = load_image(exp_path)
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                self.images.append(img)
            except Exception as e:
                print(f"Error loading explosion image {exp_path}: {e}")
        self.frame_index = 0
        if self.images:
            self.image = self.images[self.frame_index]
        else:
            self.image = pygame.Surface((50,50))
            self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0
    def update(self):
        self.rect.x += screen_scroll
        EXPLOSION_SPEED = 4
        self.counter += 1
        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]

# Create buttons
start_button   = button.Button(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 - 150, start_img, 1)
exit_button    = button.Button(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 50, exit_img, 1)
restart_button = button.Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, restart_img, 2)

# Create sprite groups
enemy_group       = pygame.sprite.Group()
bullet_group      = pygame.sprite.Group()
grenade_group     = pygame.sprite.Group()
explosion_group   = pygame.sprite.Group()
item_box_group    = pygame.sprite.Group()
decoration_group  = pygame.sprite.Group()
water_group       = pygame.sprite.Group()
exit_group        = pygame.sprite.Group()

# Load level data
world_data = []
with open(os.path.join(BASE_DIR, f"level{level}_data.csv"), newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    rows = list(reader)
    # Assume the first row is a header: e.g., "background,new"
    header = rows[0]
    if header[0].strip().lower() == "background":
        active_bg = header[1].strip().lower()
        tile_rows = rows[1:]
    else:
        tile_rows = rows
    # Parse tile rows into world_data
    for row in tile_rows:
        world_data.append([int(tile) for tile in row])


world = World()
player, health_bar = world.process_data(world_data)

# Start music for the initial level.
play_music_for_level(level,
    os.path.join(BASE_DIR, r"Darkwing Duck (NES) Music - Liquidator Stage.mp3"),
    os.path.join(BASE_DIR, r"Contra OST Base (Area 2 & 4).mp3"),
    os.path.join(BASE_DIR, r"FNaF World OST - Underneath 1.mp3"))

run = True
while run:
    clock.tick(FPS)
    
    if (level == 3 or level == 6) and not victory:
        for enemy in enemy_group:
            print(f"[VICTORY DEBUG] Enemy: {enemy.char_type}, alive: {enemy.alive}")
            if enemy.char_type == 'boss' and not enemy.alive:
                if win_sound_start_time is None and not win_sound_played:
                    pygame.mixer.music.stop()
                    win_sound_start_time = pygame.time.get_ticks()
                    win_sound_played = True  # now we know we've played it once
                    print("[VICTORY] Playing win sound now.")
                    if win_fx:
                        win_fx.play()
                elif win_sound_start_time is not None and pygame.time.get_ticks() - win_sound_start_time >= 9000:
                    victory = True


    if victory:
        screen.fill(GREEN)
        draw_text("Next Stage", victory_font, WHITE, SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 30)
    
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
            # 3-second delay is handled below—advance only if the delay has passed.
                pass  # (we process the key after the delay check)
    
    # Check if 3 seconds have passed since victory was triggered.
        if win_sound_start_time is not None and pygame.time.get_ticks() - win_sound_start_time >= 3000:
        # Before proceeding, stop the win sound if needed:
            if win_fx:
                pygame.mixer.Sound.stop(win_fx)
            victory = False
            win_sound_start_time = None
            win_sound_played = False  # reset so next level victory can play the sound again
            level += 1
            bg_scroll = 0
            world_data = reset_level()
            level_data_path = os.path.join(BASE_DIR, f"level{level}_data.csv")
            with open(level_data_path, newline='') as csvfile:
                reader = csv.reader(csvfile, delimiter=',')
                rows = list(reader)
                header = rows[0]
                if header[0].strip().lower() == "background":
                    active_bg = header[1].strip().lower()
                    tile_rows = rows[1:]
                else:
                    tile_rows = rows
                world_data = []
                for row in tile_rows:
                    world_data.append([int(tile) for tile in row])
            world = World()
            player, health_bar = world.process_data(world_data)
            pygame.mixer.music.stop()
            play_music_for_level(level,
                os.path.join(BASE_DIR, r"Darkwing Duck (NES) Music - Liquidator Stage.mp3"),
                os.path.join(BASE_DIR, r"Contra OST Base (Area 2 & 4).mp3"),
                os.path.join(BASE_DIR, r"FNaF World OST - Underneath 1.mp3"))
        pygame.display.update()
        continue


    if start_game == False:
        screen.fill(BG)
        if start_button.draw(screen):
            start_game = True
            start_intro = True
        if exit_button.draw(screen):
            run = False
    else:
        draw_bg()
        world.draw()
        health_bar.draw(player.health)
        draw_text("AMMO: ", font, WHITE, 10, 35)
        for x in range(player.ammo):
            screen.blit(bullet_img, (90 + (x * 10), 40))
        draw_text("GRENADES: ", font, WHITE, 10, 60)
        for x in range(player.grenades):
            screen.blit(grenade_img, (135 + (x * 15), 60))
        
        player.update()
        player.draw()
        
        for enemy in enemy_group:
            enemy.ai()
            enemy.update()
            enemy.draw()
        
        bullet_group.update()
        grenade_group.update()
        explosion_group.update()
        item_box_group.update()
        decoration_group.update()
        water_group.update()
        exit_group.update()
        
        bullet_group.draw(screen)
        grenade_group.draw(screen)
        explosion_group.draw(screen)
        item_box_group.draw(screen)
        decoration_group.draw(screen)
        water_group.draw(screen)
        exit_group.draw(screen)
        
        # In Level 3, spawn one item box at a time.
        if level == 3:
            if random.randint(1, 1000) <= 10:
                if world.obstacle_list:
                    random_tile = random.choice(world.obstacle_list)
                    spawn_x = random_tile[1].x
                    spawn_y = random_tile[1].y - TILE_SIZE
                    item_type = random.choice(['Health', 'Ammo', 'Grenade'])
                    new_box = ItemBox(item_type, spawn_x, spawn_y)
                    item_box_group.add(new_box)
        
        if start_intro:
            if intro_fade.fade():
                start_intro = False
                intro_fade.fade_counter = 0
        
        if player.alive:
            if shoot:
                player.shoot()
            elif grenade and not grenade_thrown and player.grenades > 0:
                grenade_obj = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction),
                                      player.rect.top, player.direction)
                grenade_group.add(grenade_obj)
                player.grenades -= 1
                grenade_thrown = True
            if player.in_air:
                player.update_action(2)
            elif moving_left or moving_right:
                player.update_action(1)
            else:
                player.update_action(0)
            screen_scroll, level_complete = player.move(moving_left, moving_right)
            bg_scroll -= screen_scroll
            if level_complete:
                start_intro = True
                level += 1
                bg_scroll = 0
                world_data = reset_level()
                if level <= MAX_LEVELS:
                    level_data_path = os.path.join(BASE_DIR, f"level{level}_data.csv")
                    with open(level_data_path, newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        rows = list(reader)
                        header = rows[0]
                        if header[0].strip().lower() == "background":
                            active_bg = header[1].strip().lower()
                            tile_rows = rows[1:]
                        else:
                            tile_rows = rows
                        world_data = []
                        for row in tile_rows:
                            world_data.append([int(tile) for tile in row])
                    world = World()
                    player, health_bar = world.process_data(world_data)
                    play_music_for_level(level,
                        os.path.join(BASE_DIR, r"Darkwing Duck (NES) Music - Liquidator Stage.mp3"),
                        os.path.join(BASE_DIR, r"Contra OST Base (Area 2 & 4).mp3"),
                        os.path.join(BASE_DIR, r"FNaF World OST - Underneath 1.mp3"))
        else:
            pygame.mixer.music.stop()
            if not death_sound_played:
                if death_fx:
                    death_fx.play()
                death_sound_played = True
                death_time = pygame.time.get_ticks()
            screen_scroll = 0
            death_fade.fade()
            if pygame.time.get_ticks() - death_time >= 2000:
                if restart_button.draw(screen):
                    death_fade.fade_counter = 0
                    death_time = 0
                    start_intro = True
                    bg_scroll = 0
                    world_data = reset_level()
                    level_data_path = os.path.join(BASE_DIR, f"level{level}_data.csv")
                    with open(level_data_path, newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        rows = list(reader)
                        header = rows[0]
                        if header[0].strip().lower() == "background":
                            active_bg = header[1].strip().lower()
                            tile_rows = rows[1:]
                        else:
                            tile_rows = rows
                        world_data = []
                        for row in tile_rows:
                            world_data.append([int(tile) for tile in row])
                    world = World()
                    player, health_bar = world.process_data(world_data)
                    death_sound_played = False
                    pygame.mixer.music.stop()
                    play_music_for_level(level,
                        os.path.join(BASE_DIR, r"Darkwing Duck (NES) Music - Liquidator Stage.mp3"),
                        os.path.join(BASE_DIR, r"Contra OST Base (Area 2 & 4).mp3"),
                        os.path.join(BASE_DIR, r"FNaF World OST - Underneath 1.mp3"))

        
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_q:
                grenade = True
            if event.key == pygame.K_w and player.alive:
                player.jump = True
                if jump_fx:
                    jump_fx.play()
            if event.key == pygame.K_ESCAPE:
                run = False
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_SPACE:
                shoot = False
            if event.key == pygame.K_q:
                grenade = False
                grenade_thrown = False
    pygame.display.update()

pygame.quit()

