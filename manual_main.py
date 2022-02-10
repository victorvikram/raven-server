"""
manual_main.py

Allows one to generate a RAVEN's tile by specifying the tree manually
"""
import numpy as np
import matplotlib.pyplot as plt
import json
import os
import sys
import argparse

sys.path.append(os.path.join(sys.path[0],'src','dataset'))
import src.dataset.const as const
import src.dataset.build_tree as build_tree
from src.dataset.rendering import render_panel
from src.dataset.AoT import (Root, Structure, Component, Layout, Entity)
from src.dataset.constraints import gen_entity_constraint, gen_layout_constraint

"""
None -> None

Given a list of tiles to generate, generates each and shows them
"""
def gen_specific(index, spec, save_dir):
    
    # load file with the square descriptions in json format
    if isinstance(spec, str):
        f = open(spec)
        spec = json.load(f)
        
    target = spec["target"]
    all_descs = spec["panels"]
    
    # make tree of panel and render
    image = np.zeros((16, 160, 160))
    for i, desc in enumerate(all_descs):
        if desc["structure"] == "center_single":
            root = gen_center_single(desc)
        elif desc["structure"] == "distribute_four":
            root = gen_distribute_x("four", desc)
        elif desc["structure"] == "distribute_nine":
            root = gen_distribute_x("nine", desc)
        elif desc["structure"] == "left_right":
            root = gen_bipartite("left_right", desc)
        elif desc["structure"] == "up_down":
            root = gen_bipartite("up_down", desc)
        elif desc["structure"] == "out_in":
            root = gen_bipartite("out_in", desc)
        elif desc["structure"] == "out_in_grid":
            root = gen_out_in_grid(desc)

        panel = render_panel(root)
        image[i,:,:] = panel

        """
        plt.figure(dpi=70)
        plt.imshow(panel, cmap='gray')
        plt.show()
        """
        
    
    """
    if not os.path.isdir(save_dir):
        os.mkdir(save_dir)
    
    np.savez(os.path.join(save_dir, "RAVEN_{}_test.npz".format(index)),
             image=image,
             target=target)
    """
    return image

"""
dict -> Root

Creates tree for the out_in_grid types structure
"""
def gen_out_in_grid(desc):

    # generate skeleton of the tree (without any specific entity attributes)
    root = build_tree.build_in_distribute_four_out_center_single(num_min=3, rand_positions=False)
    root.is_pg = True

    # handles to important nodes in the tree
    structure = root.children[0]
    out_component = structure.children[0]
    in_component = structure.children[1]
    out_layout = out_component.children[0]
    in_layout = in_component.children[0]
    
    # Add entities
    insert_entities(out_layout, desc["first_comp"])
    insert_entities(in_layout, desc["second_comp"])
    
    return root


"""
enum dict -> None

orientation - must be one of "out_in", "left_right", "up_down"

Creates tree for any bipartite structure (out_in, left_right, up_down)
"""
def gen_bipartite(orientation, desc):

    # generate skeleton of the tree (without any specific entity attributes)
    if orientation == "left_right":
        root = build_tree.build_left_center_single_right_center_single()
    elif orientation == "up_down":
        root = build_tree.build_up_center_single_down_center_single()
    elif orientation == "out_in":
        root = build_tree.build_in_center_single_out_center_single()
    
    root.is_pg = True

    # handles to important nodes in the tree
    structure = root.children[0]
    upleftout_layout = structure.children[0].children[0]
    downrightin_layout = structure.children[1].children[0]
    
    # Add entities
    insert_entities(upleftout_layout, desc["first_comp"])
    insert_entities(downrightin_layout, desc["second_comp"])

    return root

"""
enum dict -> None

n - must be one of "four", "nine"

Creates tree for any grid structure (distribute_nine, distribute_four)
"""
def gen_distribute_x(n, desc):
    
    # generate skeleton of the tree (without any specific entity attributes)
    if n == "four":
        root = build_tree.build_distribute_four(num_min=3, rand_positions=False)
    elif n == "nine":
        root = build_tree.build_distribute_nine(num_min=8, rand_positions=False)

    root.is_pg = True

    # handles to important nodes in the tree
    structure = root.children[0]
    component = structure.children[0]
    layout = component.children[0]

    # Add entities
    insert_entities(layout, desc["first_comp"])

    return root

"""
dict -> None

Creates tree for center_single structure
"""
def gen_center_single(desc):

    # generate skeleton of the tree (without any specific entity attributes)
    root = build_tree.build_center_single()
    root.is_pg = True

    # handles to important nodes in the tree
    structure = root.children[0]
    component = structure.children[0]
    layout = component.children[0]

    # Add entities
    insert_entities(layout, desc["first_comp"])

    return root

"""
Layout [dict] ->

given a layout object and a list of dictionaries describing entities, it places the
entities on the grid
"""
def insert_entities(layout, entity_descs):
    for entity_desc in entity_descs:
        entity_const = convert_to_entity_constraint(entity_desc)

        # get location for entity
        # when the entity is on a grid, location is always specified
        # if the entity is a singleton, then location is implicitly 0
        if "position" in entity_desc:
            position = entity_desc["position"]
        else:
            position = 1

        pos = layout.position.get_value()[position - 1]

        # create and add
        entity = Entity(str(position), bbox=pos, entity_constraint=entity_const)
        layout.insert(entity)

"""
dict ->

given a descriptiono of an entity, it produces constraints on the entity so that when
it is sampled, we get the correct one
"""
def convert_to_entity_constraint(entity_desc):

    # retrieve indices for the specified entity attributes
    type_index = entity_desc["type"] - 3
    size_index = entity_desc["size"]
    color_index = entity_desc["color"]
    angle_index = entity_desc["angle"] + 3

    # set them as constraints
    entity_const = gen_entity_constraint(type_min=type_index, type_max=type_index, 
                                        color_min=color_index, color_max=color_index,
                                        size_min=size_index, size_max=size_index,
                                        angle_min=angle_index, angle_max=angle_index)
    
    return entity_const
    

"""
example call:
python manual_main.py -d "/" -f "C:\\Users\vicvi\My Drive\active\analogy\Ravens\RAVEN\presets\simple_0.json" -i 0
"""
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--save-dir', '-d', type=str, required=True,
    help='the dataset dir')
    parser.add_argument('--spec-file', '-f', type=str, required=True,
    help='the dataset dir')
    parser.add_argument('--index', '-i', type=int, default=0,
    help='the dataset dir')

    args = parser.parse_args()

    gen_specific(args.index, args.spec_file, args.save_dir)


# TODO modify code to accept the new JSON format.

"""
JSON format:

[<PANEL> x 16]

Where <PANEL> is
{
        "structure": <STRUCTURE>,
        "first_comp": <COMPONENT>,
        "second_comp": <COMPONENT>,
}


If <STRUCTURE> is "center_single", "distribute_four", "distribute_nine":
"first_comp" contains all the entities

If <STRUCTURE> is "left_right", "up_down", "out_in", "out_in_grid":
"first_comp" contains the entities on the left/top/outside
"second_comp" contains the entities on the right/bottom/inside

<STRUCTURE> is one of 
- "center_single"
- "distribute_four"
- "distribute_nine"
- "left_right"
- "up_down"
- "out_in"
- "out_in_grid"

<COMPONENT> is 
[<ENTITY> x number]
Note: this is different from generate_custom because this format shows all entities explicitly


<ENTITY> is of the form
{
    "position": <INDEX>,
    "type": <TYPE>,
    "size": <SIZE>,
    "color": <COLOR>,
    "angle": <ANGLE>
}


If a singleton grid
<INDEX> must be 0. If unspecified, location will default to 0.

If a 2 by 2 grid
<INDEX> must be in 1..4
1 2
3 4

If a 3 by 3 grid
<INDEX> must be in 1..9
1 2 3
4 5 6
7 8 9

<TYPE> is one of 3..7, indicating number of sides (except 7, which is a circle)

<SIZE> is in 0..5, where 0 is small (0.4 scale) and 5 is large (0.9 scale)

<COLOR> is in 0..9, where 0 is white and 9 is black

<ANGLE> is in [-3, -2, -1, 0, 1, 2, 3, 4] 
n*45 gives the degrees of rotation for n in this range 

"""
