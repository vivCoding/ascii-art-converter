from flask import Flask, request, redirect, jsonify, send_file, send_from_directory, Response
from flask_cors import CORS
from werkzeug.utils import secure_filename
from uuid import uuid4
import os
import time
from convert_image import convert_image_process
from convert_video import convert_video_process

app = Flask(__name__)
app.config.from_object("config.Config")
config = app.config
cors = CORS(app)

jobs = {}

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
        p = convert_image_process(
            temp_path, output_path,
            image_reducer = int(data["imageReduction"]),
            fontSize = int(data["fontSize"]),
            spacing = float(data["spacing"]),
            maxsize = None if data["maxWidth"] == "" or data["maxHeight"] == "" else (int(data["maxWidth"]), int(data["maxHeight"])),
            chars = data["characters"],
            logs = False
        )
        p.start_process()
        jobs[file_id] = p
        return jsonify(file_id), 200
    elif file_ext in config["VID_EXT"]:
        temp_batch_folder = os.path.join(config["TEMP"], file_id + "/")
        p = convert_video_process(
            temp_path, output_path,
            temp_folder=temp_batch_folder,
            frame_frequency=int(data["frameFrequency"]),
            image_reducer = int(data["imageReduction"]),
            fontSize = int(data["fontSize"]),
            spacing = float(data["spacing"]),
            maxsize = None if data["maxWidth"] == "" or data["maxHeight"] == "" else (int(data["maxWidth"]), int(data["maxHeight"])),
            chars = data["characters"],
            logs = False
        )
        p.start_process()
        jobs[file_id] = p
        return jsonify(file_id), 200
    else:
        os.remove(temp_path)
        return jsonify("Bad format")

def cancel(job_id = None):
    jobs[job_id].terminate_process()
    terminated = jobs.pop(job_id, None)
    job_type_ext = os.path.splitext(terminated.output)[1]
    if job_type_ext == ".mp4":
        os.remove(terminated.video)
        terminated.cleanup_temp()
    else:
        os.remove(terminated.image_path)
    try:
        os.remove(terminated.output)
    except FileNotFoundError:
        pass
    return True

@app.route("/api/getprogress", methods=["POST"])
def get_progress():
    job_id = request.get_json()
    job = jobs[job_id]
    def progress_stream():
        try:
            while True:
                yield "data:" + str(job.get_progress()) + "\n\n"
                time.sleep(1)
        except GeneratorExit:
            print ("Client disconnected from progress stream")
            cancel(job_id)
    return Response(progress_stream(), mimetype="text/event-stream")

@app.route("/api/getoutput", methods=["POST"])
def get_output():
    job_id = request.get_json()
    done = jobs.pop(job_id, None)
    job_type_ext = os.path.splitext(done.output)[1]
    os.remove(done.video if job_type_ext == ".mp4" else done.image_path)
    return send_from_directory(config["OUTPUT"], job_id + ".txt" + job_type_ext, as_attachment=True), 200

@app.route("/api/cancel", methods=["POST"])
def cancel_conversion():
    job_id = request.get_json()
    cancelled = cancel(job_id)
    return jsonify(cancelled), 200

@app.route("/api/supportedfiles", methods=["GET"])
def supported_files():
    return send_from_directory(".", "supportedFiles.txt")

if __name__ == "__main__":
    print ("=" * 50)
    app.run(host="0.0.0.0", port=5000, debug=1)

