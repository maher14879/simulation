from source.ecosystem import Ecosystem
from source.test import creature
import numpy as np
import pygame as pg
import json
import sys
import cProfile

def main():
    def quit():
        if ecosystem.creatures:
            world = {"dna_list": [creature.dna for creature in ecosystem.creatures], "position_list": [creature.position.tolist() for creature in ecosystem.creatures]}
            with open("world.json", "w") as file: json.dump(world, file)
        pg.quit()
        sys.exit()
    try: 
        with open("world.json", "rb") as file: world = json.load(file)
        dna_list = world["dna_list"] if "dna_list" in world else []
        position_list = world["position_list"] if "position_list" in world else []
    except: None

    ecosystem = Ecosystem(creatures=[creature], max_food=1000)
    clock = pg.time.Clock()

    while True:
        if not ecosystem.creatures: quit()
        ecosystem.tick()

        
        if not pg.mouse.get_pressed()[0] or ecosystem.tick_count % 100 == 0:
            dt = clock.tick()
            ecosystem.draw(dt, center=np.array(pg.mouse.get_pos()))

        for event in pg.event.get():
            if event.type == pg.QUIT:
                quit()

if __name__ == "__main__":
    pg.init()
    #cProfile.run("main()", sort="time")
    main()