from flask import Flask, request, redirect, jsonify, send_file, send_from_directory
from werkzeug.utils import secure_filename
import os
from flask_cors import CORS
from convert_image import convert_image_from_path_and_save
from uuid import uuid4

app = Flask(__name__)
app.config.from_object("config.Config")
cors = CORS(app)

@app.route("/api/convertimage", methods=["POST"])
def convert_image():
    data = request.form
    img = request.files["fileUpload"]
    imgId = uuid4().hex
    imgPath = os.path.join(app.config["TEMP"], secure_filename(imgId + "." + img.filename))
    outputPath = app.config["OUTPUT"] + imgId + "." + img.filename
    img.save(imgPath)
    print (imgPath)
    convert_image_from_path_and_save(
        imgPath, outputPath,
        reducer = int(data["imageReduction"]),
        fontSize = int(data["fontSize"]),
        spacing = float(data["spacing"]),
        maxsize = None if data["maxWidth"] == "" or data["maxHeight"] == "" else (int(data["maxWidth"]), int(data["maxHeight"])),
        chars = data["characters"],
        logs = True
    )
    os.remove(imgPath)
    return send_from_directory(app.config["OUTPUT"], imgId + "." + img.filename + ".txt.jpg", as_attachment=True), 200
    # return jsonify("works"), 200

if __name__ == "__main__":
    print ("=" * 50)
    app.run(host="0.0.0.0", port=5000, debug=1)

