from convert import ConvertImageProcess, ConvertVideoProcess
import os
import time
from rq import get_current_job
from firebase_admin import credentials, initialize_app, storage
import json
from config import Config

def firebase_init(config):
    path_to_key = os.path.join(os.getcwd(), "key.json")
    if not os.path.exists(path_to_key):
        key_json_file = open(path_to_key, "w")
        json.dump(config.FIREBASE_KEY, key_json_file)
        key_json_file.close()
    
    cred = credentials.Certificate(path_to_key)
    default_app = initialize_app(cred, {
        "storageBucket": config.FIREBASE_BUCKET
    })

def start_image_job(filename, image_reducer=10, fontSize=10, spacing=1.1,
                    maxsize=None, chars=" .*:+%S0#@", logs=False, threads=4):
    print ("=" * 70)
    print ("- Image job", filename, "started!")
    
    config = Config()
    firebase_init(config)
    bucket = storage.bucket()

    local_temp = os.path.join(os.getcwd(), config.TEMP)
    local_output = os.path.join(os.getcwd(), config.OUTPUT)
    if not os.path.isdir(local_temp) : os.mkdir(local_temp)
    if not os.path.isdir(local_output) : os.mkdir(local_output)

    print ("- Retrieving from Firebase...")
    file_path = os.path.join(config.TEMP, filename)
    local_file_path = os.path.join(os.getcwd(), file_path)
    temp_blob = bucket.blob(file_path)
    if temp_blob.exists():
        temp_blob.download_to_filename(local_file_path)
        temp_blob.delete()
    else:
        print ("- Could not be found!")
        return filename
    
    output_path = os.path.join(config.OUTPUT, filename)
    local_output_path = os.path.join(os.getcwd(), output_path)

    p = ConvertImageProcess(
        local_file_path, local_output_path, False,
        image_reducer, fontSize, spacing, maxsize, chars,
        logs, threads
    )
    p.start_process()

    rq_job = get_current_job()
    while True:
        rq_job.meta["progress"] = p.get_progress()
        rq_job.save_meta()
        if p.get_progress() >= 100:
            break
        time.sleep(0.1)

    p.join_process()
    rq_job.meta["uploading"] = "uploading"
    rq_job.save_meta()
    print ("- Uploading to Firebase...")
    output_blob = bucket.blob(output_path)
    output_blob.upload_from_filename(local_output_path)
    os.remove(local_file_path)
    os.remove(local_output_path)
    rq_job.meta["uploading"] = "finished"
    rq_job.save_meta()

    print ("- Image job", filename, "ended!")
    return filename


def start_video_job(filename, frame_frequency=24,
                    image_reducer=100, fontSize=10, spacing=1.1, maxsize=None,
                    chars=" .*:+%S0#@", logs=False, processes=4):
    print ("=" * 70)
    print ("- Video job", filename, "started!")
    
    config = Config()
    firebase_init(config)
    bucket = storage.bucket()

    local_temp = os.path.join(os.getcwd(), config.TEMP)
    local_output = os.path.join(os.getcwd(), config.OUTPUT)
    if not os.path.isdir(local_temp) : os.mkdir(local_temp)
    if not os.path.isdir(local_output) : os.mkdir(local_output)

    print ("- Retrieving from Firebase...")
    file_path = os.path.join(config.TEMP, filename)
    local_file_path = os.path.join(os.getcwd(), file_path)
    temp_blob = bucket.blob(file_path)
    if temp_blob.exists():
        temp_blob.download_to_filename(local_file_path)
        temp_blob.delete()
    else:
        print ("- Could not be found!")
        return filename

    output_path = os.path.join(config.OUTPUT, filename)
    local_output_path = os.path.join(os.getcwd(), output_path)

    file_id = os.path.splitext(filename)[0]
    temp_batch_folder = os.path.join(local_temp, file_id + "/")

    p = ConvertVideoProcess(
        local_file_path, local_output_path, temp_batch_folder,
        frame_frequency, image_reducer, fontSize, spacing,
        maxsize, chars, logs, processes
    )
    p.start_process()

    rq_job = get_current_job()
    while True:
        rq_job.meta["progress"] = p.get_progress()
        rq_job.save_meta()
        if p.get_progress() >= 100:
            break
        time.sleep(0.1)

    p.join_process()
    rq_job.meta["uploading"] = "uploading"
    rq_job.save_meta()
    print ("- Uploading to Firebase...")
    output_blob = bucket.blob(output_path)
    output_blob.upload_from_filename(local_output_path)
    os.remove(local_file_path)
    os.remove(local_output_path)
    rq_job.meta["uploading"] = "finished"
    rq_job.save_meta()

    print ("- Video job", filename, "ended!")
    return filename