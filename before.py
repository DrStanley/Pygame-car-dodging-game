# This is a sample Python script.

# Press Ctrl+F5 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import pygame
import  random

pygame.init()
screen = pygame.display.set_mode((400,400))
clock = pygame.time.Clock()
car = pygame.Rect(190,360,20,40)
obstacles = []
score = 0
font = pygame.font.Font(None,36)

def rest():
    global car,obstacles,score
    car.topleft = (190,360)
    obstacles.clear()
    score = 0
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and car.left>0:
        car.x -=5
    if keys[pygame.K_RIGHT] and car.left<400:
        car.x +=5

    spawn_rate = 0.008 + (score*0.2)
    if random.random() <spawn_rate:
        obstacles.append(
            pygame.Rect(random.randrange(0,380,20),-40,20,40))

    for obs in obstacles[:]:
        obs.y +=4 +(score//10)
        if obs.top >400:
            obstacles.remove(obs)
            score +=1
        if car.colliderect(obs):
            rest()
    screen.fill((0,0,0))
    pygame.draw.rect(screen,(0,255,0),car)
    for obs in obstacles:
        pygame.draw.rect(screen, (255,0,0),obs)
        score_text = font.render(f"Score: {score}",True,(255,255,255))
        screen.blit(score_text,(10,10))
        pygame.display.flip()
        clock.tick(60)
pygame.quit()