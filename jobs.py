from convert import ConvertImageProcess, ConvertVideoProcess
import os
import time
from rq import get_current_job

# TODO: store output file on firebase instead of local disk

def start_image_job(fileUpload, file_id, temp_folder, output_folder,
                    image_reducer=10, fontSize=10, spacing=1.1,
                    maxsize=None, chars=" .*:+%S0#@",logs=False, threads=4):
    print ("=" * 70)
    print ("- Image job", file_id, "started!")
    # if not os.path.isdir(temp_folder) : os.mkdir(temp_folder)
    # if not os.path.isdir(output_folder) : os.mkdir(output_folder)

    # filename, file_ext = os.path.splitext(fileUpload.filename)
    # temp_path = os.path.join(temp_folder, file_id + file_ext)
    # fileUpload.save(temp_path)
    temp_path = fileUpload
    output_path = os.path.join(output_folder, file_id)

    p = ConvertImageProcess(
        temp_path, output_path + ".jpg", False,
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
    print ("- Image job", file_id, "ended!")
    return file_id + ".jpg"


def start_video_job(fileUpload, file_id, temp_folder, output_folder, frame_frequency=24,
                    image_reducer=100, fontSize=10, spacing=1.1, maxsize=None,
                    chars=" .*:+%S0#@", logs=False, processes=4):
    print ("=" * 70)
    print ("- Video job", file_id, "started!")
    # if not os.path.isdir(temp_folder) : os.mkdir(temp_folder)
    # if not os.path.isdir(output_folder) : os.mkdir(output_folder)
    
    # filename, file_ext = os.path.splitext(fileUpload.filename)
    # temp_path = os.path.join(temp_folder, file_id + file_ext)
    # fileUpload.save(temp_path)
    temp_path = fileUpload
    output_path = os.path.join(output_folder, file_id)
    temp_batch_folder = os.path.join(temp_folder, file_id)

    p = ConvertVideoProcess(
        temp_path, output_path, temp_batch_folder,
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
    print ("- Video job", file_id, "ended!")
    return file_id + ".mp4"