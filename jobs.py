from convert import ConvertImageProcess, ConvertVideoProcess
import os
import time
from rq import get_current_job
from firebase_admin import credentials, initialize_app, storage
from config import Config

def firebase_init(config):
    if not os.path.exists("key.json"):
        key_json_file = open("key.json", "w")
        json.dump(config.FIREBASE_KEY, key_json_file)
        key_json_file.close()
    
    cred = credentials.Certificate("key.json")
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

    if not os.path.isdir(config.TEMP) : os.mkdir(config.TEMP)
    if not os.path.isdir(config.OUTPUT) : os.mkdir(config.OUTPUT)

    file_path = os.path.join(config.TEMP, filename)
    temp_blob = bucket.blob(file_path)
    temp_blob.download_to_filename(file_path)
    temp_blob.delete()
    output_path = os.path.join(config.OUTPUT, filename)

    p = ConvertImageProcess(
        file_path, output_path, False,
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

    output_blob = bucket.blob(output_path)
    output_blob.upload_from_filename(output_path)
    os.remove(file_path)
    os.remove(output_path)

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

    if not os.path.isdir(config.TEMP) : os.mkdir(config.TEMP)
    if not os.path.isdir(config.OUTPUT) : os.mkdir(config.OUTPUT)

    file_path = os.path.join(config.TEMP, filename)
    print (file_path)
    temp_blob = bucket.blob(file_path)
    temp_blob.download_to_filename(file_path)
    temp_blob.delete()
    output_path = os.path.join(config.OUTPUT, filename)

    file_id = os.path.splitext(filename)[0]
    temp_batch_folder = os.path.join(config.TEMP, file_id + "/")

    p = ConvertVideoProcess(
        file_path, output_path, temp_batch_folder,
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

    output_blob = bucket.blob(output_path)
    output_blob.upload_from_filename(output_path)
    os.remove(file_path)
    os.remove(output_path)

    print ("- Video job", filename, "ended!")
    return filename