from flask import Flask
from flask import request, send_file
from generate_custom import generate_concrete_json, generate_random_blueprint, generate_initials
from manual_main import gen_specific
from PIL import Image
from flask_cors import CORS
from io import BytesIO
import matplotlib.pyplot as plt

import sys
import numpy as np

"""
to start the server on powershell
> $env:FLASK_APP = "server"
> flask run
 * Running on http://127.0.0.1:5000/
"""
app = Flask(__name__)

CORS(app)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/literal", methods=["POST"])
def literal():
    spec = request.get_json()
    blueprint = spec[0]
    initial = spec[1]

    return generate_concrete_json(blueprint, initial)

@app.route("/image", methods=["POST"])
def image():
    spec = request.get_json()
    img, tar = gen_specific(0, spec, "/")
    img = arr_to_img(img)

    return serve_pil_image(img)

@app.route("/file", methods=["post"])
def file():
    spec = request.get_json()
    img, tar = gen_specific(0, spec, "/")

    return serve_npz(img, tar)


@app.route("/blueprint", methods=["GET"])
def blueprint():
    return generate_random_blueprint()

@app.route("/initials", methods=["POST"])
def initials():
    blueprint = request.get_json()
    return {"results": generate_initials(blueprint)}

def serve_npz(image, target):
    buf = BytesIO()
    np.savez(buf,
             image=image,
             target=target)
    buf.seek(0)
    res = send_file(buf, mimetype="text/csv")
    return res

def serve_pil_image(pil_img):
    output = BytesIO()
    pil_img.save(output, 'JPEG', quality=70)
    output.seek(0)
    res = send_file(output, mimetype='image/jpeg')
    return res

# image generating functions
def arr_to_img(arr):
    context_arr = construct_array_context(arr[:8,:,:])
    answers_arr = construct_array_answers(arr[8:,:,:])
    
    return pixel_arrs_to_img(context_arr, answers_arr)

def construct_array_context(arr):
    return construct_array(arr, 3, 3)
    
def construct_array_answers(arr):
    return construct_array(arr, 2, 4)
    
def construct_array(arr, rows, cols):
    
    tile_size = arr.shape[1]
    cushion = int(tile_size/40)
    
    full_image = np.zeros((tile_size*rows + cushion*(rows - 1), tile_size*cols + cushion*(cols - 1)))
    
    for row in range(rows):
        for col in range(cols):
            index = col + cols*row
            
            if index < arr.shape[0]:
                img = arr[index,:,:]
            else:
                img = np.ones((tile_size, tile_size))*200
            
            place_at_coords(full_image, img, cushion, row, col)
    
    
    return full_image
    
def place_at_coords(full_image, tile, cushion, row_index, col_index):
    tile_size = tile.shape[0]
    
    row_start_pixel = row_index * (tile_size + cushion)
    row_end_pixel = row_start_pixel + tile_size
    
    col_start_pixel = col_index * (tile_size + cushion)
    col_end_pixel = col_start_pixel + tile_size
    
    full_image[row_start_pixel:row_end_pixel, col_start_pixel:col_end_pixel] = tile

def pixel_arrs_to_img(context_arr, answers_arr):
    context_image = Image.fromarray(np.uint8(context_arr), mode="L")
    answers_image = Image.fromarray(np.uint8(answers_arr), mode="L")
    
    context_width = context_image.size[0]
    context_height = context_image.size[1]
    answers_width = answers_image.size[0]
    answers_height = answers_image.size[1]
    padding = int(context_width/60)
    ratio = float(context_width)/answers_width

    answers_image = answers_image.resize((context_width, int(round(answers_height*ratio))))
    
    full_image = Image.new('L',(2*padding + context_width, 3*padding + context_height + answers_image.size[1]), 0)
    full_image.paste(context_image, (padding, padding))
    full_image.paste(answers_image, (padding, 2*padding + context_height))
    
    return full_image

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True)