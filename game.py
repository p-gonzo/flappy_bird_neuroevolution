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

# Application State
birds = [
    Bird(
        random.randrange(100, SCREEN_HEIGHT - 100),
        (random.randrange(0, 255), random.randrange(0, 255), random.randrange(0, 255))
    ) 
    for i in range(11)
]

done = False
clock = pygame.time.Clock()
pipes = []
closest_pipe_to_bird = None

def draw_everything(screen):

    screen.fill(BLACK)
    draw_pipes(screen)
    draw_birds(screen)
    pygame.display.flip()


def draw_birds(screen):
    for bird in birds:
        pygame.draw.circle(screen, bird.color, [bird.x, bird.y], BIRD_SIZE)

def draw_pipes(screen):
    for pipe in pipes:
        pygame.draw.rect(screen, pipe.bottom_color, (pipe.x, 0, PIPE_WIDTH, pipe.y ))
        pygame.draw.rect(screen, pipe.top_color, (pipe.x, pipe.y + PIPE_GAP, PIPE_WIDTH, SCREEN_HEIGHT - pipe.y ))

def update_everything():
    
    global pipes
    global clock
    global done
    global closest_pipe_to_bird

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

    for pipe in pipes:
        pipe.x -= (5 * dt/30)
        pipe.bottom_color = WHITE
        pipe.top_color = WHITE

        if pipe.x > BIRD_X:
            if closest_pipe_to_bird == None:
                closest_pipe_to_bird = pipe
        if closest_pipe_to_bird is not None:
            # Send pipe information to birds
            closest_pipe_to_bird.bottom_color = GREEN
            closest_pipe_to_bird.top_color = GREEN
            if closest_pipe_to_bird.x < BIRD_X:
                closest_pipe_to_bird = None

        if pipe.x < BIRD_X and pipe.x + PIPE_WIDTH > BIRD_X:
            for bird in birds:
                if bird.y > pipe.y + PIPE_GAP:
                    #done = True
                    pipe.top_color = RED
                elif bird.y < pipe.y:
                    #done = True
                    pipe.bottom_color = RED

    for bird_idx, bird in enumerate(birds):
        bird.y_delta += -1.3 #negative gravity
        bird.y = round(bird.y - (bird.y_delta * dt/30))
        bird.pipe = closest_pipe_to_bird

        
        ## This is where NN data will live 
        prob_of_flap = random.uniform(0, 1)
        if prob_of_flap < 0.08:
            bird.flap()

        if bird.y > SCREEN_HEIGHT:
            del birds[bird_idx]
    
    if len(birds) == 0:
        done = True

def main():
    pygame.init()
    pygame.display.set_caption("Flappy Bird")
    size = [SCREEN_WIDTH, SCREEN_HEIGHT]
    screen = pygame.display.set_mode(size)
 
    while not done:
       update_everything()
       draw_everything(screen)
    pygame.quit()

class Game():
    def __init__(self):
        self.done = False
        self.clock = pygame.time.Clock()
        self.pipes = []
        self.closest_pipe_to_bird = None
        self.birds = [
            Bird(
                random.randrange(100, SCREEN_HEIGHT - 100),
                (random.randrange(0, 255), random.randrange(0, 255), random.randrange(0, 255))
            ) 
            for i in range(11)
        ]

    

 
if __name__ == "__main__":
    main()