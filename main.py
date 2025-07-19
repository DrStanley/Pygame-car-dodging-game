import pygame
import random

# Initialize Pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Car Dodge Game")

# Clock and fonts
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 48)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Load images
car_img = pygame.image.load("player_car.png").convert_alpha()
enemy_img = pygame.image.load("enemy_car.png").convert_alpha()
road_img = pygame.image.load("background.jpg").convert()

car_img = pygame.transform.scale(car_img, (40, 80))
enemy_img = pygame.transform.scale(enemy_img, (40, 80))
road_img = pygame.transform.scale(road_img, (WIDTH, HEIGHT))

# Game objects
car = pygame.Rect(220 // 2 - 20, HEIGHT - 100, 40, 80)
obstacles = []

# Game state
score = 0
level = 1
game_active = False
game_over = False
paused = False  # New variable for pause state

# Sounds
crash_sound = pygame.mixer.Sound("crash.mp3")
point_sound = pygame.mixer.Sound("point.mp3")

# Lanes
LANES = [60, 140, 220, 300]  # x-positions of 4 lanes


def reset_game():
    global car, obstacles, score, level, game_active, game_over, paused
    car.topleft = (WIDTH // 2 - 20, HEIGHT - 100)
    obstacles.clear()
    score = 0
    level = 1
    game_active = True
    game_over = False
    paused = False # Ensure not paused on reset


def handle_input():
    keys = pygame.key.get_pressed()
    # Horizontal movement
    if keys[pygame.K_LEFT] and car.left > 60:
        car.x -= 5
    if keys[pygame.K_RIGHT] and car.right < WIDTH - 60:
        car.x += 5
    # Vertical movement
    if keys[pygame.K_UP] and car.top > 0:  # Prevent going off the top of the screen
        car.y -= 5
    if keys[pygame.K_DOWN] and car.bottom < HEIGHT:  # Prevent going off the bottom of the screen
        car.y += 5


def spawn_obstacle():
    if random.random() < 0.02 + (score * 0.002):
        lane = random.choice(LANES)
        enemy = pygame.Rect(lane, -80, 40, 80)
        obstacles.append(enemy)


def update_obstacles():
    global score, level, game_active, game_over

    speed = 5 + (level - 1)
    for obs in obstacles[:]:
        obs.y += speed

        if obs.top > HEIGHT:
            obstacles.remove(obs)
            score += 1
            pygame.mixer.Sound.play(point_sound)

            if score % 10 == 0:
                level += 1

        # Collision
        if car.colliderect(obs):
            game_active = False
            game_over = True
            pygame.mixer.Sound.play(crash_sound)


def draw_game():
    screen.blit(road_img, (0, 0))
    screen.blit(car_img, car)

    for obs in obstacles:
        screen.blit(enemy_img, obs)

    score_text = font.render(f"Score: {score}", True, WHITE)
    level_text = font.render(f"Level: {level}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(level_text, (WIDTH - 120, 10))

def draw_pause_screen():
    pause_text = large_font.render("PAUSED", True, WHITE)
    resume_text = font.render("Press P to Resume", True, WHITE)
    screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2 - 50))
    screen.blit(resume_text, (WIDTH // 2 - resume_text.get_width() // 2, HEIGHT // 2 + 10))


def draw_start_screen():
    screen.fill(BLACK)
    title = large_font.render("Car Dodge Game", True, WHITE)
    prompt = font.render("Press SPACE to Start", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 180))
    screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, 250))


def draw_game_over():
    screen.fill(BLACK)
    over_text = large_font.render("Game Over", True, (255, 0, 0))
    score_text = font.render(f"Score: {score} | Level: {level}", True, WHITE)
    retry_text = font.render("Press R to Restart", True, WHITE)
    screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, 150))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 210))
    screen.blit(retry_text, (WIDTH // 2 - retry_text.get_width() // 2, 260))


# Main loop
running = True
while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p and game_active: # Toggle pause only if game is active
                paused = not paused

            if not game_active and not game_over:
                if event.key == pygame.K_SPACE:
                    reset_game()

            if game_over:
                if event.key == pygame.K_r:
                    reset_game()

    if game_active and not paused:
        handle_input()
        spawn_obstacle()
        update_obstacles()
        draw_game()
    elif paused:
        draw_game() # Draw the game state underneath the pause screen
        draw_pause_screen()
    elif game_over:
        draw_game_over()
    else:
        draw_start_screen()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()