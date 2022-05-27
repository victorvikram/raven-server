import generate_custom as gc
import manual_main as mm

from PIL import Image
from datetime import datetime
import random
import os
import numpy as np
import json


import string
from PIL import ImageFont
from PIL import ImageDraw


def generate_progression_set(level="all", count=100):
    return generate_concept_set(concept="progression", level=level, count=count)

def generate_sameness_set(level="all", count=100):
    return generate_concept_set(concept="constant", level=level, count=count)

def generate_set(concept="base", level="all", count=100, genClass="base", structure="any", only_concept=True):
    blueprints = []
    print("in generate set", structure)

    for i in range(count):
        
        last_blueprint = None
        if genClass == "position_row_col":
            blueprint = gc.generate_row_or_col_blueprint(structure=structure)
        elif genClass == "linecolor":
            blueprint = gc.generate_linecolor_blueprint(structure=structure)
        elif genClass == "linesize":
            blueprint = gc.generate_linesize_blueprint(structure=structure)
        elif genClass == "base":
            if structure == "any":
               blueprint = gc.generate_random_blueprint() 
            else:
                blueprint = gc.generate_random_blueprint(structure_list=[structure])
        elif genClass == "outer_color":
            blueprint = gc.generate_outer_color_blueprint(structure=structure)
        elif genClass == "slippage":
            blueprint, last_blueprint = gc.generate_slippage_blueprint(structure=structure)
        elif genClass == "switch_comps":
            blueprint = gc.generate_switcheroo_blueprint(structure=structure)
        
        if (concept == "constant" or concept == "progression") and level != "none":
            blueprint = conceptify_blueprint(blueprint, level=level, concept=concept, constraint_class=genClass, only_concept=only_concept)
        
        blueprints.append((blueprint, last_blueprint))
        
    
    return make_problems(blueprints, comp_symmetry=(genClass == "switch_comps"))

def conceptify_blueprint(blueprint, level="all", concept="constant", constraint_class=None, only_concept=True):
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
            elif blueprint[comp][attr] not in ["NA", "constant_hide", "constant", "random", "constant!"]:
                if only_concept:
                    blueprint[comp][attr] = "random"


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


def make_problems(blueprints, comp_symmetry=False):
    print(blueprints)
    now = datetime.now()
    current_time = now.strftime("%m-%d-%H-%M-%S-%f")
    
    dirname = os.path.join("files", current_time)
    os.mkdir(dirname)
    
    for i, blueprint_pair in enumerate(blueprints):
        blueprint = blueprint_pair[0]
        last_blueprint = blueprint_pair[1]

        initial = gc.generate_initials(blueprint, human=True, last_blueprint=last_blueprint)
        literal = gc.generate_concrete_json(blueprint, initial, human=True, last_blueprint=last_blueprint, comp_symmetry=comp_symmetry)
        literal["human"] = True

        arr, target = mm.gen_specific(literal)

        filename = os.path.join("files", current_time, f"RAVEN_test_{i}")
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
    return construct_array(images, 3, 3, answers=True)
    
def construct_array(images, rows, cols, answers=False):
    
    tile_size = images.shape[1]
    cushion = int(tile_size/20)
    vert_cushion = int(tile_size/5) if answers else cushion
    
    full_image = np.zeros((tile_size*rows + vert_cushion*rows + cushion, tile_size*cols + cushion*(cols + 1)))

    gray_box = np.ones((cushion*4, cushion*4))*200
    
    for row in range(rows):
        for col in range(cols):
            index = col + cols*row
            
            if index < images.shape[0]:
                img = images[index,:,:]
            else:
                img = np.ones((tile_size, tile_size))*200
            
            place_at_coords(full_image, img, cushion, vert_cushion, row, col)
            
            
            number = char_to_pixels(str(index + 1), "C:\\Windows\\Fonts\\cour.ttf")
            
            box = np.zeros((cushion*4, cushion*4))
            box[box.shape[0] - number.shape[0]:, box.shape[1] - number.shape[1]:box.shape[1]] = number
            box = np.where(box, 0, 200)
            
            if answers and index != 8:
                place_at_coords(full_image, box, cushion, vert_cushion, row, col, offset=True, grid_size=tile_size)
            
    
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
    
    
    full_image = Image.new('L',(context_width, context_height + answers_image.size[1]), 0)
    full_image.paste(context_image, (0, 0))
    full_image.paste(answers_image, (0, context_height))
    
    return full_image
    

def arr_to_img(arr):
    context_arr = construct_array_context(arr[:8,:,:])
    answers_arr = construct_array_answers(arr[8:,:,:])
    
    return pixel_arrs_to_img(context_arr, answers_arr)

def place_at_coords(full_image, tile, cushion, vert_cushion, row_index, col_index, grid_size=None, offset=False):
    tile_size = tile.shape[0]
    if grid_size is None:
        grid_size = tile_size
        
    row_start_pixel = vert_cushion + row_index * (grid_size + vert_cushion) - offset * int(0.75 * tile_size)
    row_end_pixel = row_start_pixel + tile_size
    
    col_start_pixel = cushion + col_index * (grid_size + cushion)  
    col_end_pixel = col_start_pixel + tile_size
    
    full_image[row_start_pixel:row_end_pixel, col_start_pixel:col_end_pixel] = tile

def char_to_pixels(text, path='arialbd.ttf', fontsize=50):
    """
    Based on https://stackoverflow.com/a/27753869/190597 (jsheperd)
    """
    font = ImageFont.truetype(path, fontsize) 
    w, h = font.getsize(text)  
    h *= 2
    image = Image.new('L', (w, h), 1)  
    draw = ImageDraw.Draw(image)
    draw.text((0, 0), text, font=font) 
    arr = np.asarray(image)
    arr = np.where(arr, 0, 1)
    arr = arr[(arr != 0).any(axis=1)]
    return arr

if __name__ == "__main__":
    generate_sameness_set(level="all", count=10)
