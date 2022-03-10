import unittest
import copy
import json

import generate_custom as gc 
from manual_main import convert_to_actual_colors, map_color 

ent1 = {
    "position": 1,
    "type": 3,
    "size": 0,
    "color": 0,
    "angle": -2 
}

ent2 = {
    "position": 2,
    "type": 3,
    "size": 2,
    "color": 6,
    "angle": 1 
}

ent3 = {
    "position": 4,
    "type": 3,
    "size": 3,
    "color": 4,
    "angle": 3
}

ent4 = {
    "position": 1,
    "type": 4,
    "size": 2,
    "color": 9,
    "angle": 0
}

ent5 = {
    "position": 6,
    "type": 5,
    "size": 5,
    "color": 6,
    "angle": -1
}

ent6 = {
    "position": 9,
    "type": 6,
    "size": 0,
    "color": 7,
    "angle": 4
}

ent7 = {
    "position": 1,
    "type": 7,
    "size": 1,
    "color": 4,
    "angle": -1
}

ent8 = {
    "position": 3,
    "type": 5,
    "size": 2,
    "color": 3,
    "angle": -1
}

ent9 = {
    "position": 4,
    "type": 5,
    "size": 2,
    "color": 3,
    "angle": -1
}
ent10 = {
    "position": 1,
    "type": 5,
    "size": 2,
    "color": 3,
    "angle": -1
}

ent11 = {
    "position": 3,
    "type": 5,
    "size": 1,
    "color": 4,
    "angle": 3
}

ent12 = {
    "position": 4,
    "type": 5,
    "size": 1,
    "color": 4,
    "angle": 2
}
ent13 = {
    "position": 5,
    "type": 5,
    "size": 1,
    "color": 4,
    "angle": 1
}

ent14 = {
    "position": 8,
    "type": 5,
    "size": 1,
    "color": 4,
    "angle": 1
}


class TestGenerateCustom(unittest.TestCase):

    def test_map_color(self):
        self.assertEqual(map_color(0), 0)
        self.assertEqual(map_color(1), 1)
        self.assertEqual(map_color(2), 3)
        self.assertEqual(map_color(3), 5)
        self.assertEqual(map_color(4), 7)
        self.assertEqual(map_color(5), 9)
    
    def test_convert_to_actual_colors(self):
        with open("prototypes/human_colors.json") as f:
            human_colors = json.load(f)
        with open("prototypes/converted_colors.json") as f:
            converted_colors = json.load(f)

        self.assertEqual(convert_to_actual_colors(human_colors), converted_colors)

    def test_eligible_values(self):

        self.assertEqual(gc.eligible_values("out_in", "first_comp", "color", "constant"), [0])
        self.assertEqual(gc.eligible_values("out_in_grid", "first_comp", "number", "constant"), [1])
        self.assertEqual(gc.eligible_values("center_single", "first_comp", "position", "constant"), [1])
        self.assertEqual(gc.eligible_values("left_right", "second_comp", "position", "constant"), [1])

        self.assertEqual(gc.eligible_values("distribute_nine", "first_comp", "number", "progression_-2"), list(range(5, 10)))
        self.assertEqual(gc.eligible_values("distribute_four", "first_comp", "size", "progression_1"), list(range(0, 4)))
        self.assertEqual(gc.eligible_values("center_single", "first_comp", "color", "progression_2"), list(range(0, 6)))

        self.assertEqual(gc.eligible_values("distribute_nine", "first_comp", "number", "arithmetic_add"), list(range(1, 9)))
        self.assertEqual(gc.eligible_values("out_in_grid", "second_comp", "position", "arithmetic_sub"), list(range(1, 5)))
        self.assertEqual(gc.eligible_values("distribute_four", "first_comp", "size", "arithmetic_add"), list(range(0,6)))
        self.assertEqual(gc.eligible_values("out_in_grid", "second_comp", "number", "arithmetic_sub"), list(range(2, 5)))
        self.assertEqual(gc.eligible_values("out_in_grid", "second_comp", "number", "arithmetic_sub", used_vals=[3, 4]), list(range(2, 5)))

        self.assertEqual(gc.eligible_values("left_right", "second_comp", "type", "consistent_union", used_vals=[3, 5]), [4, 6, 7])
        self.assertEqual(gc.eligible_values("up_down", "first_comp", "size", "consistent_union", used_vals=[1]), [0, 2, 3, 4, 5])

        self.assertEqual(gc.eligible_values("up_down", "first_comp", "color", "progression_-2", used_vals=[2, 1]), [4, 5, 6, 7, 8, 9])
        self.assertEqual(gc.eligible_values("left_right", "second_comp", "color", "progression_-2", used_vals=[]), [4, 5, 6, 7, 8, 9])

    def test_panels_look_same(self):
        comp1 = {
            "uniformity": True,
            "entities": [ent1]
        }
        comp2 = {
            "uniformity": True,
            "entities": [ent2]
        }

        panel1 = {
            "structure": "left_right",
            "first_comp": comp1,
            "second_comp": comp2
        }
        panel2a = {
            "structure": "up_down",
            "first_comp": copy.deepcopy(comp1),
            "second_comp": copy.deepcopy(comp2)
        }
        panel2b = {
            "structure": "left_right", 
            "first_comp": copy.deepcopy(comp1),
            "second_comp": copy.deepcopy(comp2),
        }
        panel2c = {
            "structure": "center_single", 
            "first_comp": copy.deepcopy(comp1),
        }
        
        self.assertFalse(gc.panels_look_same(panel1, panel2a))
        self.assertTrue(gc.panels_look_same(panel1, panel2b))
        self.assertFalse(gc.panels_look_same(panel1, panel2c))

        comp1 = {
            "uniformity": False,
            "entities": [ent1, ent2, ent3]
        }
        comp2 = {
            "uniformity": True,
            "entities": [copy.deepcopy(ent2), copy.deepcopy(ent1), copy.deepcopy(ent3)]
        }
        comp3 = {
            "uniformity": True,
            "entities": [copy.deepcopy(ent2), copy.deepcopy(ent1), copy.deepcopy(ent3), ent4]
        }
        comp4 = {
            "uniformity": True,
            "entities": [copy.deepcopy(ent1), copy.deepcopy(ent2)]
        }

        panel1 = {
            "structure": "distribute_four",
            "first_comp": comp1
        }
        panel2a = {
            "structure": "distribute_four",
            "first_comp": comp2
        }
        panel2b = {
            "structure": "distribute_four",
            "first_comp": comp3
        }
        panel2c = {
            "structure": "distribute_four",
            "first_comp": comp4
        }

        self.assertTrue(gc.panels_look_same(panel1, panel2a))
        self.assertFalse(gc.panels_look_same(panel1, panel2b))
        self.assertFalse(gc.panels_look_same(panel1, panel2c))

    def test_comps_look_same(self):
        comp1 = {
            "uniformity": True,
            "entities": [ent8, ent9, ent10]
        }
        comp2a = {
            "uniformity": True,
            "entities": [ent8, ent9, ent10]
        }
        comp2b = {
            "uniformity": True,
            "entities": [copy.deepcopy(ent8), copy.deepcopy(ent9), copy.deepcopy(ent10)]
        }
        comp2c = {
            "uniformity": False,
            "entities": [copy.deepcopy(ent8), copy.deepcopy(ent9), copy.deepcopy(ent10)]
        }

        self.assertTrue(gc.comps_look_same(comp1, comp2a))
        self.assertTrue(gc.comps_look_same(comp1, comp2b))
        self.assertTrue(gc.comps_look_same(comp1, comp2c))

        comp3a = {
            "uniformity": True,
            "entities": [copy.deepcopy(ent8), copy.deepcopy(ent9)]
        }
        comp3b = {
            "uniformity": True,
            "entities": [copy.deepcopy(ent8), copy.deepcopy(ent9), copy.deepcopy(ent10), ent11]
        }
        comp3c = {
            "uniformity": True,
            "entities": [copy.deepcopy(ent8), copy.deepcopy(ent9), ent11]
        }

        self.assertFalse(gc.comps_look_same(comp1, comp3a))
        self.assertFalse(gc.comps_look_same(comp1, comp3b))
        self.assertFalse(gc.comps_look_same(comp1, comp3c))

    def test_apply_progression_to(self):
        comp = {
            "uniformity": True,
            "entities": [ent8, ent9, ent10, ent13, ent14] 
        }
        ruleset = {
            "position": "NA", 
            "number": "progression_-2",
            "size": "progression",
            "type": "consistent-union",
            "color": "constant"
        }

        comp_copy = copy.deepcopy(comp)
        gc.apply_progression_to(comp_copy, "first_comp", -2, "distribute_nine", ruleset, "number")

        self.assertEqual(len(comp_copy["entities"]), 3)
        for ent in comp_copy["entities"]:
            self.assertEqual(ent["size"], comp["entities"][0]["size"])
            self.assertEqual(ent["type"], comp["entities"][0]["type"])
            self.assertEqual(ent["color"], comp["entities"][0]["color"])
            self.assertEqual(ent["angle"], comp["entities"][0]["angle"])
        
        comp_copy = copy.deepcopy(comp)
        gc.apply_progression_to(comp_copy, "first_comp", 1, "distribute_nine", ruleset, "color")
        
        for i, ent in enumerate(comp_copy["entities"]):
            self.assertEqual(ent["size"], comp["entities"][i]["size"])
            self.assertEqual(ent["position"], comp["entities"][i]["position"])
            self.assertEqual(ent["type"], comp["entities"][i]["type"])
            self.assertEqual(ent["color"], comp["entities"][i]["color"] + 1)
            self.assertEqual(ent["angle"], comp["entities"][i]["angle"])
        
        comp_copy = copy.deepcopy(comp)
        gc.apply_progression_to(comp_copy, "first_comp", 2, "distribute_nine", ruleset, "position")
        
        for i, ent in enumerate(comp_copy["entities"]):
            new_position = (comp["entities"][i]["position"] + 2) % 9
            self.assertEqual(ent["size"], comp["entities"][i]["size"])
            self.assertEqual(ent["position"], new_position)
            self.assertEqual(ent["type"], comp["entities"][i]["type"])
            self.assertEqual(ent["color"], comp["entities"][i]["color"])
            self.assertEqual(ent["angle"], comp["entities"][i]["angle"])
        


    def test_apply_position_arithmetic_to(self):
        prev_comp = {
            "uniformity": False,
            "entities": [ent5, ent6, ent7, ent8, ent9]
        }
        comp = {
            "uniformity": False,
            "entities": [ent10, ent11, ent12, ent13, ent14]
        }
        ruleset = {
            "position": "arithmetic",
            "number": "NA",
            "size": "progression",
            "type": "constant",
            "color": "consistent-union"
        }
        
        unequal_type_count = 0
        for i in range(100):
            comp_copy = copy.deepcopy(comp)
            gc.apply_position_arithmetic_to(comp_copy, "first_comp", "add", "distribute_nine", ruleset)

            for position in range(1, 10):
                e1 = gc.get_entity(comp_copy, position)
                e2 = gc.get_entity(comp, position)

                if e1 is not None and e2 is not None:
                    self.assertEqual(e1["position"], e2["position"])
                    self.assertEqual(e1["size"], e2["size"])
                    self.assertEqual(e1["type"], e2["type"])
                    self.assertEqual(e1["color"], e2["color"])
                    self.assertEqual(e1["angle"], e2["angle"])
                elif e1 is not None and e2 is None:
                    self.assertEqual(e1["size"], comp["entities"][0]["size"])
                    self.assertIn(e1["angle"], list(range(-3,5)))
                    self.assertIn(e1["type"], list(range(3, 8)))
                    unequal_type_count += (e1["type"] != comp["entities"][0]["type"])
                    self.assertEqual(e1["color"], comp["entities"][0]["color"])
            
        self.assertGreater(unequal_type_count, 5/6 * 200 - 30) # expectation is 250

        comp_copy = copy.deepcopy(comp)
        gc.apply_position_arithmetic_to(comp_copy, "first_comp", "add", "distribute_nine", ruleset, prev_comp=prev_comp)

        # positions for prev_comp: 
        # positions for comp: 1 3 4 5 8
        # positions for prev_comp 1 3 4 6 9
        self.assertTrue(gc.get_entity(comp_copy, 1) is not None)
        self.assertTrue(gc.get_entity(comp_copy, 2) is None)
        self.assertTrue(gc.get_entity(comp_copy, 3) is not None)
        self.assertTrue(gc.get_entity(comp_copy, 4) is not None)
        self.assertTrue(gc.get_entity(comp_copy, 5) is not None)
        self.assertTrue(gc.get_entity(comp_copy, 6) is not None)
        self.assertTrue(gc.get_entity(comp_copy, 7) is None)
        self.assertTrue(gc.get_entity(comp_copy, 8) is not None)
        self.assertTrue(gc.get_entity(comp_copy, 9) is not None)
        
        # for entities that were in comp
        for i in [1, 3, 4, 5, 8]:
            ent = gc.get_entity(comp_copy, i)
            ent2 = gc.get_entity(comp, i)
            self.assertEqual(ent["position"], i)
            self.assertEqual(ent["size"], ent2["size"])
            self.assertEqual(ent["type"], ent2["type"])
            self.assertEqual(ent["color"], ent2["color"])
            self.assertEqual(ent["angle"], ent2["angle"])
        
        # for entities in prev_comp but not comp
        for i in [6, 9]:
            ent = gc.get_entity(comp_copy, i)
            ent_curr = comp["entities"][0]
            ent_prev = gc.get_entity(comp_copy, i) 
            self.assertEqual(ent["position"], i)
            self.assertEqual(ent["size"], ent_curr["size"])
            self.assertEqual(ent["type"], ent_prev["type"])
            self.assertEqual(ent["color"], ent_curr["color"])
            self.assertEqual(ent["angle"], ent_prev["angle"])

        # now test the subtraction
        comp_copy = copy.deepcopy(comp)
        gc.apply_position_arithmetic_to(comp_copy, "first_comp", "sub", "distribute_nine", ruleset, prev_comp=prev_comp)
        # positions for prev_comp: 
        # positions for comp: 1 3 4 5 8
        # positions for prev_comp 1 3 4 6 9
        self.assertTrue(gc.get_entity(comp_copy, 1) is None)
        self.assertTrue(gc.get_entity(comp_copy, 2) is None)
        self.assertTrue(gc.get_entity(comp_copy, 3) is None)
        self.assertTrue(gc.get_entity(comp_copy, 4) is None)
        self.assertTrue(gc.get_entity(comp_copy, 5) is None)
        self.assertTrue(gc.get_entity(comp_copy, 6) is not None)
        self.assertTrue(gc.get_entity(comp_copy, 7) is None)
        self.assertTrue(gc.get_entity(comp_copy, 8) is None)
        self.assertTrue(gc.get_entity(comp_copy, 9) is not None)

        for i in [6, 9]:
            ent = gc.get_entity(comp_copy, i)
            ent_curr = comp["entities"][0]
            ent_prev = gc.get_entity(comp_copy, i) 
            self.assertEqual(ent["position"], i)
            self.assertEqual(ent["size"], ent_curr["size"])
            self.assertEqual(ent["type"], ent_prev["type"])
            self.assertEqual(ent["color"], ent_curr["color"])
            self.assertEqual(ent["angle"], ent_prev["angle"])


    def test_apply_normal_arithmetic_to(self):
        # test addition on size
        prev_comp = {
            "uniformity": False,
            "entities": [ent11, ent12, ent13]
        }
        comp = {
                "uniformity": False,
                "entities": [ent8, ent9, ent10]
        }

        counts = {0: 0, 1: 0, 2: 0, 3: 0}
        for i in range(1000):
            comp_copy = copy.deepcopy(comp)
            gc.apply_normal_arithmetic_to(comp_copy, "first_comp", "add", "distribute_four", "size")
            for i, ent in enumerate(comp_copy["entities"]):
                self.assertIn(ent["size"], list(range(0, 4)))
                counts[ent["size"]] += 1

        for key in counts:
            self.assertGreater(counts[key], 600) # PROB expectation 75
            self.assertLess(counts[key], 900)
        
        comp_copy = copy.deepcopy(comp)
        gc.apply_normal_arithmetic_to(comp_copy, "first_comp", "add", "distribute_four", "size", prev_comp=prev_comp)
        for i, ent in enumerate(comp_copy["entities"]):
            self.assertEqual(ent["size"], 3)
            self.assertEqual(ent["type"], comp["entities"][i]["type"])
            self.assertEqual(ent["position"], comp["entities"][i]["position"])
            self.assertEqual(ent["color"], comp["entities"][i]["color"])
            self.assertEqual(ent["angle"], comp["entities"][i]["angle"])
        
        # test addition on number
        prev_comp = {
            "uniformity": True,
            "entities": [ent11, ent12]
        }
        comp = {
                "uniformity": True,
                "entities": [ent8, ent9, ent10]
        }
        ruleset = {
            "position": "NA",
            "number": "arithmetic",
            "size": "progression",
            "type": "constant",
            "color": "consistent-union"
        }

        len_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
        for i in range(1200):
            comp_copy = copy.deepcopy(comp)
            gc.apply_normal_arithmetic_to(comp_copy, "first_comp", "add", "distribute_nine", "number", ruleset=ruleset)
            length = len(comp_copy["entities"])
            self.assertIn(length, [1, 2, 3, 4, 5, 6])
            len_counts[length] += 1
            
            for ent in comp_copy["entities"]:
                self.assertEqual(ent["size"], comp["entities"][0]["size"])
                self.assertEqual(ent["type"], comp["entities"][0]["type"])
                self.assertEqual(ent["color"], comp["entities"][0]["color"])
        
        for length in len_counts:
            self.assertGreater(len_counts[length], 160)
            self.assertLess(len_counts[length], 240)
        
        comp_copy = copy.deepcopy(comp)
        gc.apply_normal_arithmetic_to(comp_copy, "first_comp", "add", "distribute_nine", "number", ruleset=ruleset, prev_comp=prev_comp)
        self.assertEqual(len(comp_copy["entities"]), 5)
        for entity in comp_copy["entities"]:
            self.assertEqual(ent["size"], comp["entities"][0]["size"])
            self.assertEqual(ent["type"], comp["entities"][0]["type"])
            self.assertEqual(ent["color"], comp["entities"][0]["color"])
            self.assertEqual(ent["angle"], comp["entities"][0]["angle"])
            
        # test subtraction on color
        prev_comp = {
            "uniformity": False,
            "entities": [ent11, ent12, ent13, ent14]
        }
        comp = {
                "uniformity": False,
                "entities": [ent8, ent9, ent10]
        }

        counts = {0: 0, 1: 0, 2: 0, 3: 0}
        for i in range(1000):
            comp_copy = copy.deepcopy(comp)
            gc.apply_normal_arithmetic_to(comp_copy, "first_comp", "sub", "distribute_four", "color")
            for i, ent in enumerate(comp_copy["entities"]):
                self.assertIn(ent["color"], list(range(0, 4)))
                counts[ent["color"]] += 1

        for key in counts:
            self.assertGreater(counts[key], 600) # PROB expectation 750
            self.assertLess(counts[key], 900)
        
        comp_copy = copy.deepcopy(comp)
        gc.apply_normal_arithmetic_to(comp_copy, "first_comp", "sub", "distribute_four", "color", prev_comp=prev_comp)
        for i, ent in enumerate(comp_copy["entities"]):
            self.assertEqual(ent["color"], 1)
            self.assertEqual(ent["type"], comp["entities"][i]["type"])
            self.assertEqual(ent["position"], comp["entities"][i]["position"])
            self.assertEqual(ent["size"], comp["entities"][i]["size"])
            self.assertEqual(ent["angle"], comp["entities"][i]["angle"])
        
        # test subtraction on number
        prev_comp = {
            "uniformity": True,
            "entities": [ent11, ent12, ent13, ent14]
        }
        comp = {
                "uniformity": True,
                "entities": [ent8, ent9]
        }
        ruleset = {
            "position": "NA",
            "number": "arithmetic",
            "size": "constant",
            "type": "progression",
            "color": "consistent-union"
        }

        len_counts = {1: 0, 2: 0, 3: 0}
        for i in range(1200):
            comp_copy = copy.deepcopy(prev_comp)
            gc.apply_normal_arithmetic_to(comp_copy, "first_comp", "sub", "distribute_nine", "number", ruleset=ruleset)
            length = len(comp_copy["entities"])
            self.assertIn(length, [1, 2, 3])
            len_counts[length] += 1
            
            for ent in comp_copy["entities"]:
                self.assertEqual(ent["size"], prev_comp["entities"][0]["size"])
                self.assertEqual(ent["type"], prev_comp["entities"][0]["type"])
                self.assertEqual(ent["color"], prev_comp["entities"][0]["color"])
        
        for length in len_counts:
            self.assertGreater(len_counts[length], 360) # expectation 400
            self.assertLess(len_counts[length], 440) # expectation 400
        
        comp_copy = copy.deepcopy(comp)
        gc.apply_normal_arithmetic_to(comp_copy, "first_comp", "sub", "distribute_nine", "number", ruleset=ruleset, prev_comp=prev_comp)
        self.assertEqual(len(comp_copy["entities"]), 2)
        for ent in comp_copy["entities"]:
            self.assertEqual(ent["size"], comp["entities"][0]["size"])
            self.assertEqual(ent["type"], comp["entities"][0]["type"])
            self.assertEqual(ent["color"], comp["entities"][0]["color"])
            self.assertEqual(ent["angle"], comp["entities"][0]["angle"])

        

    def test_apply_consistent_union_to(self):
        
        prev_comp = {
            "uniformity": False,
            "entities": [ent8, ent9, ent10]
        }
        comp = {
                "uniformity": False,
                "entities": [ent1, ent2, ent3]
        }
        consistent_union_vals = [3, 5, 7]
        attr = "type"
        attr_counts = {3: 0, 5: 0, 7: 0}
        for i in range(100):
            comp_copy = copy.deepcopy(comp)
            gc.apply_consistent_union_to(comp_copy, consistent_union_vals, "out_in_grid", attr)
            
            for i, entity in enumerate(comp_copy["entities"]):
                if i > 0:
                    self.assertEqual(comp_copy["entities"][i - 1][attr], entity[attr])
                
                self.assertIn(entity[attr], [5, 7])
                self.assertEqual(entity["position"], comp["entities"][i]["position"])
                self.assertEqual(entity["size"], comp["entities"][i]["size"])
                self.assertEqual(entity["color"], comp["entities"][i]["color"])
                self.assertEqual(entity["angle"], comp["entities"][i]["angle"])
                self.assertNotEqual(entity["type"], comp["entities"][i]["type"])
            
            attr_counts[comp_copy["entities"][0][attr]] += 1

        self.assertGreater(attr_counts[7], 40)
        self.assertLess(attr_counts[7], 60)
        
        self.assertGreater(attr_counts[5], 40)
        self.assertLess(attr_counts[5], 60)

        self.assertEqual(attr_counts[3], 0)

        comp_copy = copy.deepcopy(comp)
        gc.apply_consistent_union_to(comp_copy, consistent_union_vals, "out_in_grid", attr, prev_comp=prev_comp)
        
        for i, entity in enumerate(comp_copy["entities"]):
            if i > 0:
                self.assertEqual(comp_copy["entities"][i - 1][attr], entity[attr])
            
            self.assertEqual(entity[attr], 7)
            self.assertEqual(entity["position"], comp["entities"][i]["position"])
            self.assertEqual(entity["size"], comp["entities"][i]["size"])
            self.assertEqual(entity["color"], comp["entities"][i]["color"])
            self.assertEqual(entity["angle"], comp["entities"][i]["angle"])
            self.assertNotEqual(entity["type"], comp["entities"][i]["type"])

        consistent_union_vals = [(1, 2, 4), (1, 3, 4), (2, 3)]
        ruleset = {
            "number": "NA",
            "position": "consistent-union",
            "type": "progression",
            "size": "constant",
            "color": "arithmetic-sum" 
        }

        two_layout_count = 0
        three_layout_count = 0
        unequal_size_count = 0
        for i in range(1000):
            comp_copy = copy.deepcopy(comp)
            gc.apply_consistent_union_to(comp_copy, consistent_union_vals, "distribute_four", "position", ruleset=ruleset)
            
            posns = set()
            for ent in comp_copy["entities"]:
                posns.add(ent["position"])
            
            self.assertIn(posns, [{3, 4, 1}, {2, 3}])

            if len(comp_copy["entities"]) == 2:
                two_layout_count += 1
            elif len(comp_copy["entities"]) == 3:
                three_layout_count += 1
            
            for ent in comp_copy["entities"]:
                self.assertEqual(ent["type"], comp["entities"][0]["type"])
                self.assertEqual(ent["color"], comp["entities"][0]["color"])
                self.assertIn(ent["size"], list(range(0,6)))
                unequal_size_count += (ent["size"] != comp["entities"][0]["size"])

        self.assertGreater(unequal_size_count, 1800) # expectation that its 2100
        self.assertGreater(two_layout_count, 450)
        self.assertLess(two_layout_count, 550)
        self.assertGreater(three_layout_count, 450)
        self.assertLess(three_layout_count, 550)

        comp_copy = copy.deepcopy(comp)
        ruleset = {
            "number": "NA",
            "position": "consistent-union",
            "type": "progression",
            "size": "consistent-union",
            "color": "constant" 
        }

        gc.apply_consistent_union_to(comp_copy, consistent_union_vals, "distribute_four", "position", ruleset=ruleset, prev_comp=prev_comp)
        
        posns = set()
        for ent in comp_copy["entities"]:
            posns.add(ent["position"])
            
        self.assertEqual(posns, {2, 3})
            
        for i, entity in enumerate(comp_copy["entities"]):
            self.assertEqual(ent["type"], comp["entities"][0]["type"])
            self.assertEqual(ent["size"], comp["entities"][0]["size"])
            self.assertIn(ent["color"], list(range(0, 10)))
        
        consistent_union_vals = [1, 3, 4]
        ruleset = {
            "number": "consistent-union",
            "position": "NA",
            "type": "constant",
            "size": "progression",
            "color": "arithmetic-sum"
        }

        one_count = 0
        four_count = 0
        unequal_type_count = 0
        for i in range(1000):
            comp_copy = copy.deepcopy(comp)
            gc.apply_consistent_union_to(comp_copy, consistent_union_vals, "distribute_four", "number", ruleset=ruleset)
            
            self.assertIn(len(comp_copy["entities"]), [1, 4])

            if len(comp_copy["entities"]) == 1:
                one_count += 1
            elif len(comp_copy["entities"]) == 4:
                four_count += 1
            
            for ent in comp_copy["entities"]:
                self.assertEqual(ent["size"], comp["entities"][0]["size"])
                self.assertEqual(ent["color"], comp["entities"][0]["color"])
                self.assertIn(ent["type"], list(range(3,8)))
                unequal_size_count += (ent["size"] != comp["entities"][0]["size"])
        
        self.assertGreater(one_count, 400)
        self.assertLess(one_count, 600)
        self.assertGreater(four_count, 400)
        self.assertLess(four_count, 600)
        
        comp_copy = copy.deepcopy(comp)
        prev_comp["entities"].remove(ent8)
        ruleset = {
            "number": "consistent-union",
            "position": "NA",
            "type": "progression",
            "size": "constant",
            "color": "arithmetic-sum"
        }
        consistent_union_vals = [2, 3, 6]
        gc.apply_consistent_union_to(comp_copy, consistent_union_vals, "distribute_nine", "number", ruleset=ruleset, prev_comp=prev_comp)

        self.assertEqual(len(comp_copy["entities"]), 6)
        for entity in comp_copy["entities"]:
            self.assertEqual(entity["type"], comp["entities"][0]["type"])
            self.assertIn(entity["size"], list(range(0,10)))
            self.assertEqual(entity["color"], comp["entities"][0]["color"])
        
        

        

    def test_place_new_entity(self):
        # TODO test the part that places at a particular position
        struct = "out_in_grid"

        ent4_copy = ent4.copy()
        ent4_copy["position"] = 5

        ent5_copy = ent5.copy()
        ent5_copy["position"] = 6

        ent6_copy = ent6.copy()
        ent6_copy["position"] = 8

        struct = "out_in_grid"
        ruleset = {
            "number": "progression_1",
            "position": "constant",
            "type": "consistent_union",
            "size": "arithmetic_sub",
            "color": "constant"
        }
        comp = {
            "uniformity": False,
            "entities": [ent1, ent2, ent3]
        }
        
        new_entity = gc.place_new_entity(comp, struct, ruleset)
        self.assertEqual(new_entity["position"], 3)
        self.assertEqual(new_entity["type"], ent1["type"])
        self.assertEqual(new_entity["size"], ent1["size"])
        self.assertIn(new_entity["color"], list(range(0, 10)))
        self.assertIn(new_entity["angle"], list(range(-3, 5)))
    
        struct = "distribute_four"
        ruleset = {
            "number": "constant",
            "position": "arithmetic_sub",
            "type": "arithmetic_add",
            "size": "constant",
            "color": "constant"
        }
        comp = {
            "uniformity": True,
            "entities": [ent8, ent9, ent10],
        }
        new_entity = gc.place_new_entity(comp, struct, ruleset)
        self.assertEqual(new_entity["position"], 2)
        self.assertEqual(new_entity["type"], ent8["type"])
        self.assertEqual(new_entity["size"], ent8["size"])
        self.assertEqual(new_entity["color"], ent8["color"])
        self.assertEqual(new_entity["angle"], ent8["angle"])

        struct = "distribute_nine"
        ruleset = {
            "number": "constant",
            "position": "arithmetic_sub",
            "type": "constant",
            "size": "constant",
            "color": "progression"
        }
        comp = {
            "uniformity": False, 
            "entities": [ent1, ent2, ent3, ent4_copy, ent5_copy, ent6_copy]
        }

        sizes = set()
        types = set()
        for i in range(20):
            new_entity = gc.place_new_entity(comp, struct, ruleset)
            self.assertIn(new_entity["position"], [3, 7, 9])
            self.assertEqual(new_entity["color"], ent1["color"])

            sizes.add(new_entity["size"])
            types.add(new_entity["type"])

        self.assertTrue(len(sizes) > 1)
        self.assertTrue(sizes.issubset(list(range(0, 6))))
        self.assertTrue(len(types) > 1)
        self.assertTrue(types.issubset(list(range(0, 10))))



        struct = "center_single"

    def test_range_of_values(self):
        self.assertEqual(gc.range_of_values("number"), list(range(1, 2)))
        self.assertEqual(gc.range_of_values("position"), list(range(1, 2)))
        self.assertEqual(gc.range_of_values("type"), list(range(3, 8)))
        self.assertEqual(gc.range_of_values("size"), list(range(0, 6)))
        self.assertEqual(gc.range_of_values("color"), list(range(0, 10)))
        self.assertEqual(gc.range_of_values("angle"), list(range(-3, 5)))

        self.assertEqual(gc.range_of_values("number", struct="center_single"), list(range(1, 2)))
        self.assertEqual(gc.range_of_values("number", struct="distribute_four"), list(range(1, 5)))
        self.assertEqual(gc.range_of_values("number", struct="distribute_nine"), list(range(1, 10)))
        self.assertEqual(gc.range_of_values("number", struct="left_right"), list(range(1, 2)))
        self.assertEqual(gc.range_of_values("number", struct="up_down"), list(range(1, 2)))
        self.assertEqual(gc.range_of_values("number", struct="out_in"), list(range(1, 2)))
        self.assertEqual(gc.range_of_values("number", struct="out_in_grid"), list(range(1, 2)))
        self.assertEqual(gc.range_of_values("number", struct="out_in_grid", comp="first_comp"), list(range(1, 2)))
        self.assertEqual(gc.range_of_values("number", struct="out_in_grid", comp="second_comp"), list(range(1, 5)))

        self.assertEqual(gc.range_of_values("position", struct="center_single"), list(range(1, 2)))
        self.assertEqual(gc.range_of_values("position", struct="distribute_four"), list(range(1, 5)))
        self.assertEqual(gc.range_of_values("position", struct="distribute_nine"), list(range(1, 10)))
        self.assertEqual(gc.range_of_values("position", struct="left_right"), list(range(1, 2)))
        self.assertEqual(gc.range_of_values("position", struct="up_down"), list(range(1, 2)))
        self.assertEqual(gc.range_of_values("position", struct="out_in"), list(range(1, 2)))
        self.assertEqual(gc.range_of_values("position", struct="out_in_grid"), list(range(1, 2)))
        self.assertEqual(gc.range_of_values("position", struct="out_in_grid", comp="first_comp"), list(range(1, 2)))
        self.assertEqual(gc.range_of_values("position", struct="out_in_grid", comp="second_comp"), list(range(1, 5)))

    def test_make_square(self):
        struct = "out_in_grid"
        first_comp = {
            "uniformity": True,
            "entities": [ent1, ent2]
        }
        second_comp = {
            "uniformity": False,
            "entities": [ent3, ent4]
        }

        self.assertEqual(gc.make_square(struct, first_comp, second_comp), 
            {
                "structure": "out_in_grid",
                "first_comp": first_comp,
                "second_comp": second_comp
            }
        )

        self.assertEqual(gc.make_square(struct, first_comp), 
            {
                "structure": "out_in_grid",
                "first_comp": first_comp
            }
        )

if __name__ == "__main__":
    unittest.main()