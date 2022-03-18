import generate_custom as gc
import manual_main as mm

from PIL import Image
from datetime import datetime
import random
import os
import numpy as np
import json

def generate_progression_set(level="all", count=100):
    return generate_concept_set(concept="progression", level=level, count=count)

def generate_sameness_set(level="all", count=100):
    return generate_concept_set(concept="constant", level=level, count=count)

def generate_set(concept="base", level="all", count=100, genClass="base"):
    blueprints = []
    for i in range(count):

        if genClass == "position_row_col":
            blueprint = gc.generate_row_or_col_blueprint()
        elif genClass == "linecolor":
            blueprint = gc.generate_linecolor_blueprint()
        elif genClass == "linesize":
            blueprint = gc.generate_linesize_blueprint()
        elif genClass == "base":
            blueprint = gc.generate_random_blueprint()
        elif genClass == "outer_color":
            blueprint = gc.generate_outer_color_blueprint()
        
        if concept == "constant" or concept == "progression":
            blueprint = conceptify_blueprint(blueprint, level=level, concept=concept, constraint_class=genClass)
        
        blueprints.append(blueprint)
        
    
    return make_problems(blueprints)

def conceptify_blueprint(blueprint, level="all", concept="constant", constraint_class=None):
    if level == "all":
        prob = 1
    elif level == "boost":
        prob = 0.5

    if concept == "constant":
        concept = "constant!"

    comps = ["first_comp", "second_comp"] if "second_comp" in blueprint else ["first_comp"]
    for comp in comps:
        for attr in gc.generate_attr_list(blueprint[comp]):
            if random.random() < prob and blueprint[comp][attr] not in ["NA", "constant_hide"]:
                blueprint[comp][attr] = concept

    gc.decorate_relations(blueprint)
    gc.impose_constraints(blueprint, constraint_class=constraint_class)
    
    # make sure there is at least one realtion that matches the concept
    acc = gc.iterate_through_attrs(blueprint, lambda rel, acc : acc or (concept in rel), False)

    if not acc:
        comp = random.choice(comps)
        attr = random.choice(["type", "color", "size"])
        blueprint[comp][attr] = concept
        gc.decorate_relations(blueprint)
    
    return blueprint


def make_problems(blueprints):
    now = datetime.now()
    current_time = now.strftime("%m-%d-%H-%M-%S-%f")
    
    dirname = os.path.join("files", current_time)
    os.mkdir(dirname)
    
    for i, blueprint in enumerate(blueprints):
        initial = gc.generate_initials(blueprint, human=True)
        literal = gc.generate_concrete_json(blueprint, initial, human=True)
        literal["human"] = True

        arr, target = mm.gen_specific(literal)

        filename = os.path.join("files", current_time, f"RAVEN_{i}")
        np.savez(filename,
             image=arr,
             target=target)
        
        img = arr_to_img(arr)
        img.save(filename + ".jpg", format="JPEG")
        with open(filename + ".json", "w") as f:
            json.dump(literal, f, indent=4)
    
    return dirname

# image generating functions
def construct_array_context(images):
    return construct_array(images, 3, 3)
    
def construct_array_answers(images):
    return construct_array(images, 3, 3)
    
def construct_array(images, rows, cols):
    
    tile_size = images.shape[1]
    cushion = int(tile_size/20)
    
    full_image = np.zeros((tile_size*rows + cushion*(rows - 1), tile_size*cols + cushion*(cols - 1)))
    
    for row in range(rows):
        for col in range(cols):
            index = col + cols*row
            
            if index < images.shape[0]:
                img = images[index,:,:]
            else:
                img = np.ones((tile_size, tile_size))*200
            
            place_at_coords(full_image, img, cushion, row, col)
    
    
    return full_image

def pixel_arrs_to_img(context_arr, answers_arr):
    context_image = Image.fromarray(np.uint8(context_arr), mode="L")
    answers_image = Image.fromarray(np.uint8(answers_arr), mode="L")
    
    context_width = context_image.size[0]
    context_height = context_image.size[1]
    answers_width = answers_image.size[0]
    answers_height = answers_image.size[1]
    padding = int(context_width/20)
    ratio = context_width/answers_width
    
    answers_image = answers_image.resize((context_width, round(answers_height*ratio)))
    
    
    full_image = Image.new('L',(2*padding + context_width, 3*padding + context_height + answers_image.size[1]), 0)
    full_image.paste(context_image, (padding, padding))
    full_image.paste(answers_image, (padding, 2*padding + context_height))
    
    return full_image
    

def arr_to_img(arr):
    context_arr = construct_array_context(arr[:8,:,:])
    answers_arr = construct_array_answers(arr[8:,:,:])
    
    return pixel_arrs_to_img(context_arr, answers_arr)

def place_at_coords(full_image, tile, cushion, row_index, col_index):
    tile_size = tile.shape[0]
    
    row_start_pixel = row_index * (tile_size + cushion)
    row_end_pixel = row_start_pixel + tile_size
    
    col_start_pixel = col_index * (tile_size + cushion)
    col_end_pixel = col_start_pixel + tile_size
    
    full_image[row_start_pixel:row_end_pixel, col_start_pixel:col_end_pixel] = tile

if __name__ == "__main__":
    generate_sameness_set(level="all", count=10)
