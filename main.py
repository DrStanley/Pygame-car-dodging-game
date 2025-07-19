import pygame
import random
import time
import json # Import the json module

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
BLUE = (0, 0, 255) # For shield visual feedback

# Load images
car_img_original = pygame.image.load("player_car.png").convert_alpha()
enemy_img = pygame.image.load("enemy_car.png").convert_alpha()
road_img = pygame.image.load("background.jpg").convert()
shield_powerup_img = pygame.image.load("shield.png").convert_alpha()

# Scale images
car_img_original = pygame.transform.scale(car_img_original, (40, 80))
enemy_img = pygame.transform.scale(enemy_img, (40, 80))
road_img = pygame.transform.scale(road_img, (WIDTH, HEIGHT))
shield_powerup_img = pygame.transform.scale(shield_powerup_img, (40, 40)) # Scale shield power-up

# Create a shielded version of the car image (optional, but good for feedback)
car_img_shielded = car_img_original.copy()
pygame.draw.circle(car_img_shielded, BLUE, (car_img_shielded.get_width() // 2, car_img_shielded.get_height() // 2), 30, 3) # Add a blue circle outline

# Lanes (DEFINED HERE FIRST)
LANES = [60, 140, 220, 300]  # x-positions of 4 lanes

# Game objects
car = pygame.Rect(LANES[1], HEIGHT - 100, 40, 80) # Adjusted car start to align with a lane
obstacles = []
powerups = [] # List to hold power-up rectangles

# Game state
score = 0
level = 1
game_active = False
game_over = False
paused = False

# High score persistence
HIGHSCORE_FILE = "highscore.json"
def load_highscore():
    try:
        with open(HIGHSCORE_FILE, 'r') as f:
            data = json.load(f)
            return data.get('highscore', 0) # Get 'highscore' key, default to 0 if not found
    except FileNotFoundError:
        return 0
    except json.JSONDecodeError:
        return 0

def save_highscore(score_to_save):
    with open(HIGHSCORE_FILE, 'w') as f:
        json.dump({'highscore': score_to_save}, f)

high_score = load_highscore() # Load the high score when the game starts

# Shield variables
shield_active = False
shield_duration_start_time = 0
SHIELD_DURATION = 5 # seconds

# Sounds
crash_sound = pygame.mixer.Sound("crash.mp3")
point_sound = pygame.mixer.Sound("point.mp3")
powerup_sound = pygame.mixer.Sound("power_up.mp3")


def reset_game():
    global car, obstacles, powerups, score, level, game_active, game_over, paused, shield_active, shield_duration_start_time, high_score
    car.topleft = (LANES[1], HEIGHT - 100) # Reset car to initial lane position
    obstacles.clear()
    powerups.clear()
    score = 0
    level = 1
    game_active = True
    game_over = False
    paused = False
    shield_active = False # Reset shield state
    shield_duration_start_time = 0
    # high_score is not reset here, it persists across games


def handle_input():
    keys = pygame.key.get_pressed()
    # Horizontal movement
    if keys[pygame.K_LEFT] and car.left > 60:
        car.x -= 5
    if keys[pygame.K_RIGHT] and car.right < WIDTH - 60:
        car.x += 5
    # Vertical movement
    if keys[pygame.K_UP] and car.top > 0:
        car.y -= 5
    if keys[pygame.K_DOWN] and car.bottom < HEIGHT:
        car.y += 5


def spawn_obstacle():
    # Regular obstacle spawning
    if random.random() < 0.02 + (score * 0.002):
        lane = random.choice(LANES)
        enemy = pygame.Rect(lane, -80, 40, 80)
        obstacles.append(enemy)

def spawn_powerup():
    # Shield power-up spawning (less frequent than obstacles)
    if random.random() < 0.005: # Adjust this probability for how often power-ups appear
        lane = random.choice(LANES)
        shield_pu = pygame.Rect(lane, -40, 40, 40) # Smaller rect for power-up
        powerups.append(shield_pu)


def update_game_elements():
    global score, level, game_active, game_over, shield_active, shield_duration_start_time, high_score

    speed = 5 + (level - 1)

    # Update and check obstacles
    for obs in obstacles[:]:
        obs.y += speed

        if obs.top > HEIGHT:
            obstacles.remove(obs)
            score += 1
            pygame.mixer.Sound.play(point_sound)

            if score % 10 == 0:
                level += 1

        # Collision with obstacles
        if car.colliderect(obs):
            if shield_active:
                obstacles.remove(obs) # Shield destroys the obstacle
            else:
                game_active = False
                game_over = True
                pygame.mixer.Sound.play(crash_sound)
                # Check and save high score here when game ends due to collision
                if score > high_score:
                    high_score = score
                    save_highscore(high_score)


    # Update and check power-ups
    for pu in powerups[:]:
        pu.y += speed

        if pu.top > HEIGHT:
            powerups.remove(pu)

        # Collision with power-up
        if car.colliderect(pu):
            powerups.remove(pu)
            shield_active = True
            shield_duration_start_time = time.time() # Record activation time
            pygame.mixer.Sound.play(powerup_sound)

    # Manage shield duration
    if shield_active:
        if time.time() - shield_duration_start_time > SHIELD_DURATION:
            shield_active = False # Deactivate shield


def draw_game():
    screen.blit(road_img, (0, 0))

    # Draw car based on shield status
    if shield_active:
        screen.blit(car_img_shielded, car)
    else:
        screen.blit(car_img_original, car)

    for obs in obstacles:
        screen.blit(enemy_img, obs)

    for pu in powerups:
        screen.blit(shield_powerup_img, pu) # Draw shield power-up

    score_text = font.render(f"Score: {score}", True, WHITE)
    level_text = font.render(f"Level: {level}", True, WHITE)
    shield_status_text = font.render(f"Shield: {'ON' if shield_active else 'OFF'}", True, BLUE if shield_active else WHITE)
    high_score_text = font.render(f"High Score: {high_score}", True, WHITE) # Render high score

    screen.blit(score_text, (10, 10))
    screen.blit(level_text, (WIDTH - 120, 10))
    screen.blit(shield_status_text, (10, 40)) # Display shield status
    screen.blit(high_score_text, (WIDTH // 2 - high_score_text.get_width() // 2, 10)) # Centered high score


def draw_pause_screen():
    pause_text = large_font.render("PAUSED", True, WHITE)
    resume_text = font.render("Press P to Resume", True, WHITE)
    screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2 - 50))
    screen.blit(resume_text, (WIDTH // 2 - resume_text.get_width() // 2, HEIGHT // 2 + 10))


def draw_start_screen():
    screen.fill(BLACK)
    title = large_font.render("Car Dodge Game", True, WHITE)
    prompt = font.render("Press SPACE to Start", True, WHITE)
    high_score_start_text = font.render(f"High Score: {high_score}", True, WHITE) # Show high score on start screen

    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 180))
    screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, 250))
    screen.blit(high_score_start_text, (WIDTH // 2 - high_score_start_text.get_width() // 2, 300)) # Position on start screen


def draw_game_over():
    screen.fill(BLACK)
    over_text = large_font.render("Game Over", True, (255, 0, 0))
    score_text = font.render(f"Score: {score} | Level: {level}", True, WHITE)
    high_score_display_text = font.render(f"High Score: {high_score}", True, WHITE) # Display high score on game over
    retry_text = font.render("Press R to Restart", True, WHITE)

    screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, 150))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 210))
    screen.blit(high_score_display_text, (WIDTH // 2 - high_score_display_text.get_width() // 2, 240)) # New position
    screen.blit(retry_text, (WIDTH // 2 - retry_text.get_width() // 2, 290)) # Shifted down


# Main loop
running = True
while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p and game_active:
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
        spawn_powerup()
        update_game_elements()
        draw_game()
    elif paused:
        draw_game()
        draw_pause_screen()
    elif game_over:
        draw_game_over()
    else: # Start screen
        draw_start_screen()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()