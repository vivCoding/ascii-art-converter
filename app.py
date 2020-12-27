from flask import Flask, request, redirect, jsonify, send_file, send_from_directory
from werkzeug.utils import secure_filename
import os
from flask_cors import CORS
from convert_image import convert_image_from_path_and_save
from convert_video import convert_video_from_path_and_save
from uuid import uuid4

app = Flask(__name__)
app.config.from_object("config.Config")
config = app.config
cors = CORS(app)

@app.route("/api/convert", methods=["POST"])
def convert():
    data = request.form
    fileUpload = request.files["fileUpload"]
    filename, file_ext = os.path.splitext(fileUpload.filename)
    file_id = uuid4().hex
    temp_path = os.path.join(config["TEMP"], file_id + file_ext)
    fileUpload.save(temp_path)
    output_path = config["OUTPUT"] + file_id

    if file_ext in config["IMG_EXT"]:
        convert_image_from_path_and_save(
            temp_path, output_path,
            reducer = int(data["imageReduction"]),
            fontSize = int(data["fontSize"]),
            spacing = float(data["spacing"]),
            maxsize = None if data["maxWidth"] == "" or data["maxHeight"] == "" else (int(data["maxWidth"]), int(data["maxHeight"])),
            chars = data["characters"],
            logs = True
        )
        os.remove(temp_path)
        return send_from_directory(config["OUTPUT"], file_id + ".txt.jpg", as_attachment=True, attachment_filename=filename + ".txt.jpg"), 200
    elif file_ext in config["VID_EXT"]:
        temp_batch_folder = os.path.join(config["TEMP"], file_id + "/")
        convert_video_from_path_and_save(
            temp_path, output_path,
            temp_folder=temp_batch_folder,
            frame_frequency=int(data["frameFrequency"]),
            image_reducer = int(data["imageReduction"]),
            fontSize = int(data["fontSize"]),
            spacing = float(data["spacing"]),
            maxsize = None if data["maxWidth"] == "" or data["maxHeight"] == "" else (int(data["maxWidth"]), int(data["maxHeight"])),
            chars = data["characters"],
            logs = True
        )
        os.remove(temp_path)
        return send_from_directory(config["OUTPUT"], file_id + ".txt.mp4", as_attachment=True, attachment_filename=filename + ".txt.mp4"), 200
    else:
        os.remove(temp_path)
        return jsonify("Bad format")

def thing():
    img = request.files["fileUpload"]
    imgId = uuid4().hex
    imgPath = os.path.join(app.config["TEMP"], secure_filename(imgId + "." + img.filename))
    outputPath = app.config["OUTPUT"] + imgId + "." + img.filename
    img.save(imgPath)
    print ("=" * 50)
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

