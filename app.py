from flask import Flask, request, jsonify, send_from_directory, Response, render_template, json
from flask_cors import CORS
from werkzeug.utils import secure_filename

from redis import Redis
from rq import Queue
from rq.job import Job
from rq.command import send_stop_job_command

from uuid import uuid4
import os
import time

from jobs import *

app = Flask(__name__)
app.config.from_object("config.Config")
config = app.config
cors = CORS(app, origins=config["CORS"])

# TODO: define connection stuff thru env vars
redis = Redis("localhost")
queue = Queue(connection=redis)

IMG_EXT = config["IMG_EXT"]
VID_EXT = config["VID_EXT"]
TEMP = config["TEMP"]
OUTPUT= config["OUTPUT"]
PROGRESS_RATE = config["PROGRESS_RATE"]
CONVERT_PROCESSES = config["CONVERT_PROCESSES"]
CONVERT_THREADS = config["CONVERT_THREADS"]

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/api/convert", methods=["POST"])
def convert():
    print ("-" * 20)
    print ("- Job request received")
    data = request.form

    # TODO: check file upload size here
    fileUpload = request.files["fileUpload"]
    filename, file_ext = os.path.splitext(fileUpload.filename)
    file_id = uuid4().hex

    # TODO: get rid of this, as it is just temporary, before firebase is implemented
    filename, file_ext = os.path.splitext(fileUpload.filename)
    temp_path = os.path.join(TEMP, file_id + file_ext)
    fileUpload.save(temp_path)

    if file_ext in IMG_EXT:
        job = queue.enqueue(start_image_job,
            job_id = file_id,
            fileUpload = temp_path,
            file_id = file_id,
            temp_folder = TEMP,
            output_folder = OUTPUT,
            image_reducer = int(data["imageReduction"]),
            fontSize = int(data["fontSize"]),
            spacing = float(data["spacing"]),
            maxsize = None if data["maxWidth"] == "" or data["maxHeight"] == "" else (int(data["maxWidth"]), int(data["maxHeight"])),
            chars = data["characters"],
            logs = False,
            threads = CONVERT_THREADS
        )
        return jsonify(file_id), 200
    elif file_ext in VID_EXT:
        job = queue.enqueue(start_video_job,
            job_id = file_id,
            fileUpload = temp_path,
            file_id = file_id,
            temp_folder = TEMP,
            output_folder = OUTPUT,
            frame_frequency=int(data["frameFrequency"]),
            image_reducer = int(data["imageReduction"]),
            fontSize = int(data["fontSize"]),
            spacing = float(data["spacing"]),
            maxsize = None if data["maxWidth"] == "" or data["maxHeight"] == "" else (int(data["maxWidth"]), int(data["maxHeight"])),
            chars = data["characters"],
            logs = False,
            processes = CONVERT_THREADS
        )
        return jsonify(file_id), 200
    else:
        return jsonify("bad_format"), 200

@app.route("/api/getprogress", methods=["POST"])
def get_progress():
    print ("- Getting progress")
    job_id = request.get_json()
    job = Job.fetch(job_id, connection=redis)
    def progress_stream():
        try:
            while True:
                job.refresh()
                message = json.dumps({
                    "status": job.get_status(),
                    "progress": job.meta.get("progress", 0),
                    "result": str(job.result)
                })
                yield "data:" + message + "\n\n"
                time.sleep(PROGRESS_RATE)
        except GeneratorExit:
            if job.meta.get("progress", 0) < 100:
                print ("- Client disconnected from progress stream")
                try:
                    send_stop_job_command(redis, job_id)
                except:
                    print ("Failed to cancel", job_id)
    return Response(progress_stream(), mimetype="text/event-stream")

@app.route("/api/cancel", methods=["POST"])
def cancel_conversion():
    job_id = request.get_json()
    try:
        send_stop_job_command(redis, job_id)
        return jsonify("cancel_success"), 200
    except:
        return jsonify("cancel_failed"), 200

# TODO: this will have to be changed when firebase is implemented
@app.route("/api/getoutput", methods=["POST"])
def get_output():
    print ("- Getting output")
    filename = request.get_json()
    return send_from_directory(OUTPUT, filename, as_attachment=True), 200