
def generate_answers(correct_answer):
    answer_choices = [correct_answer]

    while len(answer_choices) < 8:
        choice_to_modify = random.choice(answer_choices)
        comps = list(correct_answer.keys()).remove("structure")
        comp_to_modify = random.choice(comps)

        

        if structure in ["center_single", "left_right", "up_down", "out_in"]:
            possible_attrs = ["size", "type", "color"]
        else:
            possible_attrs = ["size", "type", "color", "position", "number", "uniformity"]
        
        attr_to_modify = random.choice(possible_attrs)