import pygame
import random

# Initialize pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SIZE = 50
PLAYER_SPEED = 5
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

class MetaGame:
    def __init__(self):
        # Set up display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Meta Game")
        
        # Game elements
        self.player = pygame.Rect(
            SCREEN_WIDTH // 2 - PLAYER_SIZE // 2,
            SCREEN_HEIGHT // 2 - PLAYER_SIZE // 2,
            PLAYER_SIZE,
            PLAYER_SIZE
        )
        
        # Meta texts
        self.meta_texts = [
            "This is a game about games",
            "You're controlling a red square",
            "Press R for random meta thoughts",
            "The game knows you're playing it",
            "Try moving with WASD keys"
        ]
        self.current_text = random.choice(self.meta_texts)
        
        # Font setup
        self.font = pygame.font.SysFont('Arial', 24)
        self.clock = pygame.time.Clock()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_r:
                    self.current_text = random.choice(self.meta_texts)
        return True
    
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]: self.player.y -= PLAYER_SPEED
        if keys[pygame.K_s]: self.player.y += PLAYER_SPEED
        if keys[pygame.K_a]: self.player.x -= PLAYER_SPEED
        if keys[pygame.K_d]: self.player.x += PLAYER_SPEED
        
        # Keep player on screen
        self.player.x = max(0, min(self.player.x, SCREEN_WIDTH - PLAYER_SIZE))
        self.player.y = max(0, min(self.player.y, SCREEN_HEIGHT - PLAYER_SIZE))
    
    def draw(self):
        self.screen.fill(BLACK)
        pygame.draw.rect(self.screen, RED, self.player)
        
        # Render text
        text = self.font.render(self.current_text, True, WHITE)
        self.screen.blit(text, (20, 20))
        
        pygame.display.flip()
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()

if __name__ == "__main__":
    game = MetaGame()
    game.run()