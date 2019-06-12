from copy import deepcopy
import numpy as np

from constants import *

class BirdBrain:
    def __init__(self, parent_blueprint = None):
        if parent_blueprint is not None:
            self.copy_brain_blueprint(parent_blueprint)
            self.mutate(MUTATION_RATE, MUTATION_VARIANCE_LOW, MUTATION_VARIANCE_HIGH)
        else:
            # Initialize random brain structure
            self.dense_layer_weights = np.random.normal(scale=0.5, size=(4,8))
            self.dense_layer_biases = np.zeros(8)
            self.output_layer_weights = np.random.normal(scale=0.5, size=(8,2))
            self.output_layer_biases = np.zeros(2)
        
    def copy_brain_blueprint(self, parent_blueprint):
        self.dense_layer_weights = deepcopy(parent_blueprint["dense_layer_weights"])
        self.dense_layer_biases = deepcopy(parent_blueprint["dense_layer_biases"])
        self.output_layer_weights = deepcopy(parent_blueprint["output_layer_weights"])
        self.output_layer_biases = deepcopy(parent_blueprint["output_layer_biases"])
    
    def mutate(self, mutation_rate, variance_low, variance_high):
        for set_idx, weight_set in enumerate(self.dense_layer_weights):
            for weight_idx, weight in enumerate(weight_set):
                if np.random.random() < mutation_rate:
                    self.dense_layer_weights[set_idx][weight_idx] += np.random.normal() * np.random.uniform(low=variance_low, high=variance_high)
        for weight_idx, weight in enumerate(self.dense_layer_biases):
            if np.random.random() < mutation_rate:
                self.dense_layer_biases[weight_idx] += np.random.normal() * np.random.uniform(low=variance_low, high=variance_high)
        for set_idx, weight_set in enumerate(self.output_layer_weights):
            for weight_idx, weight in enumerate(weight_set):
                if np.random.random() < mutation_rate:
                    self.output_layer_weights[set_idx][weight_idx] += np.random.normal() * np.random.uniform(low=variance_low, high=variance_high)
        for weight_idx, weight in enumerate(self.output_layer_biases):
            if np.random.random() < mutation_rate:
                self.output_layer_biases[weight_idx] += np.random.normal() * np.random.uniform(low=variance_low, high=variance_high)
                
    def get_blueprint(self):
        return {
            "dense_layer_weights": self.dense_layer_weights,
            "dense_layer_biases": self.dense_layer_biases,
            "output_layer_weights": self.output_layer_weights,
            "output_layer_biases": self.output_layer_biases
        }
    
    def predict(self, input_layer):
        input_layer = np.array(input_layer)
        dense_layer = input_layer.dot(self.dense_layer_weights) + self.dense_layer_biases
        # ReLU activation
        dense_layer = np.maximum(dense_layer, np.zeros(8))
        output_layer = dense_layer.dot(self.output_layer_weights) + self.output_layer_biases
        # Softmax
        output_layer = [np.exp(value) / sum(np.exp(output_layer)) for value in output_layer]
        return output_layer[0] > output_layer[1]
            
