import pygame
import random
import numpy as np
from copy import deepcopy
from nn import NeuralNetwork
import tensorflow as tf


# Constants
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
DARK_GREEN = (0, 100, 0)
ACTIVE_GREEN = (0, 200, 0)
SKY_BLUE = (135, 206, 235)

GAME_SCREEN_WIDTH = 700
GAME_SCREEN_HEIGHT = 500
BIRD_SIZE = 10
PIPE_WIDTH = 25
PIPE_GAP = 100
BIRD_X = GAME_SCREEN_WIDTH // 2
GAME_MENU_WIDTH = 300
SCREEN_WIDTH = GAME_SCREEN_WIDTH + GAME_MENU_WIDTH
FONT_SIZE = 30

# New pipe event timer
NEW_PIPE_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(NEW_PIPE_EVENT, 1400)

#Helper func
def translate(value, leftMin, leftMax, rightMin, rightMax):
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin
    valueScaled = float(value - leftMin) / float(leftSpan)
    return rightMin + (valueScaled * rightSpan)

# Game classes
class Pipe:
    def __init__(self):
        self.x = GAME_SCREEN_WIDTH
        self.y = random.randrange(100, GAME_SCREEN_HEIGHT - 100)
        self.bottom_color = DARK_GREEN
        self.top_color = DARK_GREEN

class Bird:
    def __init__(self, y_start, color, brain_model = None):
        self.x = GAME_SCREEN_WIDTH // 2
        self.y = y_start
        self.y_delta = 0
        self.color = color
        self.pipe = None
        #shape of our brain
        self.brain = NeuralNetwork(3, 8, 2, parent_weights=brain_model)
        self.fitness = 0
    
    def flap(self):
        if self.y_delta < 0:
            self.y_delta = 5
        if self.y_delta < 15:
            self.y_delta +=6
    
    def will_flap(self):
        if self.pipe is not None:
            x_delta, y_delta = self.look_at_oncoming_pipe()
            self_delta = translate(self.y_delta, -21, 21, -1, 1)
            x_delta = translate(x_delta, 0, 388, -1, 1)
            y_delta = translate(y_delta, 0, 470, -1, 1)
            return(self.brain.predict([x_delta, y_delta, self_delta]))

    def look_at_oncoming_pipe(self):
        horizontal_distance_to_pipe = self.pipe.x + PIPE_WIDTH - self.x
        vertical_distance_to_pipe = self.pipe.y - self.y
        return (horizontal_distance_to_pipe, vertical_distance_to_pipe)



class Game():
    def __init__(self, birds):
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption("Flappy Bird: NeuroEvolution")


        self.done = False
        self.created_new_generation = False
        self.clock = pygame.time.Clock()
        self.pipes = []
        self.closest_pipe_to_bird = None
        self.birds = birds
        self.size = [SCREEN_WIDTH, GAME_SCREEN_HEIGHT]
        self.screen = pygame.display.set_mode(self.size)
        self.dt = 0
        self.fitest_brain_so_far = None
        self.highest_fitness_so_far = 0
        self.current_generation = 1
        self.current_score = 0

        self.main_font = pygame.font.Font(None, FONT_SIZE)
        self.large_font = pygame.font.Font(None, FONT_SIZE * 2)

    def run(self):
 
        while not self.done:
            self.dt = self.clock.tick(30)
            if self.created_new_generation:
                self.refresh_game_after_new_generation()
            self.handle_event_queue()
            self.update_everything()
            self.draw_everything()
            
            if len(self.birds) == 1:
                self.capture_last_bird_remaining(self.birds[0])
            if len(self.birds) == 0:
                self.display_loading_screen()
                self.create_new_generation(self.fitest_brain_so_far)
            
        pygame.quit()

    def handle_event_queue(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done = True
            elif event.type == NEW_PIPE_EVENT:
                    self.pipes = [Pipe()] + self.pipes
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    self.done = True
                if event.key == pygame.K_SPACE:
                    for bird in self.birds:
                        bird.flap()

    def update_everything(self):
        for pipe in self.pipes:
            self.move_pipe_forward(pipe)
            self.set_closest_pipe_to_bird(pipe)
            self.handle_pipe_bird_collistion(pipe)

        for bird_idx, bird in enumerate(self.birds):
            bird.fitness +=1
            self.move_bird(bird)
            self.kill_bird_that_flies_out_of_bounds(bird, bird_idx)
            if self.closest_pipe_to_bird is not None:
                bird.pipe = self.closest_pipe_to_bird
            if bird.will_flap():
                bird.flap()
        
        self.update_text_values()

    def move_pipe_forward(self, pipe):
        pipe.x -= (5 * self.dt/30)
        pipe.bottom_color = DARK_GREEN
        pipe.top_color = DARK_GREEN
        if pipe.x < -50:
            self.pipes.pop()
    
    def set_closest_pipe_to_bird(self, pipe):
        if pipe.x > BIRD_X:
            if self.closest_pipe_to_bird == None:
                self.closest_pipe_to_bird = pipe
        if self.closest_pipe_to_bird is not None:
            self.closest_pipe_to_bird.bottom_color = ACTIVE_GREEN
            self.closest_pipe_to_bird.top_color = ACTIVE_GREEN
            if self.closest_pipe_to_bird.x < BIRD_X:
                self.current_score += 1
                self.closest_pipe_to_bird = None

    def handle_pipe_bird_collistion(self, pipe):
        if pipe.x < BIRD_X and pipe.x + PIPE_WIDTH > BIRD_X:
            for bird_idx, bird in enumerate(self.birds):
                if bird.y > pipe.y + PIPE_GAP:
                    del self.birds[bird_idx]
                    pipe.top_color = RED
                elif bird.y < pipe.y:
                    del self.birds[bird_idx]
                    pipe.bottom_color = RED

    def move_bird(self, bird):
        bird.y_delta += -1.3 #negative gravity
        bird.y = round(bird.y - (bird.y_delta * self.dt/30))

    def kill_bird_that_flies_out_of_bounds(self, bird, bird_idx):
        if bird.y + 25 > GAME_SCREEN_HEIGHT or bird.y < -100:
            del self.birds[bird_idx]

    def capture_last_bird_remaining(self, fit_bird):
        if self.fitest_brain_so_far is None or fit_bird.fitness > self.highest_fitness_so_far:
            self.fitest_brain_so_far = fit_bird.brain.model.get_weights()
            self.highest_fitness_so_far = fit_bird.fitness

    def update_text_values(self):
        self.generation_text = self.main_font.render(f'Generation : {self.current_generation}', False, WHITE)
        self.current_score_text = self.large_font.render(f'{self.current_score}', False, YELLOW)

    def draw_everything(self):
        self.screen.fill(SKY_BLUE)
        self.draw_pipes()
        self.draw_birds()
        self.draw_menu()
        pygame.display.flip()

    def draw_birds(self):
        for bird in self.birds:
            pygame.draw.circle(self.screen, bird.color, [bird.x, bird.y], BIRD_SIZE)

    def draw_pipes(self):
        for pipe in self.pipes:
            pygame.draw.rect(self.screen, pipe.bottom_color, (pipe.x, 0, PIPE_WIDTH, pipe.y ))
            pygame.draw.rect(self.screen, pipe.top_color, (pipe.x, pipe.y + PIPE_GAP, PIPE_WIDTH, GAME_SCREEN_HEIGHT - pipe.y ))
        
        text_rect = self.current_score_text.get_rect()
        text_rect.center = (GAME_SCREEN_WIDTH - FONT_SIZE * 2 , 0 + FONT_SIZE * 2 // 2 )
        self.screen.blit(self.current_score_text, text_rect)

    def draw_menu(self):
        pygame.draw.rect(self.screen, BLACK, (GAME_SCREEN_WIDTH, 0, GAME_MENU_WIDTH, GAME_SCREEN_HEIGHT))
        text_rect = self.generation_text.get_rect()
        text_rect.center = ((GAME_SCREEN_WIDTH + SCREEN_WIDTH) // 2, 0 + FONT_SIZE // 2 )
        self.screen.blit(self.generation_text, text_rect)

    def create_new_generation(self, fit_brain):
        tf.keras.backend.clear_session()
        for i in range(20):
            new_bird = Bird(
                GAME_SCREEN_HEIGHT // 2,
                (random.randrange(0, 255), random.randrange(0, 255), random.randrange(0, 255)),
                brain_model=fit_brain
            )
            new_bird.y_delta = 0
            new_bird.fitness = 0
            self.birds.append(new_bird)
        self.created_new_generation = True

    def refresh_game_after_new_generation(self):
        self.created_new_generation = False
        self.dt = 1
        pygame.event.clear()
        pygame.time.set_timer(NEW_PIPE_EVENT, 0)
        pygame.time.set_timer(NEW_PIPE_EVENT, 1400)
        pygame.event.post(pygame.event.Event(NEW_PIPE_EVENT))
        self.pipes = []
        self.closest_pipe_to_bird = None
        self.current_score = 0
        self.current_generation += 1

    def display_loading_screen(self):
        self.dt = self.clock.tick(30)
        self.screen.fill(SKY_BLUE)
        self.draw_menu()
        loading_text = self.main_font.render(f'Spawing Generation {self.current_generation + 1}', False, YELLOW)
        text_rect = loading_text.get_rect()
        text_rect.center = (GAME_SCREEN_WIDTH // 2, GAME_SCREEN_HEIGHT // 2 )
        self.screen.blit(loading_text, text_rect)
        #Need to check for events to get screen to update
        pygame.display.flip()
        for event in pygame.event.get():
            pass


 
if __name__ == "__main__":
    birds = [
        Bird(
            GAME_SCREEN_HEIGHT // 2,
            (random.randrange(0, 255), random.randrange(0, 255), random.randrange(0, 255))
        ) 
        for i in range(20)
    ]
    game = Game(birds)
    game.run()