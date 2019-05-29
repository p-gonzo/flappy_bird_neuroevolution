import pygame
import random
 
# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
 
SCREEN_WIDTH = 700
SCREEN_HEIGHT = 500
BIRD_SIZE = 10

NEW_PIPE_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(NEW_PIPE_EVENT, 1200)

 
class Pipe:
    def __init__(self):
        self.x = SCREEN_WIDTH
        self.y = random.randrange(100, SCREEN_HEIGHT - 100)

class Bird:
    def __init__(self):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.y_delta = 0
 
def main():
    """
    This is our main program.
    """
    pygame.init()
    size = [SCREEN_WIDTH, SCREEN_HEIGHT]
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("Flappy Bird")
 
    done = False
 
    clock = pygame.time.Clock()
    pipes = []
    player = Bird()
 
    while not done:
        dt = clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == NEW_PIPE_EVENT:
                    pipes = [Pipe()] + pipes
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if player.y_delta < 0:
                        player.y_delta = 5
                    if player.y_delta < 15:
                        player.y_delta +=6
 
        screen.fill(BLACK)
 
        for pipe_idx, pipe in enumerate(pipes):
            pipe.x -= (5 * dt/30)
            pygame.draw.rect(screen, WHITE, (pipe.x, 0, 50, pipe.y ))
            pygame.draw.rect(screen, WHITE, (pipe.x, pipe.y + 80, 50, SCREEN_HEIGHT - pipe.y ))
            
            if pipe.x < 350 and pipe.x + 50 > 350:
                if player.y > pipe.y + 80:
                    #done = True
                    pygame.draw.rect(screen, RED, (pipe.x, pipe.y + 80, 50, SCREEN_HEIGHT - pipe.y ))
                elif player.y < pipe.y:
                    #done = True
                    pygame.draw.rect(screen, RED, (pipe.x, 0, 50, pipe.y ))
            if pipe.x < -51:
                pipes.pop()

        
        player.y_delta += -1.3 #negative gravity
        player.y = round(player.y - (player.y_delta * dt/30))
        pygame.draw.circle(screen, YELLOW, [player.x, player.y], BIRD_SIZE)

        if player.y > SCREEN_HEIGHT:
            done = True

        pygame.display.flip()
 
    pygame.quit()
 
if __name__ == "__main__":
    main()