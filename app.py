from flask import Flask, request, redirect, jsonify, send_file, send_from_directory, Response
from flask_cors import CORS
from werkzeug.utils import secure_filename
from uuid import uuid4
import os
import time
from convert import ConvertImageProcess, ConvertVideoProcess

app = Flask(__name__)
app.config.from_object("config.Config")
config = app.config
cors = CORS(app)

jobs = {}
max_jobs = config["MAX_JOBS"]
progress_update_rate = 0.5

@app.route("/api/convert", methods=["POST"])
def convert():
    data = request.form
    fileUpload = request.files["fileUpload"]
    filename, file_ext = os.path.splitext(fileUpload.filename)
    file_id = uuid4().hex
    temp_path = os.path.join(config["TEMP"], file_id + file_ext)
    fileUpload.save(temp_path)
    output_path = config["OUTPUT"] + file_id

    if len(jobs) >= max_jobs:
        print ("Too many jobs")
        return jsonify("max"), 200

    if file_ext in config["IMG_EXT"]:
        p = ConvertImageProcess(
            temp_path, output_path, override=False,
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
        p = ConvertVideoProcess(
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

def cancel(job_id):
    print ("Cancelled")
    jobs[job_id].terminate_process()
    terminated = jobs.pop(job_id, None)
    job_type_ext = os.path.splitext(terminated.output)[1]
    if job_type_ext == ".mp4":
        os.remove(terminated.video_path)
        terminated.cleanup_temp()
    else:
        os.remove(terminated.image_path)
    if os.path.isfile(terminated.output_path):
        os.remove(terminated.output_path)
    return True

@app.route("/api/getprogress", methods=["POST"])
def get_progress():
    print ("Getting progress")
    job_id = request.get_json()
    job = jobs[job_id]
    def progress_stream():
        try:
            while True:
                yield "data:" + str(job.get_progress()) + "\n\n"
                time.sleep(progress_update_rate)
        except GeneratorExit:
            if job.get_progress() < 100 and job_id in jobs:
                print ("Client disconnected from progress stream")
                cancel(job_id)
    return Response(progress_stream(), mimetype="text/event-stream")

@app.route("/api/getoutput", methods=["POST"])
def get_output():
    print ("Getting output")
    job_id = request.get_json()
    done = jobs.pop(job_id, None)
    job_type_ext = os.path.splitext(done.output)[1]
    os.remove(done.video_path if job_type_ext == ".mp4" else done.image_path)
    return send_from_directory(config["OUTPUT"], job_id + ".txt" + job_type_ext, as_attachment=True), 200

@app.route("/api/cancel", methods=["POST"])
def cancel_conversion():
    job_id = request.get_json()
    cancelled = cancel(job_id)
    return jsonify(cancelled), 200

if __name__ == "__main__":
    print ("=" * 50)
    app.run(host="0.0.0.0", port=5000, debug=1)

