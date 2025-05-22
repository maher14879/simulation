import numpy as np
from source.ecosystem import Creature

dna = [
    {
        "type": "motor"
    },
    {
        "type": "vision",
        "vision": {
            "fov": 170,
            "food": 1,
            "cell": -1
        }
    },
    {
        "type": "body"
    },
        {
        "type": "motor"
    },
        {
        "type": "body"
    },
        {
        "type": "body"
    }
]

creature = Creature(position=(0, 0), direction=np.random.rand(2) * 2 - 1, dna=dna)

herbivore = None 
carnivore = None
omnivore = None