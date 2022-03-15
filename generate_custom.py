"""
input 1:
<BLUEPRINT>, which is
{
    "structure": <STRUCTURE>,
    "first_comp": <RULESET>,
    "second_comp": <RULESET>
}

Where <STRUCTURE> is one of 
"center_single", "distribute_four", "distribute_nine",
"left_right", "up_down", "out_in", "out_in_grid"


Where <RULESET> is
{
    "number": <RELATION>,
    "position": <RELATION>,
    "type": <RELATION>,
    "size": <RELATION>,
    "color": <RELATION> 
}

Where <RELATION> is one of
"progression_1", "progression_2", "progression_-2", "progression_-1" / "progression-up", "progression-down"
"consistent_union", 
"constant", 
"arithmetic_add", "arithmetic_sub"

input 2:
[<PANEL> x 3]

Where <PANEL> is 
{
        "structure": <STRUCTURE>,
        "first_comp": <COMPONENT>,
        "second_comp": <COMPONENT>,
}

And <COMPONENT> is 
{   
    "uniformity": True/False,
    "entities": [<ENTITY> x number]
}
or, when first input 
[<ENTITY> x number]

Where <ENTITY> 
{
    "position": <NUMBER>
    "type": <TYPE>,
    "size": <SIZE>,
    "color": <COLOR>,
    "angle": <ANGLE>
}

Constraints - 
<INITIAL>
- has length 1 if structure is "center_single", "distribute_four", "distribute_nine", otherwise, length 2

<RULESET>
- can't have non-constant relations on both number and position
- can't have arithmetic on type
- can't have non-constant number or position on a center layout

<ENTITY>
- "position" one of the positions listed in the layout, MECE
"""

import sys
import copy
import random
import numpy as np

def generate_linecolor_blueprint():
    blueprint = generate_random_blueprint(structure_list=["center_single", "distribute_four", "left_right", "up_down", "out_in"],
                                            attr_list=["position", "number", "size", "type", "color", "linecolor"])
    
    comps = ["first_comp", "second_comp"] if "second_comp" in blueprint else ["first_comp"]

    for comp in comps:
        blueprint[comp]["linesize"] = "constant!"
        blueprint[comp]["initials"]["linesize"] = 4
    

def generate_row_or_col_blueprint():
    blueprint = generate_random_blueprint(structure_list=["distribute_nine"])
    blueprint["first_comp"]["position"] = "NA"
    blueprint["first_comp"]["number"] = "NA"
    row_or_col = random.choice(["position_row", "position_col"])

    blueprint["first_comp"][row_or_col] = random.choice(["progression", "constant", "consistent_union"])
    decorate_relations(blueprint)

    print(blueprint)
    return blueprint

# string -> dict
# generates a random blueprint for a given structure, where the structure is sampled uniformly at random and relations are too, subject to constraints
def generate_random_blueprint(structure_list=["center_single", "distribute_four", "distribute_nine", "left_right", "up_down", "out_in", "out_in_grid"],
                                attr_list=["position", "number", "size", "type", "color"]):
    
    structure = random.choice(structure_list)
    components = ["first_comp"] if structure in ["center_single", "distribute_four", "distribute_nine"] else ["first_comp", "second_comp"]
    rel_list = ["progression", "consistent_union", "arithmetic", "constant"]
    
    blueprint = {"structure": structure}
    for comp in components:
        blueprint[comp] = {}
        for attr in attr_list:
            blueprint[comp][attr] = random.choice(rel_list)

    decorate_relations(blueprint)
    impose_constraints(blueprint)
    uniformity = random.choice([True, False, None])

    if uniformity is not None:
        blueprint["uniformity"] = uniformity
    
    return blueprint

def iterate_through_attrs(blueprint, func, acc):
    comps = ["first_comp", "second_comp"] if "second_comp" in blueprint else ["first_comp"]
    for comp in comps:
        for attr in blueprint[comp]:
            acc = func(blueprint[comp][attr], acc)
    
    return acc



# string string dict ->
# modifies the *blueprint* so that the relations are decorated with their subtype (e.g. "progression" becomes "progression_-1")
def decorate_relations(blueprint):
    comps = ["first_comp", "second_comp"] if "second_comp" in blueprint else ["first_comp"]
    for comp in comps:
        for attr in ["position", "number", "size", "type", "color", "position_row", "position_col"]:
            if attr not in blueprint[comp]:
                continue
            if blueprint[comp][attr] == "progression" and attr in ["position_row", "position_col"]:
                increment = random.choice(["-1", "1"])
                blueprint[comp][attr] = "progression_" + increment
            elif blueprint[comp][attr] == "progression":
                increment = random.choice(["-2", "-1", "1", "2"])
                blueprint[comp][attr] = "progression_" + increment

            elif blueprint[comp][attr] == "arithmetic":
                direction = random.choice(["add", "sub"])
                blueprint[comp][attr] = "arithmetic_" + direction
    
# string string dict ->
# modifies *blueprint* so that it satisfies constraints on what kinds of relations are permissible on what attributes
def impose_constraints(blueprint):
    structure = blueprint["structure"]

    comps = ["first_comp", "second_comp"] if "second_comp" in blueprint else ["first_comp"]

    for comp in comps:
        if structure in ["center_single",  "left_right", "up_down", "out_in"] or (structure == "out_in_grid" and comp == "first_comp"):
            blueprint[comp]["position"] = "constant"
            blueprint[comp]["number"] = "constant"
        else:
            pos_or_number = random.choice(["number", "position"])
            blueprint[comp][pos_or_number] = "NA"
        
        if structure in ["out_in", "out_in_grid"] and comp == "first_comp":
            blueprint[comp]["color"] = "constant"

    
        if structure in ["out_in_grid", "distribute_four"] and ("progression" in blueprint[comp]["number"]):
            if int(blueprint[comp]["number"].split("_")[1]) > 0:
                blueprint[comp]["number"] = "progression_1"
            else:
                blueprint[comp]["number"] = "progression_-1"
        
        if "arithmetic" in blueprint[comp]["type"]:
            new_relation = random.choice(["constant", "progression", "consistent_union"])
            blueprint[comp]["type"] = new_relation
            decorate_relations(blueprint)

def sample_posns(structure, comp, pos_attr="position", rel="", ind=None):
    if pos_attr in ["position_row", "position_col"]:
        number_to_select = random.choice([1, 2, 3])
        row_or_col = pos_attr.split("_")[1]
        eligible_posns = get_pos_options_for_row_or_col(ind, row_or_col)

    else:
        number_to_select = random.choice(range_of_values(pos_attr, structure, comp))
        eligible_posns = eligible_values(structure, comp, pos_attr, rel=rel)
    
    posns = random.sample(eligible_posns, number_to_select)
    posns.sort()
    return tuple(posns)

def generate_initials(blueprint, human=False):
    structure = blueprint["structure"]
    components = ["first_comp"] if blueprint["structure"] in ["center_single", "distribute_four", "distribute_nine"] else ["first_comp", "second_comp"]

    prev_used = {comp: {attr: set() for attr in ["position", "number", "size", "type", "color", "angle", "position_row", "position_col"]} for comp in components}

    initials = []
    for i in range(3):
        if "uniformity" in blueprint:
            uniformity = blueprint["uniformity"]
        else:
            uniformity = random.choice([True, False])

        panel = {"structure": structure} 
        for comp in components:
            rels = blueprint[comp]
            rels["angle"] = "NA"

            contains_initials = ("initials" in blueprint[comp])

            # TODO fix this, it doesn't prevent equal positions
            if rels["position"] not in ["constant", "constant!", "NA"]:
                posns = sample_posns(structure, comp)

                if rels["position"] == "consistent_union":
                    while posns in prev_used[comp]["position"]:
                        posns = sample_posns(structure, comp)
                        
                    prev_used[comp]["position"].add(tuple(posns))
            elif "position_row" in rels:
                if contains_initials and "position_row" in blueprint[comp]["initials"]:
                    ind = blueprint[comp]["initials"]["position_row"]
                else:
                    ind = random.choice(eligible_values(structure, comp, "position_row", rels["position_row"], used_vals=prev_used[comp]["position_row"], human=human))
                
                posns = sample_posns(structure, comp, pos_attr="position_row", rel=rels["position_row"], ind=ind)

                if rels["position_row"] == "consistent_union":
                    prev_used[comp]["position_row"].add(ind)
            elif "position_col" in rels:
                if contains_initials and "position_col" in blueprint[comp]["initials"]:
                    ind = blueprint[comp]["initials"]["position_col"]
                else:
                    ind = random.choice(eligible_values(structure, comp, "position_col", rels["position_col"], used_vals=prev_used[comp]["position_col"], human=human))

                posns = sample_posns(structure, comp, pos_attr="position_col", rel=rels["position_col"], ind=ind)
                if rels["position_col"] == "consistent_union":
                    prev_used[comp]["position_col"].add(ind)
            else:
                if contains_initials and "number" in blueprint[comp]["initials"]:
                    number = blueprint[comp]["initials"]["number"]
                else:
                    eligible_vals = eligible_values(structure, comp, "number", rels["number"], used_vals=prev_used[comp]["number"], human=human)
                    number = random.choice(eligible_vals)

                if rels["number"] == "consistent_union":
                    prev_used[comp]["number"].add(number)
                
                posns = random.sample(eligible_values(structure, comp, "position", rels["position"], human=human), number)
 
            const_attrs = {}  
            for attr in ["type", "size", "color", "angle"]:
                # when uniformity is true or there is a relation on the attributes, choose a single value across the whole panel
                # or when the initial value is specified
                if uniformity or (rels[attr] not in ["constant", "NA", "random"]) or (contains_initials and attr in blueprint[comp]["initials"]):
                    if contains_initials and attr in blueprint[comp]["initials"]:
                        val = blueprint[comp]["initials"][attr]
                    else:
                        eligible_vals = eligible_values(structure, comp, attr, rels[attr], used_vals=prev_used[comp][attr], human=human)
                        val = random.choice(eligible_vals)

                    const_attrs[attr] = val

                    if attr != "angle" and rels[attr] == "consistent_union":
                        prev_used[comp][attr].add(val)

            entities = []
            for i, posn in enumerate(posns):
                entity = {}
                entity["position"] = posn
                for attr in ["size", "color", "type", "angle"]:
                    if attr in const_attrs:
                        entity[attr] = const_attrs[attr]
                    else:
                        entity[attr] = random.choice(eligible_values(structure, comp, attr, rels[attr], human=human))
                
                entities.append(entity)
            
            panel[comp] = {}
            panel[comp]["entities"] = entities
            panel[comp]["uniformity"] = uniformity
        
        initials.append(panel)
    
    return initials

# ~tested~
def eligible_values(structure, comp, attr, rel="", used_vals=None, human=False):
    if structure in ["out_in_grid", "out_in"] and comp == "first_comp" and attr == "color":
        return [0]

    elif (structure in ["center_single",  "left_right", "up_down", "out_in"] or (structure == "out_in_grid" and comp == "first_comp")) and attr in ["position", "number"]:
        return [1]

    elif "progression" in rel and "position" not in attr and attr != "angle":
        inc = int(rel.split("_")[1])
        max_final = max(range_of_values(attr, structure, comp, human))
        min_final = min(range_of_values(attr, structure, comp, human))
        max_initial = min(max_final - inc * 2, max_final)
        min_initial = max(min_final - inc * 2, min_final)

        return list(range(min_initial, max_initial + 1))

    elif "arithmetic" in rel and attr != "position" and attr != "angle":
        direction = rel.split("_")[1]
        if direction == "add":
            min_val = min(range_of_values(attr, structure, comp, human))
            max_val = max(range_of_values(attr, structure, comp, human)) - min_val
        elif direction == "sub":
            min_val = min(range_of_values(attr, structure, comp, human))*2
            max_val = max(range_of_values(attr, structure, comp, human))

        return list(range(min_val, max_val + 1))
    
    elif "consistent_union" == rel and attr != "position" and attr != "angle":
        eligible_values = [val for val in range_of_values(attr, structure, comp, human) if val not in used_vals]
        return eligible_values

    elif "progression" in rel and (attr == "position_row" or attr == "position_col"):
        if int(rel.split("_")[1]) == 1:
            return [0]
        elif int(rel.split("_")[1]) == -1:
            return [2]

    else:
        return range_of_values(attr, structure, comp, human)
    
    
# dict dict -> dict
# takes a problem *blueprint* (a structure and what the rules are for each component) and (optionally) *initial*
# values. then it returns a concrete json file--one that explicitly lays out all the entities and their attributes.
# if no initial values are given, it generates them randomly. 
def generate_concrete_json(blueprint, initial=None, human=False):
    # TODO: checks to see if the input satisfies the constraints

    squares = [[None for i in range(3)] for j in range(3)]

    for i in range(3):

        panel = initial[i]
        # first_comp = panel["first_comp"]
        # second_comp = {} if "second_comp" not in panel else panel["second_comp"]

        squares[i][0] = panel

    consistent_union_vals = establish_consistent_union_values(blueprint, initial, human=human)

    squares[0][1], squares[0][2] = complete_row(squares[0][0], blueprint, consistent_union_vals, human=human)
    squares[1][1], squares[1][2] = complete_row(squares[1][0], blueprint, consistent_union_vals, human=human)
    squares[2][1], squares[2][2] = complete_row(squares[2][0], blueprint, consistent_union_vals, human=human)

    answers, target = generate_answers(squares[2][2], blueprint, human=human)

    return flatten(squares, answers, blueprint, target, human)

def modify_square(square):
    square["first_comp"]["entities"].sort(key=(lambda elt : elt["position"]))
    mod_square = {}
    mod_square["structure"] = square["structure"]
    
    

    mod_square["first_comp"] = square["first_comp"]["entities"]
            
    if "second_comp" in square:
        square["second_comp"]["entities"].sort(key=(lambda elt : elt["position"]))
        mod_square["second_comp"] = square["second_comp"]["entities"]
    
    return mod_square


def flatten(squares, answers, blueprint, target, human):
    output_dict = {"target": target, "human": human, "panels": []} # TODO implement target properly
    for i in range(3):
        for j in range(3):
            mod_square = modify_square(squares[i][j])
            
            if i != 2 or j != 2:
                output_dict["panels"].append(mod_square)
    
    for answer in answers:
        mod_square = modify_square(answer)
        output_dict["panels"].append(mod_square)
    
    return output_dict

# convert the initial panels into the correct format
"""
def convert_components_to_dicts(initial):
    # TODO figure out how we're gonna do this
    for panel in initial:b
        for field in panel:
            if field == "first_comp" or field == "second_comp":
                panel[field] = {
                    "uniformity": True,
                    "entities": panel[field]
                }
        if "second_comp" not in panel:
            panel["second_comp"] = {}
"""   


# dict dict -> dict
# For any attributes that follow the consistent_union relation in the *blueprint*, we save the three values that
# form the consistent union by looking at the three *initial* values for each of the rows. If there are fewer 
# than three values, we fill the set up randomly.
def establish_consistent_union_values(blueprint, initial, human=False):
    # TODO add a method for sampling new positions and new
    # TODO fix the second comp thing
    comps = ["first_comp"]
    if "second_comp" in blueprint:
        comps.append("second_comp")

    vals = {"first_comp": {}, "second_comp": {}}

    for comp in comps:
        for attr in ["number", "position", "size", "type", "color", "position_row", "position_col"]:
            if attr not in blueprint[comp]:
                continue
            
            if blueprint[comp][attr] == "consistent_union":
                if attr == "number":
                    candidate = [len(initial[i][comp]["entities"]) for i in range(3)]
                elif attr in ["position_row", "position_col"]:
                    candidate = [0, 1, 2]
                elif attr == "position":
                    candidate = []
                    for i in range(3):
                        posns = [entity["position"] for entity in initial[i][comp]["entities"]]
                        posns.sort()
                        posn_tuple = tuple(posns)
                        candidate.append(posn_tuple)
                else:
                    candidate = [initial[i][comp]["entities"][0][attr] for i in range(3)]

                candidate_set = set(candidate)
                candidate = fill(candidate_set, attr, blueprint["structure"], comp, human=human)
                vals[comp][attr] = candidate

    return vals

# set string -> 
# if *val_set* has fewer than three values, it fills it up with random values that
# are in the required range of *attr*     
def fill(val_set, attr, struct=None, comp=None, human=False):
    while len(val_set) < 3:
        if attr == "position":
            posns = sample_posns(struct, comp)
            val_set.add(posns)
        else:
            possible_new_values = [val for val in range_of_values(attr, struct=struct, comp=comp, human=human) if val not in val_set]
            new_addition = random.choice(possible_new_values)
            val_set.add(new_addition)
    
    return list(val_set)


# dict dict dict -> dict dict
# given the first *square* in a row, the *blueprint* that contains structure infromation and relation information, 
# and the *consistent_union_vals* (which depend on the square in the other rows), generate the last two squares
# in the row.
def complete_row(square, blueprint, consistent_union_vals, human=False):

    first_comp_0 = square["first_comp"]
    
    if "second_comp" in blueprint:
        second_comp_0 = square["second_comp"]

    # constructing square_1
    first_comp_1 = generate_next_col(first_comp_0, "first_comp", blueprint["structure"], blueprint["first_comp"], consistent_union_vals["first_comp"], human=human)
    if "second_comp" in blueprint:
        second_comp_1 = generate_next_col(second_comp_0, "second_comp", blueprint["structure"], blueprint["second_comp"], consistent_union_vals["second_comp"], human=human)
        square_1 = make_square(blueprint["structure"], first_comp_1, second_comp_1)
    else:
        square_1 = make_square(blueprint["structure"], first_comp_1)

    # constructing square_2
    first_comp_2 = generate_next_col(first_comp_1, "first_comp", blueprint["structure"], blueprint["first_comp"], consistent_union_vals["first_comp"], prev_comp=first_comp_0, human=human)
    if "second_comp" in blueprint:
        second_comp_2 = generate_next_col(second_comp_1, "second_comp", blueprint["structure"], blueprint["second_comp"], consistent_union_vals["second_comp"], prev_comp=second_comp_0, human=human)
        square_2 = make_square(blueprint["structure"], first_comp_2, second_comp_2)
    else:
        square_2 = make_square(blueprint["structure"], first_comp_2)

    return square_1, square_2

# dict string dict dict dict -> dict
# transforms *comp* according to the rules in *ruleset*, if this is the third col then *prev_comp* is also passed
# *struct* can determine the range of attribute values, and *consistent_union_vals* provides the values that 
# consistent_union attributes can take. 
def generate_next_col(comp, comp_name, struct, ruleset, consistent_union_vals, prev_comp=None, human=False):
    next_comp = copy.deepcopy(comp)
    for attr in ["number", "position",  "position_row", "position_col", "type", "color", "size"]:
        if attr not in ruleset:
            continue
        
        if "progression" in ruleset[attr]:
            inc = int(ruleset[attr].split("_")[1])   
            apply_progression_to(next_comp, comp_name, inc, struct, ruleset, attr, human)

        elif "consistent_union" == ruleset[attr]:
            apply_consistent_union_to(next_comp, consistent_union_vals[attr], struct, attr, ruleset, prev_comp, human)

        elif "arithmetic" in ruleset[attr]:
            direction = ruleset[attr].split("_")[1]
            apply_arithmetic_to(next_comp, comp_name, direction, struct, ruleset, attr, prev_comp, human)
        
        elif "constant" in ruleset[attr]:
            apply_constant_to(next_comp, comp_name, struct, ruleset, attr, prev_comp, human)
        
        elif "random" in ruleset[attr]:
            apply_random_to(next_comp, comp_name, struct, ruleset, attr, prev_comp, human)

    return next_comp

def apply_random_to(comp, comp_name, struct, ruleset, attr, prev_comp, human=False):
    if attr == "number":
        new_number = random.choice(range_of_values(attr, struct, comp_name, human))
        entity_to_copy = comp["entities"][0]
        comp["entities"] = []

        for i in range(new_number):
            comp["entities"].append(place_new_entity(comp, struct, ruleset, entity_to_copy=entity_to_copy, human=human))

    elif attr == "position":
        posns = sample_posns(struct, comp_name)
        entity_to_copy = comp["entities"][0]
        comp["entities"] = []

        for posn in posns:
            comp["entities"].append(place_new_entity(comp, struct, ruleset, entity_to_copy=entity_to_copy, position=posn, human=human))

    else:
        new_val = random.choice(range_of_values(attr, struct, comp_name, human))

        for entity in comp["entities"]:
            if not comp["uniformity"]:
                new_val = random.choice(range_of_values(attr, struct, comp_name, human))
            
            entity[attr] = new_val

def in_multi_entity_comp(struct, comp_name):
    if struct in ["center_single", "out_in", "left_right", "up_down"]:
        return False
    elif struct == "out_in_grid" and comp_name == "first_comp":
        return False
    elif struct == "out_in_grid" and comp_name == "second_comp":
        return True
    elif struct in ["distribute_four", "distribute_nine"]:
        return True

def get_row_or_col_index(pos, row_or_col):
    if row_or_col == "row":
        if pos in [1, 2, 3]:
            return 0
        elif pos in [4, 5, 6]:
            return 1
        elif pos in [7, 8, 9]:
            return 2
    elif row_or_col == "col":
        if pos in [1, 4, 7]:
            return 0
        elif pos in [2, 5, 8]:
            return 1
        elif pos in [3, 6, 9]:
            return 2

def get_pos_options_for_row_or_col(ind, row_or_col):
    if row_or_col == "row":
        if ind == 0:
            return [1, 2, 3]
        elif ind == 1:
            return [4, 5, 6]
        elif ind == 2:
            return [7, 8, 9]
    elif row_or_col == "col":
        if ind == 0:
            return [1, 4, 7]
        elif ind == 1:
            return [2, 5, 8]
        elif ind == 2:
            return [3, 6, 9]
    
def apply_constant_to(comp, comp_name, struct, ruleset, attr, prev_comp=None, human=False):
    if attr == "position_row" or attr == "position_col":
        number_of_entities = len(comp["entities"])
        entity_to_copy = comp["entities"][0]
        comp["entities"] = []

        row_or_col = attr.split("_")[1]
        ind = get_row_or_col_index(entity_to_copy["position"], row_or_col)
        place_entities_in_row_or_col(ind, number_of_entities, row_or_col, comp, struct, ruleset, entity_to_copy, human=human)
        
    elif attr == "number" and in_multi_entity_comp(struct, comp_name):
        number_of_entities = len(comp["entities"])
        entity_to_copy = comp["entities"][0]
        comp["entities"] = []

        for i in range(number_of_entities):
            comp["entities"].append(place_new_entity(comp, struct, ruleset, entity_to_copy=entity_to_copy, human=human))

def place_entities_in_row_or_col(ind, number_of_entities, row_or_col, comp, struct, ruleset, entity_to_copy, human=False):
    points = get_pos_options_for_row_or_col(ind, row_or_col)
    used_points = []
    for i in range(number_of_entities):
        new_pos = random.choice([point for point in points if point not in used_points])
        used_points.append(new_pos)
        comp["entities"].append(place_new_entity(comp, struct, ruleset, entity_to_copy=entity_to_copy, human=human, position=new_pos))


# dict int string string ->
# modifies *comp* to reflect a progression of a certain *inc*rement on a given *attr*ibute.
# *struct* can determine how many position fields there are
# ~tested~
def apply_progression_to(comp, comp_name, inc, struct, ruleset, attr, human=False):
    # TODO need to remove entities also
    if attr == "number":
        entity_to_copy = comp["entities"][0]
        target_number = len(comp["entities"]) + inc
        comp["entities"] = []
        for i in range(target_number):
            comp["entities"].append(place_new_entity(comp, struct, ruleset, entity_to_copy=entity_to_copy, human=human))
    elif attr == "position_row" or attr == "position_col":
        number_of_entities = len(comp["entities"])
        entity_to_copy = comp["entities"][0]
        comp["entities"] = []

        row_or_col = attr.split("_")[1]
        ind = get_row_or_col_index(entity_to_copy["position"], row_or_col) + inc
        place_entities_in_row_or_col(ind, number_of_entities, row_or_col, comp, struct, ruleset, entity_to_copy, human=human)
        
    else:
        for entity in comp["entities"]:
            new_val = entity[attr] + inc
            
            possible_range = range_of_values(attr, struct=struct, comp=comp_name, human=human)
            if new_val not in possible_range and attr == "position":
                new_val = new_val % len(possible_range) # TODO for attributes other than position, do something besides wrapping around
                

            entity[attr] = new_val

# dict string string string dict ->
# modifies *comp* to reflect an arithmetic relationship in a given *direction* ("add" or "sub") on an *attr*ibute
# if its the second row, we can sample a random value, but the third column is completely determined by the last two
def apply_arithmetic_to(comp, comp_name, direction, struct, ruleset, attr, prev_comp=None, human=False):
    # TODO need to implement this for position
    if attr == "position":
        apply_position_arithmetic_to(comp, comp_name, direction, struct, ruleset, prev_comp, human=human)
    else:
        apply_normal_arithmetic_to(comp, comp_name, direction, struct, attr, prev_comp, ruleset, human=human)

# ~tested~
def apply_position_arithmetic_to(comp, comp_name, direction, struct, ruleset, prev_comp=None, human=False):
    if prev_comp is None:
        slots = range_of_values("position", struct, comp_name, human)
        old_occupied_spots = {entity["position"] for entity in comp["entities"]}
        new_occupied_mask = np.random.choice([0, 1], size=(len(slots)))
        new_occupied_spots = set([i + 1 for i in np.nonzero(new_occupied_mask)[0]])
        
        if old_occupied_spots.issubset(new_occupied_spots):
            diff = random.choice(list(old_occupied_spots))
            new_occupied_spots.remove(diff)

        if len(new_occupied_spots) == 0:
            val_to_add = random.choice([val for val in slots if (len(old_occupied_spots) > 1) or (val not in old_occupied_spots)])
            new_occupied_spots.add(val_to_add)
        
        entity_to_copy = comp["entities"][0]
        for i in slots:
            if i in new_occupied_spots and i not in old_occupied_spots:
                comp["entities"].append(place_new_entity(comp, struct, ruleset, entity_to_copy=entity_to_copy, position=i, human=human))
            elif i not in new_occupied_spots and i in old_occupied_spots:
                remove_entity(comp, i)
    else: 
        prev_occupied_spots = {entity["position"] for entity in prev_comp["entities"]}
        curr_occupied_spots = {entity["position"] for entity in comp["entities"]}
        for pos in prev_occupied_spots:
            if pos not in curr_occupied_spots:
                new_entity = copy.deepcopy(get_entity(prev_comp, pos))
                for attr in ruleset:
                    if ruleset[attr] not in ["constant", "constant!", "NA"] and attr != "number" and attr != "position":
                        new_entity[attr] = comp["entities"][0][attr]

                comp["entities"].append(new_entity)

        if direction == "sub":
            for pos in curr_occupied_spots:
                remove_entity(comp, pos)

def get_entity(comp, pos):
    for entity in comp["entities"]:
        if entity["position"] == pos:
            return entity

    return None

def remove_entity(comp, pos=None):
    new_entity_list = []
    for entity in comp["entities"]:
        if entity["position"] != pos:
            new_entity_list.append(entity)
    
    comp["entities"] = new_entity_list


# dict string string string dict dict ->
# modifies *comp* according to the arithmetic progression rule on attribute *attr*
# ~tested~
def apply_normal_arithmetic_to(comp, comp_name, direction, struct, attr, prev_comp=None, ruleset=None, uniform=True, human=False):
    if prev_comp is None:
        max_sum = max(range_of_values(attr, struct, comp_name, human))
        min_sum = min(range_of_values(attr, struct, comp_name, human))

        # TODO for now we are assuming all entities share the attribute. We will relax this later. 
        curr_value = len(comp["entities"]) if attr == "number" else comp["entities"][0][attr]
        
        if direction == "add":
            min_new_val = max(min_sum - curr_value, min_sum)
            max_new_val = min(max_sum - curr_value, max_sum)

        elif direction == "sub":
            min_new_val = max(curr_value - max_sum, min_sum)
            max_new_val = min(curr_value - min_sum, max_sum)
            
        new_val = random.choice(list(range(min_new_val, max_new_val + 1)))
        
        if attr == "number":
            # need to place three shapes with random characteristics
            entity_to_copy = comp["entities"][0]
            comp["entities"] = []
            for i in range(new_val):
                comp["entities"].append(place_new_entity(comp, struct, ruleset, entity_to_copy=entity_to_copy, human=human))
            
        for i, entity in enumerate(comp["entities"]):
            entity[attr] = new_val
        
    else:
        multiplier = 1 if direction == "add" else -1
        if attr == "number":
            entity_to_copy = comp["entities"][0]
            new_val = len(prev_comp["entities"]) + multiplier*len(comp["entities"])
            comp["entities"] = []
            for i in range(new_val):
                comp["entities"].append(place_new_entity(comp, struct, ruleset, entity_to_copy=entity_to_copy, human=human))
        else:
            for i, entity in enumerate(comp["entities"]):
                # TODO this is going to cause problems when we stack arithmetic on top of other transformations
                entity[attr] = multiplier*entity[attr] + prev_comp["entities"][0][attr]

# dict set string string dict ->
# transforms *comp* so it displays a consistent_union on an *attr*. Samples randomly from candidate
# *consistent_union_vals*
# ~tested~
def apply_consistent_union_to(comp, consistent_union_vals, struct, attr, ruleset=None, prev_comp=None, human=False):
    # TODO maybe check to see if I accidentally create another type of relation

    if attr == "position":
        used_vals = [[ent["position"] for ent in comp["entities"]]]
        if prev_comp is not None:
            used_vals.append([ent["position"] for ent in prev_comp["entities"]])
        
        used_vals = [tuple(sorted(val)) for val in used_vals]
    
    elif attr == "position_row" or attr == "position_col":
        # TODO finish this
        row_or_col = attr.split("_")[1]
        used_vals = [get_row_or_col_index(comp["entities"][0]["position"], row_or_col)]
        if prev_comp is not None:
            used_vals.append(get_row_or_col_index(prev_comp["entities"][0]["position"], row_or_col))

    elif attr == "number":
        used_vals = [len(comp["entities"])]
        if prev_comp is not None:
            used_vals.append(len(prev_comp["entities"]))
    else:
        used_vals = [comp["entities"][0][attr]]
        if prev_comp is not None:
            used_vals.append(prev_comp["entities"][0][attr])

    value_options = [val for val in consistent_union_vals if val not in used_vals]
    val = random.choice(value_options)

    if attr == "position":
        entity_to_copy = comp["entities"][0]
        comp["entities"] = []
        for pos in val:
            comp["entities"].append(place_new_entity(comp, struct, ruleset, entity_to_copy=entity_to_copy, position=pos, human=human))
    elif attr in ["position_row", "position_col"]:
        number_of_entities = len(comp["entities"])
        entity_to_copy = comp["entities"][0]
        comp["entities"] = []

        place_entities_in_row_or_col(val, number_of_entities, row_or_col, comp, struct, ruleset, entity_to_copy, human=human)
    elif attr == "number":
        entity_to_copy = comp["entities"][0]
        comp["entities"] = []  
        for i in range(val):
            comp["entities"].append(place_new_entity(comp, struct, ruleset, entity_to_copy=entity_to_copy, human=human))
    
    else:
        for i, entity in enumerate(comp["entities"]):
            entity[attr] = val

# dict string dict -> 
# places a new entity in an unoccupied spot in *comp*, and determines its attributes
# ~tested~
def place_new_entity(comp, struct, ruleset, entity_to_copy=None, position=None, comp_name="second_comp", human=False):
    if in_multi_entity_comp(struct, comp_name):
        non_constant_attrs = [attr for attr in ruleset if ruleset[attr] not in ["constant", "random"]]
        comp_uni = comp["uniformity"]
        occupied_positions = {entity["position"] for entity in comp["entities"]}
        struct_positions = 4 if (struct == "distribute_four") or (struct == "out_in_grid") else 9 # on

        if position is None:
            available_positions = [i for i in range(1, struct_positions + 1) if i not in occupied_positions]
            position = random.choice(available_positions)
            print_stuff = False

        new_entity = {"position": position}

        if entity_to_copy is None:
            entity_to_copy = comp["entities"][0]
        
        for attr in entity_to_copy:
            if attr != "position":
                new_entity[attr] = entity_to_copy[attr] if (attr in non_constant_attrs) or comp_uni else random.choice(range_of_values(attr, struct=struct, comp=comp_name, human=human))
    
        return new_entity
        
# string dict int -> range
# returns the range of possible values an *attr* can take in a given *struct*ure *comp*onent
# ~tested~
def range_of_values(attr, struct=None, comp="first_comp", human=False):
    if attr == "type":
        return list(range(3, 8))
    elif attr == "size":
        return list(range(0, 6))
    elif attr == "color" and not human:
        return list(range(0, 10))
    elif attr == "color" and human:
        return list(range(0, 6))
    elif attr == "angle":
        return list(range(-3, 5))
    elif attr == "position_row" or attr == "position_col":
        return list(range(0, 3))
    elif attr == "number" or attr == "position":
        if struct == "distribute_four":
            return list(range(1, 5))
        elif struct == "distribute_nine":
            return list(range(1, 10))
        elif struct == "out_in_grid" and comp == "second_comp":
            return list(range(1, 5))
        else:
            return list(range(1, 2))

def panels_look_same(one, two):
    if one["structure"] != two["structure"]:
        return False
    else:
        first_comp_equal = comps_look_same(one["first_comp"], two["first_comp"])
        if "second_comp" in one and "second_comp" in two:
            second_comp_equal = comps_look_same(one["second_comp"], two["second_comp"])
        elif "second_comp" not in one and "second_comp" not in two:
            second_comp_equal = True
        else:
            second_comp_equal = False
        return first_comp_equal and second_comp_equal

def comps_look_same(one, two):
    if len(one["entities"]) == len(two["entities"]):
        entities_equal = 0
        for entity in one["entities"]:
            if entity in two["entities"]:
                entities_equal += 1
        return entities_equal == len(two["entities"])
    else:
        return False


def generate_answers(correct_answer, blueprint, fair=True, human=False):
    # TODO need to make sure that all answers are wrong except the right one
    if human:
        step_distrib = [0.5, 0.5]
    else:
        step_distrib = [1, 0]
    
    answer_choices = [correct_answer]
    structure = correct_answer["structure"]
    choice_to_modify = None
    while len(answer_choices) < 8:
        # if we are restarting the process of generating an answer
        if choice_to_modify is None:
            steps_to_take = random.choices([1, 2], weights=step_distrib, k=1)[0]

            if fair:
                choice_to_modify = random.choice(answer_choices)
            else:
                choice_to_modify = correct_answer

        new_choice = copy.deepcopy(choice_to_modify)
        comps = list(correct_answer.keys())
        comps.remove("structure")
        comp_to_modify = random.choice(comps)
        comp = new_choice[comp_to_modify]
        ruleset = blueprint[comp_to_modify]

       

        if structure in ["center_single", "left_right", "up_down", "out_in"]:
            possible_attrs = ["size", "type", "color"]
        elif structure in ["distribute_nine", "distribute_four", "out_in_grid"]:
            possible_attrs = ["size", "type", "color", "position", "number", "uniformity"]
        
        if structure in ["out_in", "out_in_grid"] and comp_to_modify == "first_comp":
            if "color" in possible_attrs: possible_attrs.remove("color")
            if "uniformity" in possible_attrs: possible_attrs.remove("uniformity")
            if "position" in possible_attrs: possible_attrs.remove("position")
            if "number" in possible_attrs: possible_attrs.remove("number")
        
        attr_to_modify = random.choice(possible_attrs)

        if attr_to_modify in ["size", "type", "color"]:
            for i, entity in enumerate(comp["entities"]):
                if not comp["uniformity"] or i == 0:
                    vals = [val for val in range_of_values(attr_to_modify, structure, comp_to_modify, human) if val != entity[attr_to_modify]]
                    new_val = random.choice(vals)

                entity[attr_to_modify] = new_val

        elif attr_to_modify in ["position", "number"]:
            vals = [val for val in range_of_values("number", structure, comp_to_modify, human) if val != len(comp["entities"])]
            new_val = random.choice(vals)
            
            if  attr_to_modify == "number":
                # print("modifying number")
                entity_to_copy = comp["entities"][0]
                comp["entities"] = []

                while len(comp["entities"]) < new_val:
                    comp["entities"].append(place_new_entity(comp, structure, ruleset, entity_to_copy, human=human))

            if attr_to_modify == "position":
                # print("modifying position")
                while len(comp["entities"]) != new_val:
                    if len(comp["entities"]) > new_val:
                        entity_to_remove = random.choice(comp["entities"])
                        remove_entity(comp, pos=entity_to_remove["position"])

                    elif len(comp["entities"]) < new_val:
                        entity_to_copy = comp["entities"][0]
                        comp["entities"].append(place_new_entity(comp, structure, ruleset, entity_to_copy, human=human))
        elif attr_to_modify == "uniformity":
            comp["uniformity"] = not comp["uniformity"]
            entity_to_copy = comp["entities"][0]

            # resample each entity according to the new uniformity rule
            for entity in comp["entities"]:
                pos = entity["position"]
                remove_entity(comp, pos=pos)
                comp["entities"].append(place_new_entity(comp, structure, ruleset, entity_to_copy=entity_to_copy, position=pos, human=human))

        # if we've modified the starting panel enough times, then add it to the choice set
        steps_to_take -= 1
        if steps_to_take == 0:
            equality = False
            for choice in answer_choices:
                if panels_look_same(new_choice, choice):
                    equality = True

            if not equality:
                # print("added")
                answer_choices.append(new_choice)
            
            choice_to_modify = None
        else:
            choice_to_modify = new_choice

        
    
    random.shuffle(answer_choices)
    target = answer_choices.index(correct_answer)
    return answer_choices, target

# string dict dict -> dict
# given a *struct*ure and two components, generates a representation of the panel
# ~tested~
def make_square(struct, first_comp, second_comp=None):
    panel = {
        "structure": struct,
        "first_comp": first_comp,
    }
    if second_comp is not None:
        panel["second_comp"] = second_comp
    
    return panel

import json

if __name__ == "__main__":
    bp = generate_row_or_col_blueprint()
    print(bp)


    """
    f = open("structures/blueprint.json")
    spec = json.load(f)

    blueprint = spec[0]
    initials = spec[1]

    generate_concrete_json(blueprint, initials)

    blueprint = generate_random_blueprint()
    print(generate_initials(blueprint))
    """

# make sure to do the number and position ones first



