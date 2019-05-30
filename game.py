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
    def __init__(self, y_start, color):
        self.x = SCREEN_WIDTH // 2
        self.y = y_start
        self.y_delta = 0
        self.color = color
    def flap(self):
        if self.y_delta < 0:
            self.y_delta = 5
        if self.y_delta < 15:
            self.y_delta +=6
        
 
def main(players):
    pygame.init()
    size = [SCREEN_WIDTH, SCREEN_HEIGHT]
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("Flappy Bird")
 
    done = False
 
    clock = pygame.time.Clock()
    pipes = []
    birds = players
 
    while not done:
        dt = clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == NEW_PIPE_EVENT:
                    pipes = [Pipe()] + pipes
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    for bird in birds:
                        if bird.y_delta < 0:
                            bird.y_delta = 5
                        if bird.y_delta < 15:
                            bird.y_delta +=6
 
        screen.fill(BLACK)
 
        for pipe in pipes:
            pipe.x -= (5 * dt/30)
            pygame.draw.rect(screen, WHITE, (pipe.x, 0, 50, pipe.y ))
            pygame.draw.rect(screen, WHITE, (pipe.x, pipe.y + 80, 50, SCREEN_HEIGHT - pipe.y ))
            
            if pipe.x < 350 and pipe.x + 50 > 350:
                for bird in birds:
                    if bird.y > pipe.y + 80:
                        #done = True
                        pygame.draw.rect(screen, RED, (pipe.x, pipe.y + 80, 50, SCREEN_HEIGHT - pipe.y ))
                    elif bird.y < pipe.y:
                        #done = True
                        pygame.draw.rect(screen, RED, (pipe.x, 0, 50, pipe.y ))
            if pipe.x < -51:
                pipes.pop()

        for bird in birds:
            bird.y_delta += -1.3 #negative gravity
            bird.y = round(bird.y - (bird.y_delta * dt/30))
            pygame.draw.circle(screen, bird.color, [bird.x, bird.y], BIRD_SIZE)
            
            ## This is where NN data will live 
            prob_of_flap = random.uniform(0, 1)
            if prob_of_flap < 0.1:
                bird.flap()

        for bird_idx, bird in enumerate(birds):
            if bird.y > SCREEN_HEIGHT:
                del birds[bird_idx]
        if len(birds) == 0:
            done = True
        


        pygame.display.flip()
 
    pygame.quit()
 
if __name__ == "__main__":
    birds = [
        Bird(
            random.randrange(100, SCREEN_HEIGHT - 100),
            (random.randrange(0, 255), random.randrange(0, 255), random.randrange(0, 255))
        ) 
        for i in range(11)
    ]
    main(birds)