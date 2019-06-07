from nn import NeuralNetwork
from constants import *

# Helper function to map values before input into the NeuralNet
def transpose(value, leftMin, leftMax, rightMin, rightMax):
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin
    valueScaled = float(value - leftMin) / float(leftSpan)
    return rightMin + (valueScaled * rightSpan)

class Bird:
    def __init__(self, y_start, color, brain_model = None):
        self.x = GAME_SCREEN_WIDTH // 2
        self.y = y_start
        self.y_delta = 0
        self.color = color
        self.pipe = None
        #shape of our brain is 4 inputs, 1 hidden layer w/ 8 nodes, 2 outputs
        self.brain = NeuralNetwork(4, 8, 2, parent_weights=brain_model)
        self.fitness = 0
    
    def flap(self):
        if self.y_delta < 0:
            self.y_delta = 5
        if self.y_delta < 15:
            self.y_delta +=6
    
    def will_flap(self):
        if self.pipe is not None:
            x_delta, y1_delta, y2_delta = self.look_at_oncoming_pipe()
            self_delta = transpose(self.y_delta, -21, 21, -1, 1)
            x_delta = transpose(x_delta, 0, 388, -1, 1)
            y1_delta = transpose(y1_delta, 0, 470, -1, 1)
            y2_delta = transpose(y2_delta, 0, 470, -1, 1)
            return(self.brain.predict([x_delta, y1_delta, y2_delta, self_delta]))

    def look_at_oncoming_pipe(self):
        horizontal_distance_to_pipe = self.pipe.x + (PIPE_WIDTH // 2) - self.x
        vertical_distance_to_top_pipe = self.y - self.pipe.y
        vertical_distance_to_bottom_pipe = self.pipe.y + PIPE_GAP - self.y
        return (horizontal_distance_to_pipe, vertical_distance_to_top_pipe, vertical_distance_to_bottom_pipe)