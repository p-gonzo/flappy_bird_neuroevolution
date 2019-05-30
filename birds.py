import random
from game import main, Bird, SCREEN_HEIGHT

birds = [
        Bird(
            random.randrange(100, SCREEN_HEIGHT - 100),
            (random.randrange(0, 255), random.randrange(0, 255), random.randrange(0, 255))
        ) 
        for i in range(11)
    ]

main(birds)