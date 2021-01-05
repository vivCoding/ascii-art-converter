from flask import Flask, request, jsonify, send_from_directory, Response, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
from uuid import uuid4
import os
import time
from convert import ConvertImageProcess, ConvertVideoProcess

app = Flask(__name__)
app.config.from_object("config.Config")
cors = CORS(app, origins=app.config["CORS"])

IMG_EXT = app.config["IMG_EXT"]
VID_EXT = app.config["VID_EXT"]
TEMP = app.config["TEMP"]
OUTPUT= app.config["OUTPUT"]
MAX_JOBS = app.config["MAX_JOBS"]
PROGRESS_RATE = app.config["PROGRESS_RATE"]
MAX_PROCESSES = app.config["MAX_PROCESSES"]
MAX_THREADS = app.config["MAX_THREADS"]

jobs = {}
jobs_count = 0

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

# TODO: figure out how to avoid reading/writing from disk between different requests. DO NOT RELY ON THE SAME DYNO
# One solution is to maybe use an external database
# Another is to combine all the functions into one convert function. Return progress instead of an id.
# However, also have to figure out how to return the final output. And how to receive cancel input
# Another solution is to do websockets, 2 way communication

@app.route("/api/convert", methods=["POST"])
def convert():
    print ("-" * 20)
    print ("- Job request received")
    if not os.path.isdir(TEMP) : os.mkdir(TEMP)
    if not os.path.isdir(OUTPUT) : os.mkdir(OUTPUT)
    data = request.form
    if not os.path.isdir(TEMP) : os.mkdir(TEMP)
    if not os.path.isdir(OUTPUT) : os.mkdir(OUTPUT)
    
    fileUpload = request.files["fileUpload"]
    filename, file_ext = os.path.splitext(fileUpload.filename)
    file_id = uuid4().hex
    temp_path = os.path.join(TEMP, file_id + file_ext)
    fileUpload.save(temp_path)
    output_path = OUTPUT + file_id

    if len(jobs) >= MAX_JOBS:
        print ("Too many jobs")
        return jsonify("max"), 200
    

    global jobs_count
    jobs_count += 1
    if file_ext in IMG_EXT:
        p = ConvertImageProcess(
            temp_path, output_path + ".jpg", override=False,
            image_reducer = int(data["imageReduction"]),
            fontSize = int(data["fontSize"]),
            spacing = float(data["spacing"]),
            maxsize = None if data["maxWidth"] == "" or data["maxHeight"] == "" else (int(data["maxWidth"]), int(data["maxHeight"])),
            chars = data["characters"],
            logs = False,
            threads = MAX_THREADS
        )
        p.start_process()
        jobs[file_id] = p
        print (temp_path, ":", os.path.exists(temp_path))
        return jsonify(file_id), 200
    elif file_ext in VID_EXT:
        temp_batch_folder = os.path.join(TEMP, file_id + "/")
        p = ConvertVideoProcess(
            temp_path, output_path + ".mp4",
            temp_folder=temp_batch_folder,
            frame_frequency=int(data["frameFrequency"]),
            image_reducer = int(data["imageReduction"]),
            fontSize = int(data["fontSize"]),
            spacing = float(data["spacing"]),
            maxsize = None if data["maxWidth"] == "" or data["maxHeight"] == "" else (int(data["maxWidth"]), int(data["maxHeight"])),
            chars = data["characters"],
            logs = False,
            processes = MAX_PROCESSES
        )
        p.start_process()
        jobs[file_id] = p
        return jsonify(file_id), 200
    else:
        os.remove(temp_path)
        return jsonify("Bad format"), 200

def cancel(job_id):
    print ("- Cancelling")
    terminated = jobs.pop(job_id, None)
    if terminated is None:
        print (job_id, "is not running anymore!")
        return False
    terminated.terminate_process()
    job_type_ext = os.path.splitext(terminated.output_path)[1]
    if job_type_ext == ".mp4":
        os.remove(terminated.video_path)
        terminated.cleanup_temp()
    else:
        os.remove(terminated.image_path)
    if os.path.isfile(terminated.output_path):
        os.remove(terminated.output_path)
    print ("- Cancelled")
    return True

@app.route("/api/getprogress", methods=["POST"])
def get_progress():
    print ("- Getting progress")
    job_id = request.get_json()
    print (TEMP + job_id + ".jpg :", os.path.exists(TEMP + job_id + ".jpg"))
    job = jobs[job_id]
    def progress_stream():
        try:
            while True:
                yield "data:" + str(job.get_progress()) + "\n\n"
                time.sleep(PROGRESS_RATE)
        except GeneratorExit:
            if job.get_progress() < 100 and job_id in jobs:
                print ("- Client disconnected from progress stream")
                cancel(job_id)
    return Response(progress_stream(), mimetype="text/event-stream")

@app.route("/api/getoutput", methods=["POST"])
def get_output():
    print ("- Getting output")
    print (jobs)
    job_id = request.get_json()
    done = jobs.pop(job_id, None)
    print (done)
    job_type_ext = os.path.splitext(done.output_path)[1]
    os.remove(done.video_path if job_type_ext == ".mp4" else done.image_path)
    filename = secure_filename(job_id + job_type_ext)
    return send_from_directory(OUTPUT, filename, as_attachment=True), 200

@app.route("/api/cancel", methods=["POST"])
def cancel_conversion():
    job_id = request.get_json()
    cancelled = cancel(job_id)
    return jsonify(cancelled), 200

if __name__ == "__main__":
    print ("=" * 50)
    app.run(host="0.0.0.0")

