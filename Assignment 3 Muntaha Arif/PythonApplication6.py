import pygame
import random

# Initialize Pygame and mixer for sound
pygame.init()
pygame.mixer.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
UPPER_BOUND = 50  # The upper boundary the player cannot jump beyond
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Set up the clock for frame rate
clock = pygame.time.Clock()

# Load basic assets
player_image = pygame.Surface((50, 80))  # Taller to resemble a human
player_image.fill((0, 128, 255))
enemy_image = pygame.Surface((50, 50))
enemy_image.fill((255, 0, 0))
projectile_image = pygame.Surface((10, 5))
projectile_image.fill((0, 0, 0))  # Changed to black
platform_image = pygame.Surface((200, 20))
platform_image.fill((139, 69, 19))  # Brown for platforms

# Special enemy for level progression (Green Enemy)
green_enemy_image = pygame.Surface((50, 50))
green_enemy_image.fill((0, 255, 0))  # Green color for special enemy

# Big enemy for level 3 (Boss)
big_enemy_image = pygame.Surface((100, 100))
big_enemy_image.fill((255, 0, 0))  # Red, larger size

# Life Box
life_box_image = pygame.Surface((30, 30))
life_box_image.fill((128, 0, 128))  # Purple color for life box

# Load sound (make sure 'end_game.wav' exists in the same folder)
try:
    end_game_sound = pygame.mixer.Sound('end_game.wav')
except FileNotFoundError:
    print("Warning: 'end_game.wav' not found! Sound will be disabled.")
    end_game_sound = None

# Fonts for the score and game over
font = pygame.font.SysFont("Arial", 28)

# Define Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
DARK_GREEN = (0, 100, 0)
RED = (255, 0, 0)

# Firework Colors
firework_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]
firework_radius = 5

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_image
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60)
        self.speed = 5
        self.jump_power = 15
        self.gravity = 1
        self.velocity_y = 0
        self.on_ground = False
        self.lives = 3  # Player has 3 lives

    def update(self, keys, platforms):
        # Movement
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed

        # Jump
        if keys[pygame.K_SPACE] and self.on_ground:
            self.velocity_y = -self.jump_power
            self.on_ground = False

        # Gravity and vertical movement
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

        # Collision with platforms
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect) and self.velocity_y > 0:  # Falling onto platform
                self.rect.bottom = platform.rect.top
                self.velocity_y = 0
                self.on_ground = True

        # Boundaries (prevent going out of screen)
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.on_ground = True
        if self.rect.top < UPPER_BOUND:  # Prevent going above the upper boundary
            self.rect.top = UPPER_BOUND

# Projectile class
class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = projectile_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 10

    def update(self):
        self.rect.x += self.speed
        if self.rect.right > SCREEN_WIDTH:
            self.kill()  # Remove projectile when out of screen

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, speed=2):
        super().__init__()
        self.image = enemy_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = speed

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()  # Remove enemy when off-screen

# Green enemy for level progression (Hazard: lose 1 life)
class GreenEnemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = green_enemy_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 2

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()  # Remove green enemy when off-screen

# Big enemy class for level 3 (Boss with 5 HP)
class BigEnemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = big_enemy_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 1  # Boss moves slowly
        self.health = 5  # Boss requires 5 hits to die

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()  # Remove boss when off-screen

    def take_damage(self):
        self.health -= 1
        if self.health <= 0:
            self.kill()  # Kill boss after 5 hits

# Life box for extra lives
class LifeBox(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = life_box_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 2  # Life box moves like enemies

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()  # Remove life box when off-screen

# Platform class
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width=200, height=20, color=(139, 69, 19)):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Function to create 6 platforms at proper jumpable heights
def create_fixed_platforms():
    platforms = pygame.sprite.Group()
    jumpable_distance = 150  # Adjusted for player's jump range

    for i in range(5):
        x = random.randint(50, SCREEN_WIDTH - 250)  # Random x position within screen
        y = SCREEN_HEIGHT - 50 - (i * jumpable_distance)  # Stack platforms from bottom to top
        platform = Platform(x, y)
        platforms.add(platform)

    # Add a bottom platform at a one square distance from the ground
    bottom_platform = Platform(50, SCREEN_HEIGHT - 110, 200, 20)  # Positioned one square above the ground
    platforms.add(bottom_platform)

    # Add a dark green ground platform
    ground = Platform(0, SCREEN_HEIGHT - 30, SCREEN_WIDTH, 20, DARK_GREEN)
    platforms.add(ground)

    return platforms

# Function to display fireworks after winning
def display_fireworks():
    firework_list = []
    for _ in range(10):  # Generate 10 fireworks randomly
        firework_x = random.randint(100, SCREEN_WIDTH - 100)
        firework_y = random.randint(100, SCREEN_HEIGHT // 2)
        firework_color = random.choice(firework_colors)
        firework_list.append((firework_x, firework_y, firework_color))

    # Animate the fireworks
    for i in range(50):  # Firework expansion steps
        screen.fill(WHITE)
        for firework_x, firework_y, firework_color in firework_list:
            pygame.draw.circle(screen, firework_color, (firework_x, firework_y), firework_radius + i)
        pygame.display.flip()
        pygame.time.delay(50)

# Main game loop
def game_loop():
    player = Player()
    player_group = pygame.sprite.Group(player)
    
    enemies = pygame.sprite.Group()
    projectiles = pygame.sprite.Group()
    green_enemies = pygame.sprite.Group()  # Group for green enemies
    life_boxes = pygame.sprite.Group()  # Group for life boxes
    
    platforms = create_fixed_platforms()  # Create 6 fixed platforms

    score = 0
    kills = 0  # Track cumulative kills for level progression
    highest_score = 0  # Track the highest score
    level = 1
    green_enemy_timer = 0
    life_box_timer = 0  # Timer to spawn life boxes
    enemy_spawn_timer = 0  # Timer to spawn enemies
    game_paused = False
    can_shoot = True  # Controls shooting logic
    running = True
    game_over = False  # To track game over state
    player_won = False  # To track if player has won

    big_enemy_exists = False  # For level 3

    while running:
        screen.fill(WHITE)

        # Draw the upper boundary line
        pygame.draw.line(screen, BLACK, (0, UPPER_BOUND), (SCREEN_WIDTH, UPPER_BOUND), 5)

        # Event handling loop (added inside game loop)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # Pause button (P) - Toggle pause only once per press
                if event.key == pygame.K_p:
                    game_paused = not game_paused

        # Pause feature
        if game_paused:
            pause_text = font.render("Game Paused. Press P to Resume", True, BLACK)
            screen.blit(pause_text, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2))
            pygame.display.flip()
            continue  # Skip game logic when paused

        # Display score, highest score, lives, and level
        score_text = font.render(f"Score: {score}", True, BLACK)
        kills_text = font.render(f"Kills: {kills}", True, BLACK)
        lives_text = font.render(f"Lives: {player.lives}", True, BLACK)
        level_text = font.render(f"Level: {level}", True, BLACK)
        screen.blit(score_text, (10, 10))
        screen.blit(kills_text, (10, 40))
        screen.blit(lives_text, (10, 70))
        screen.blit(level_text, (10, 100))

        keys = pygame.key.get_pressed()

        if not game_over and not player_won:
            player_group.update(keys, platforms)
            enemies.update()
            projectiles.update()
            green_enemies.update()
            life_boxes.update()

            # Draw everything
            player_group.draw(screen)
            platforms.draw(screen)
            enemies.draw(screen)
            projectiles.draw(screen)
            green_enemies.draw(screen)
            life_boxes.draw(screen)

            # Handle shooting (S key, once per press)
            if keys[pygame.K_s] and can_shoot:
                projectile = Projectile(player.rect.centerx, player.rect.centery)
                projectiles.add(projectile)
                can_shoot = False  # Prevent continuous shooting

            # Allow shooting again when the key is released
            if not keys[pygame.K_s]:
                can_shoot = True

            # Check for collisions between player and enemies (red enemies)
            for enemy in pygame.sprite.groupcollide(projectiles, enemies, True, True):
                score += 1
                kills += 1

            # Check for collisions between player and life boxes
            for life_box in pygame.sprite.spritecollide(player, life_boxes, True):
                if player.lives < 3:  # Add life only if below 3
                    player.lives += 1

            # Check for collisions between player and green enemies (lose 1 life)
            if pygame.sprite.spritecollideany(player, green_enemies):
                player.lives -= 1  # Lose 1 life
                if player.lives <= 0:
                    game_over = True
                green_enemies.empty()  # Remove all green enemies after collision

            # Check for collisions between projectiles and green enemies
            for green_enemy in pygame.sprite.groupcollide(projectiles, green_enemies, True, True):
                if level < 3:  # Green enemies can only level up to level 2
                    level += 1

            # Level progression based on cumulative kills
            if kills == 11:
                level = 2  # Proceed to level 2 after 10 cumulative kills
            if kills == 21:
                level = 3  # Proceed to level 3 after 20 cumulative kills

            # Enemy spawning logic based on level
            if level == 1:
                enemy_speed = 2  # Level 1 speed
                enemy_spawn_timer += 1
                if enemy_spawn_timer > 60:  # Spawn an enemy every 1 second
                    enemy = Enemy(SCREEN_WIDTH, random.randint(UPPER_BOUND, SCREEN_HEIGHT - 100), speed=enemy_speed)
                    enemies.add(enemy)
                    enemy_spawn_timer = 0  # Reset timer
            elif level == 2:
                enemy_speed = 5  # Level 2 speed
                enemy_spawn_timer += 1
                if enemy_spawn_timer > 60:  # Spawn an enemy every 1 second
                    enemy = Enemy(SCREEN_WIDTH, random.randint(UPPER_BOUND, SCREEN_HEIGHT - 100), speed=enemy_speed)
                    enemies.add(enemy)
                    enemy_spawn_timer = 0  # Reset timer
            elif level == 3:
                # Only big enemies in level 3
                if not big_enemy_exists:
                    big_enemy = BigEnemy(SCREEN_WIDTH, SCREEN_HEIGHT // 2)
                    enemies.add(big_enemy)
                    big_enemy_exists = True
                # Check if the big enemy was hit 5 times
                for projectile in pygame.sprite.spritecollide(big_enemy, projectiles, True):
                    big_enemy.take_damage()
                if not big_enemy.alive():
                    player_won = True  # Player wins after defeating the boss

            # Spawn green enemy every 15 seconds in levels 1 and 2
            if level < 3:
                green_enemy_timer += 1
                if green_enemy_timer > 900:  # Approximately 15 seconds at 60 FPS
                    green_enemy = GreenEnemy(SCREEN_WIDTH, random.randint(UPPER_BOUND, SCREEN_HEIGHT - 100))
                    green_enemies.add(green_enemy)
                    green_enemy_timer = 0  # Reset timer

            # Spawn life boxes every 10 seconds
            life_box_timer += 1
            if life_box_timer > 600 and len(life_boxes) < 3:  # Approximately 10 seconds at 60 FPS
                life_box = LifeBox(SCREEN_WIDTH, random.randint(UPPER_BOUND + 50, SCREEN_HEIGHT - 100))
                life_boxes.add(life_box)
                life_box_timer = 0  # Reset timer

            # Check for collisions between player and enemies
            if pygame.sprite.spritecollideany(player, enemies):
                player.lives -= 1  # Reduce player's lives
                if player.lives <= 0:
                    if end_game_sound:
                        end_game_sound.play()  # Play end game sound when player dies
                    game_over = True  # Trigger game over
                else:
                    # Reset player position after hit
                    player.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60)

        elif player_won:
            # Display the winning message and fireworks animation
            win_text = font.render("You Win!", True, BLACK)
            screen.blit(win_text, (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2))
            pygame.display.flip()
            pygame.time.delay(1000)  # Short pause before fireworks
            display_fireworks()
            running = False  # End the game after fireworks

        else:
            # Display Game Over text
            game_over_text = font.render("Game Over! Press R to restart", True, BLACK)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2))

            # Handle restarting the game
            if keys[pygame.K_r]:
                # Reset the game
                player.lives = 3
                score = 0
                kills = 0
                level = 1
                enemies.empty()
                projectiles.empty()
                green_enemies.empty()
                life_boxes.empty()
                player.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60)
                platforms = create_fixed_platforms()  # Generate new random platforms
                game_over = False
                big_enemy_exists = False
                player_won = False  # Reset the win state

        pygame.display.flip()

        clock.tick(60)  # Frame rate (60 FPS)

    pygame.quit()

# Start the game
if __name__ == "__main__":
    game_loop()
