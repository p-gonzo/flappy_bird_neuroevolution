import pygame
import random

# Constants
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
SCREEN_WIDTH = 700
BIRD_X = SCREEN_WIDTH // 2
SCREEN_HEIGHT = 500
BIRD_SIZE = 10
PIPE_WIDTH = 50
PIPE_GAP = 80

# New pipe event timer
NEW_PIPE_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(NEW_PIPE_EVENT, 1200)

# Game classes
class Pipe:
    def __init__(self):
        self.x = SCREEN_WIDTH
        self.y = random.randrange(100, SCREEN_HEIGHT - 100)
        self.color = WHITE
        self.bottom_color = WHITE
        self.top_color = WHITE

class Bird:
    def __init__(self, y_start, color):
        self.x = SCREEN_WIDTH // 2
        self.y = y_start
        self.y_delta = 0
        self.color = color
        self.pipe = None
    
    def flap(self):
        if self.y_delta < 0:
            self.y_delta = 5
        if self.y_delta < 15:
            self.y_delta +=6


class Game():
    def __init__(self, birds):
        self.done = False
        self.clock = pygame.time.Clock()
        self.pipes = []
        self.closest_pipe_to_bird = None
        self.birds = birds
        self.size = [SCREEN_WIDTH, SCREEN_HEIGHT]
        self.screen = None
        self.dt = 0

    def run(self):
        pygame.init()
        pygame.display.set_caption("Flappy Bird")
        self.screen = pygame.display.set_mode(self.size)
 
        while not self.done:
            self.dt = self.clock.tick(30)
            self.update_everything()
            self.draw_everything()
        pygame.quit()

    def update_everything(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done = True
            elif event.type == NEW_PIPE_EVENT:
                    self.pipes = [Pipe()] + self.pipes
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    for bird in self.birds:
                        if bird.y_delta < 0:
                            bird.y_delta = 5
                        if bird.y_delta < 15:
                            bird.y_delta +=6

        for pipe in self.pipes:
            pipe.x -= (5 * self.dt/30)
            pipe.bottom_color = WHITE
            pipe.top_color = WHITE

            if pipe.x > BIRD_X:
                if self.closest_pipe_to_bird == None:
                    self.closest_pipe_to_bird = pipe
            if self.closest_pipe_to_bird is not None:
                # Send pipe information to birds
                self.closest_pipe_to_bird.bottom_color = GREEN
                self.closest_pipe_to_bird.top_color = GREEN
                if self.closest_pipe_to_bird.x < BIRD_X:
                    self.closest_pipe_to_bird = None

            if pipe.x < BIRD_X and pipe.x + PIPE_WIDTH > BIRD_X:
                for bird in self.birds:
                    if bird.y > pipe.y + PIPE_GAP:
                        #done = True
                        pipe.top_color = RED
                    elif bird.y < pipe.y:
                        #done = True
                        pipe.bottom_color = RED

        for bird_idx, bird in enumerate(self.birds):
            bird.y_delta += -1.3 #negative gravity
            bird.y = round(bird.y - (bird.y_delta * self.dt/30))
            bird.pipe = self.closest_pipe_to_bird

            
            ## This is where NN data will live 
            prob_of_flap = random.uniform(0, 1)
            if prob_of_flap < 0.08:
                bird.flap()

            if bird.y > SCREEN_HEIGHT:
                del self.birds[bird_idx]
        
        if len(self.birds) == 0:
            self.done = True
    
    def draw_everything(self):
        self.screen.fill(BLACK)
        self.draw_pipes()
        self.draw_birds()
        pygame.display.flip()

    def draw_birds(self):
        for bird in self.birds:
            pygame.draw.circle(self.screen, bird.color, [bird.x, bird.y], BIRD_SIZE)

    def draw_pipes(self):
        for pipe in self.pipes:
            pygame.draw.rect(self.screen, pipe.bottom_color, (pipe.x, 0, PIPE_WIDTH, pipe.y ))
            pygame.draw.rect(self.screen, pipe.top_color, (pipe.x, pipe.y + PIPE_GAP, PIPE_WIDTH, SCREEN_HEIGHT - pipe.y ))


 
if __name__ == "__main__":
    birds = [
        Bird(
            random.randrange(100, SCREEN_HEIGHT - 100),
            (random.randrange(0, 255), random.randrange(0, 255), random.randrange(0, 255))
        ) 
        for i in range(11)
    ]
    game = Game(birds)
    game.run()