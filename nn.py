from copy import deepcopy
import tensorflow as tf
import numpy as np

class NeuralNetwork():
    def __init__(self, input_nodes, hidden_nodes, output_nodes, model=None):
        if model == None:
            inputs = tf.keras.Input(shape=(input_nodes,))
            x = tf.keras.layers.Dense(hidden_nodes, activation=tf.nn.relu)(inputs)
            outputs = tf.keras.layers.Dense(output_nodes, activation=tf.nn.softmax)(x)
            self.model = tf.keras.Model(inputs=inputs, outputs=outputs)
        else:
            self.model = model
            self.mutate(0.75)

    def predict(self, inputs):
        xs = np.array([inputs])
        y_pred = self.model.predict(xs)[0]
        return y_pred[0] > y_pred[1]
    
    def mutate(self, rate):
        current_weights = self.model.get_weights()
        mutated_weights = deepcopy(current_weights)
        def recursively_mutate(obj):
            for item_idx, item in enumerate(obj):
                if isinstance(item, (list, np.ndarray)):
                    recursively_mutate(item)
                else:
                    if np.random.random() < rate:
                        print('mutate')
                        obj[item_idx] = item + np.random.normal(scale=3)
        recursively_mutate(mutated_weights)
        self.model.set_weights(mutated_weights)
            
