import generate_custom as gc
import manual_main as mm

from datetime import datetime
import random
import os
import numpy as np

def generate_progression_set(level="all", count=100):
    return generate_concept_set(concept="progression", level=level, count=count)

def generate_sameness_set(level="all", count=100):
    return generate_concept_set(concept="constant", level=level, count=count)

def generate_concept_set(concept="constant", level="all", count=100):
    if concept == "constant":
        concept = "constant!"
    
    if level == "all":
        prob = 1
    elif level == "boost":
        prob = 0.5
    
    blueprints = []
    for i in range(count):
        blueprint = gc.generate_random_blueprint()
        comps = ["first_comp", "second_comp"] if "second_comp" in blueprint else ["first_comp"]
        for comp in comps:
            for attr in blueprint[comp]:
                if random.random() < prob:
                    blueprint[comp][attr] = concept

        gc.decorate_relations(blueprint)
        gc.impose_constraints(blueprint)
        
        # make sure there is at least one realtion that matches the concept
        acc = gc.iterate_through_attrs(blueprint, lambda rel, acc : acc or (concept in rel), False)

        if not acc:
            comp = random.choice(comps)
            attr = random.choice(["type", "color", "size"])
            blueprint[comp][attr] = concept
            gc.decorate_relations(blueprint)

        blueprints.append(blueprint)

    return generate_set(blueprints)

def generate_set(blueprints):
    now = datetime.now()
    current_time = now.strftime("%m-%d-%H-%M-%S-%f")
    
    dirname = os.path.join("files", current_time)
    os.mkdir(dirname)
    
    for i, blueprint in enumerate(blueprints):
        initial = gc.generate_initials(blueprint, human=True)
        literal = gc.generate_concrete_json(blueprint, initial, human=True)
        literal["human"] = True

        img, target = mm.gen_specific(literal)

        filename = os.path.join("files", current_time, f"RAVEN_{i}")
        np.savez(filename,
             image=img,
             target=target)
    
    return dirname

if __name__ == "__main__":
    generate_sameness_set(level="all", count=10)
