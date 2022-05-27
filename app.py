from flask import Flask
from flask import request, send_file, Response
from generate_custom import generate_concrete_json, generate_random_blueprint, generate_initials
from manual_main import gen_specific
from pipeline import generate_set, arr_to_img
from flask_cors import CORS
from io import BytesIO
import matplotlib.pyplot as plt
from zipfile import ZipFile


import sys
import os
import shutil
import numpy as np
import json

"""
to start the server on powershell
> $env:FLASK_APP = "app"
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
    blueprint = spec["blueprint"]
    initial = spec["initial"]
    human = spec["human"]

    return generate_concrete_json(blueprint, initial, human)

@app.route("/image", methods=["POST"])
def image():
    print("in function")
    spec = request.get_json()
    print("didnt get json")
    print(json.dumps(spec, indent=4))
    img, tar = gen_specific(spec)
    img = arr_to_img(img)

    return serve_pil_image(img)

@app.route("/file", methods=["post"])
def file():
    spec = request.get_json()
    img, tar = gen_specific(spec)

    return serve_npz(img, tar)

@app.route("/blueprint", methods=["POST"])
def blueprint():
    body = request.get_json()
    struct = body["structure"]
    if struct == "any":
        return generate_random_blueprint()
    else:
        return generate_random_blueprint(structure_list=[struct])

@app.route("/createset", methods=["POST"])
def createset():
    body = request.get_json()
    print(body)

    dirname = generate_set(count=body["count"], concept=body["concept"], level=body["mag"], genClass=body["genClass"], structure=body["structure"], only_concept=body["onlyConcept"])

    zipname = os.path.join("files", f"{body['concept']}_problems.zip")
    with ZipFile(zipname, "w") as zipObj:
        for foldername, subfolders, filenames in os.walk(dirname):
            for filename in filenames:
                if filename != "desktop.ini":
                    filepath = os.path.join(foldername, filename)
                    zipObj.write(filepath, filename)
    
    with open(zipname, "rb") as zipObj:
        data = zipObj.readlines()
    
    os.remove(zipname)
    shutil.rmtree(dirname)

    return Response(data, headers={
        'Content-Type': 'application/zip',
        'Content-Disposition': 'attachment; filename="%s_problems.zip"' % body["concept"]
    })


@app.route("/initials", methods=["POST"])
def initials():
    spec = request.get_json()
    blueprint = spec["blueprint"]
    human = spec["human"]

    return {"results": generate_initials(blueprint, human)}

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

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True)