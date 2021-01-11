from flask import Flask, request, jsonify, send_from_directory, Response, render_template, json
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

from redis import Redis
from rq import Queue
from rq.job import Job
from rq.command import send_stop_job_command

from firebase_admin import credentials, initialize_app, storage

from uuid import uuid4
import os
import time

from jobs import *

app = Flask(__name__)
app.config.from_object("config.Config")
config = app.config
cors = CORS(app, origins=config["CORS"])

if config["REDIS_URL"] != "unavailable":
    redis = Redis(config["REDIS_URL"])
    queue = Queue(connection=redis)

TEMP = config["TEMP"]
OUTPUT= config["OUTPUT"]
IMG_EXT = config["IMG_EXT"]
VID_EXT = config["VID_EXT"]
PROGRESS_RATE = config["PROGRESS_RATE"]
CONVERT_PROCESSES = config["CONVERT_PROCESSES"]
CONVERT_THREADS = config["CONVERT_THREADS"]

FAILURE_TTL = config["FAILURE_TTL"]
RESULT_TTL = config["RESULT_TTL"]
JOB_TIMEOUT = config["JOB_TIMEOUT"]

path_to_key = os.path.join(os.getcwd(), "key.json")
if not os.path.exists(path_to_key):
    key_json_file = open(path_to_key, "w")
    json.dump(config["FIREBASE_KEY"], key_json_file)
    key_json_file.close()

cred = credentials.Certificate(path_to_key)
default_app = initialize_app(cred, {
    "storageBucket": config["FIREBASE_BUCKET"]
})
bucket = storage.bucket()

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/api/convert", methods=["POST"])
def convert():
    print ("-" * 20)
    print ("- Job request received")

    if config["REDIS_URL"] == "unavailable":
        return jsonify("unavailable"), 404

    try:
        data = request.form
        fileUpload = request.files["fileUpload"]
        filename, file_ext = os.path.splitext(fileUpload.filename)
        
        local_temp = os.path.join(os.getcwd(), TEMP)
        local_output = os.path.join(os.getcwd(), TEMP)
        if not os.path.isdir(local_temp) : os.mkdir(local_temp)
        if not os.path.isdir(local_output) : os.mkdir(local_output)

        # filename will consist of random hex and file_ext
        filename = secure_filename(uuid4().hex + file_ext)
        temp_path = os.path.join(TEMP, filename)
        local_temp_path = os.path.join(os.getcwd(), temp_path)
        fileUpload.save(local_temp_path)
    except RequestEntityTooLarge as e:
        print ("- File too large!")
        return jsonify("large_file"), 413

    if file_ext in IMG_EXT:
        try:
            blob = bucket.blob(temp_path)
            blob.upload_from_filename(local_temp_path)
        except:
            os.remove(local_temp_path)
            return jsonify("firebase_error"), 503
        job = queue.enqueue(start_image_job,
            job_id = filename, failure_ttl = 60, job_timeout = 300, result_ttl = 60,
            filename = filename,
            image_reducer = int(data["imageReduction"]),
            fontSize = int(data["fontSize"]),
            spacing = float(data["spacing"]),
            maxsize = None if data["maxWidth"] == "" or data["maxHeight"] == "" else (int(data["maxWidth"]), int(data["maxHeight"])),
            chars = data["characters"],
            logs = True,
            threads = CONVERT_THREADS
        )
        os.remove(local_temp_path)
        return jsonify(filename), 200
    elif file_ext in VID_EXT:
        try:
            blob = bucket.blob(temp_path)
            blob.upload_from_filename(local_temp_path)
        except:
            return jsonify("firebase_error"), 503
        job = queue.enqueue(start_video_job,
            job_id = filename, failure_ttl = 60, job_timeout = 300, result_ttl = 60,
            filename = filename,
            frame_frequency=int(data["frameFrequency"]),
            image_reducer = int(data["imageReduction"]),
            fontSize = int(data["fontSize"]),
            spacing = float(data["spacing"]),
            maxsize = None if data["maxWidth"] == "" or data["maxHeight"] == "" else (int(data["maxWidth"]), int(data["maxHeight"])),
            chars = data["characters"],
            logs = True,
            processes = CONVERT_PROCESSES
        )
        os.remove(local_temp_path)
        return jsonify(filename), 200
    else:
        os.remove(local_temp_path)
        return jsonify("bad_format"), 415

def cancel(job_id):
    job = Job.fetch(job_id, connection=redis)
    temp_blob = bucket.blob(os.path.join(TEMP, job_id))
    output_blob = bucket.blob(os.path.join(OUTPUT, job_id))
    if temp_blob.exists() : temp_blob.delete()
    if output_blob.exists() : output_blob.delete()
    try:
        if job.get_status() == "started":
            send_stop_job_command(redis, job_id)
            print ("- Stopped executing job", job_id)
            return True
        elif job.get_status() == "queued":
            queue.remove(job_id)
            print ("- Removed job from queue", job_id)
            return True
        else:
            print ("- No job found for", job_id)
    except:
        print ("- No job found for", job_id)
    return False

@app.route("/api/getprogress", methods=["POST"])
def get_progress():
    print ("- Getting progress")
    # job_id and filename are the same thing
    job_id = secure_filename(request.get_json())
    job = Job.fetch(job_id, connection=redis)
    def progress_stream():
        try:
            while True:
                job.refresh()
                message = json.dumps({
                    "status": job.meta.get("uploading", job.get_status()),
                    "progress": job.meta.get("progress", 0),
                    "result": str(job.result)
                })
                yield "data:" + message + "\n\n"
                time.sleep(PROGRESS_RATE)
        except GeneratorExit:
            if job.get_status() != "finished":
                print ("- Client disconnected from progress stream")
                cancel(job_id)
                
    return Response(progress_stream(), mimetype="text/event-stream")

@app.route("/api/cancel", methods=["POST"])
def cancel_conversion():
    print ("- Canceling")
    job_id = secure_filename(request.get_json())
    cancelable = cancel(job_id)
    if cancelable:
        print ("- Canceled")
        return jsonify("cancel_success"), 200
    else:
        return jsonify("cancel_failed"), 200

@app.route("/api/getoutput", methods=["POST"])
def get_output():
    print ("- Getting output")
    try:
        filename = secure_filename(request.get_json())
        file_path = os.path.join(OUTPUT, filename)
        blob = bucket.blob(file_path)
        blob.download_to_filename(file_path)
        blob.delete()
        print ("- Got output", file_path)
        return send_from_directory(OUTPUT, filename, as_attachment=True), 200
    except Exception as e:
        print (e)
        return jsonify("firebase_error"), 503