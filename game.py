import random
from copy import deepcopy

import pygame
import numpy as np
# import tensorflow as tf

from bird import Bird
from pipe import Pipe
from constants import *

pygame.init()
pygame.font.init()
pygame.display.set_caption("Flappy Bird: NeuroEvolution")

NEW_PIPE_EVENT = pygame.USEREVENT + 1
MAIN_FONT = pygame.font.Font(None, FONT_SIZE)
LARGE_FONT = pygame.font.Font(None, FONT_SIZE * 2)

class Game():
    def __init__(self, birds):
        pygame.event.post(pygame.event.Event(NEW_PIPE_EVENT))
        pygame.time.set_timer(NEW_PIPE_EVENT, 1400) #

        self.done = False
        self.created_new_generation = False
        self.clock = pygame.time.Clock()
        self.pipes = []
        self.closest_pipe_to_bird = None
        self.birds = birds
        self.screen = pygame.display.set_mode([SCREEN_WIDTH, GAME_SCREEN_HEIGHT])
        self.dt = 0
        self.current_generation = 1
        self.current_score = 0
        self.fittest_bird_so_far = {
            'brain': None,
            'fitness': 0,
            'generation': 0,
            'color': None,
            'score': 0
        }
        self.fittest_bird_current_gen = {
            'brain': None,
            'fitness': 0,
            'generation': 0,
            'color': None,
            'score': 0
        }
        self.update_menu_text_values()

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
                self.create_new_generation()
            
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
        
        self.current_score_text = LARGE_FONT.render(f'{self.current_score}', False, YELLOW)

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
        if bird.y > GAME_SCREEN_HEIGHT + 50 or bird.y < -50:
            del self.birds[bird_idx]

    def capture_last_bird_remaining(self, fit_bird):
        self.fittest_bird_current_gen['brain'] = fit_bird.brain.get_blueprint()
        # print(fit_bird.brain.model.get_weights())
        # print(type(fit_bird.brain.model.get_weights()))
        # for item in fit_bird.brain.model.get_weights():
        #     print(type(item), item.shape)
        self.fittest_bird_current_gen['fitness'] = fit_bird.fitness
        self.fittest_bird_current_gen['score'] = self.current_score
        self.fittest_bird_current_gen['generation'] = self.current_generation
        self.fittest_bird_current_gen['color'] = fit_bird.color
        if self.current_score > 0:
            if self.fittest_bird_so_far['brain'] is None or fit_bird.fitness > self.fittest_bird_so_far['fitness']:
                self.fittest_bird_so_far = deepcopy(self.fittest_bird_current_gen)

    def update_menu_text_values(self):

        self.generation_text = MAIN_FONT.render(f'Generation : {self.current_generation}', False, WHITE)

        self.fittest_bird_text_1 = MAIN_FONT.render(f'Fittest Bird So Far:', False, WHITE)
        self.fittest_bird_text_2 = MAIN_FONT.render(f"Score: {self.fittest_bird_so_far['score']}", False, YELLOW)
        self.fittest_bird_text_3 = MAIN_FONT.render(f"Gen: {self.fittest_bird_so_far['generation']}", False, WHITE)

        self.fittest_bird_text_4 = MAIN_FONT.render(f'Fittest in Prev Gen:', False, WHITE)
        self.fittest_bird_text_5 = MAIN_FONT.render(f"Score: {self.fittest_bird_current_gen['score']}", False, YELLOW)
        self.fittest_bird_text_6 = MAIN_FONT.render(f"Gen: {self.fittest_bird_current_gen['generation']}", False, WHITE)

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
            if pipe.bottom_color == ACTIVE_GREEN:
                pygame.draw.circle(self.screen, BLACK, [int(pipe.x + (PIPE_WIDTH // 2)), int(pipe.y)], 5)
                pygame.draw.circle(self.screen, BLACK, [int(pipe.x + (PIPE_WIDTH // 2)), int(pipe.y + PIPE_GAP)], 5)
        
        text_rect = self.current_score_text.get_rect()
        text_rect.center = (GAME_SCREEN_WIDTH - FONT_SIZE * 2 , 0 + FONT_SIZE * 2 // 2 )
        self.screen.blit(self.current_score_text, text_rect)

    def draw_menu(self):
        
        pygame.draw.rect(self.screen, BLACK, (GAME_SCREEN_WIDTH, 0, GAME_MENU_WIDTH, GAME_SCREEN_HEIGHT))
        text_rect = self.generation_text.get_rect()
        text_rect.center = ((GAME_SCREEN_WIDTH + SCREEN_WIDTH) // 2, 0 + FONT_SIZE // 2 )
        self.screen.blit(self.generation_text, text_rect)

        if self.fittest_bird_so_far['brain'] is not None:
            fittest_bird_text_1 = self.fittest_bird_text_1.get_rect()
            fittest_bird_text_1.center = ((GAME_SCREEN_WIDTH + SCREEN_WIDTH) // 2, 50 + FONT_SIZE // 2 )
            self.screen.blit(self.fittest_bird_text_1, fittest_bird_text_1)
            pygame.draw.circle(self.screen, self.fittest_bird_so_far['color'], [GAME_SCREEN_WIDTH + 50, 118], BIRD_SIZE)

            fittest_bird_text_2 = self.fittest_bird_text_2.get_rect()
            fittest_bird_text_2.center = (((GAME_SCREEN_WIDTH + SCREEN_WIDTH) // 2) - 25, 88 + FONT_SIZE // 2 )
            self.screen.blit(self.fittest_bird_text_2, fittest_bird_text_2)

            fittest_bird_text_3 = self.fittest_bird_text_3.get_rect()
            fittest_bird_text_3.center = (((GAME_SCREEN_WIDTH + SCREEN_WIDTH) // 2) - 33, 88 + FONT_SIZE + 10 )
            self.screen.blit(self.fittest_bird_text_3, fittest_bird_text_3)

            fittest_bird_text_4 = self.fittest_bird_text_4.get_rect()
            fittest_bird_text_4.center = ((GAME_SCREEN_WIDTH + SCREEN_WIDTH) // 2, 50 + FONT_SIZE // 2 + 100 )
            self.screen.blit(self.fittest_bird_text_4, fittest_bird_text_4)
            pygame.draw.circle(self.screen, self.fittest_bird_current_gen['color'], [GAME_SCREEN_WIDTH + 50, 118 + 100], BIRD_SIZE)

            fittest_bird_text_5 = self.fittest_bird_text_5.get_rect()
            fittest_bird_text_5.center = (((GAME_SCREEN_WIDTH + SCREEN_WIDTH) // 2) - 25, 88 + FONT_SIZE // 2 + 100 )
            self.screen.blit(self.fittest_bird_text_5, fittest_bird_text_5)

            fittest_bird_text_6 = self.fittest_bird_text_6.get_rect()
            fittest_bird_text_6.center = (((GAME_SCREEN_WIDTH + SCREEN_WIDTH) // 2) - 33, 88 + FONT_SIZE + 10 + 100 )
            self.screen.blit(self.fittest_bird_text_6, fittest_bird_text_6)
    
    def display_loading_screen(self):
        self.dt = self.clock.tick(30)
        self.screen.fill(SKY_BLUE)
        self.update_menu_text_values()
        self.draw_menu()
        loading_text = MAIN_FONT.render(f'Spawning Generation {self.current_generation + 1}', False, YELLOW)
        text_rect = loading_text.get_rect()
        text_rect.center = (GAME_SCREEN_WIDTH // 2, GAME_SCREEN_HEIGHT // 2 )
        self.screen.blit(loading_text, text_rect)
        #Need to check for events to get screen to update
        pygame.display.flip()
        for event in pygame.event.get():
            pass

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

    def create_new_generation(self):
        # tf.keras.backend.clear_session()
        for i in range(20):
            new_bird = Bird(
                GAME_SCREEN_HEIGHT // 2,
                (random.randrange(0, 255), random.randrange(0, 255), random.randrange(0, 255)),
                # Half of new birds are mutated from the fittest bird ever
                # Other half are mutated from the fittest bird in last generation
                brain_model= self.fittest_bird_so_far['brain'] if i % 2 == 0 else self.fittest_bird_current_gen['brain']
            )
            self.birds.append(new_bird)
        self.created_new_generation = True


 
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