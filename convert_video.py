import numpy as np
import cv2
import glob
import sys
import os
import time
import shutil
from convert_image import *
import multiprocessing
import threading
import imageio

def save_frames(start, end, video, batch_folder, frame_frequency, process_id=1):
    # we open a separate and independent capture for each process
    capture = cv2.VideoCapture(video)
    capture.set(cv2.CAP_PROP_POS_FRAMES, start)
    total_frames = end - start
    frames_count = 0
    frames_included = 0
    # we utitlize multithreading for writing to disk
    threads = []
    process_start = time.process_time()
    print ("- Process", process_id, "started at", process_start)
    for i in range(total_frames):
        ret, frame = capture.read()
        if ret is False:
            continue
        frames_count += 1
        if frames_count % frame_frequency == 0:
            frames_included += 1
            filename = batch_folder + str(frames_included) + ".jpg"
            write_thread = threading.Thread(target=cv2.imwrite, args=(filename, frame))
            write_thread.start()
            threads.append(write_thread)
        print ("Saved frames:", frames_included, "/", total_frames, end="\r")
    for t in threads:
        t.join()
    capture.release()
    print ("- Process", process_id, "finished at", str(time.process_time() - process_start), "secs")

def convert_batch(batch_folder, frames_per_batch, image_reducer, fontSize, spacing, maxsize, process_id):
    # take every frame in batch folder and convert them
    process_start = time.process_time()
    print ("- Process", process_id, "started at", process_start, frames_per_batch)
    for i in range(1, frames_per_batch + 1):
        filename =  batch_folder + str(i)
        convert_image_from_path_and_save(filename + ".jpg", filename, reducer=image_reducer, fontSize=fontSize, spacing=spacing, maxsize=maxsize, logs=False)
        print ("Converted frames", i, "/", frames_per_batch, end="\r")
    print ("- Process", process_id, "finished at", str(time.process_time() - process_start), "secs")


def convert_video_from_path_and_save(video, output="output", frame_frequency=24, image_reducer=100, fontSize=10, spacing=1.1, maxsize=None):
    """Converts video from given path to ASCII art and saves it to disk as .txt.mp4 format

    Parameters
    --------
    video : str
        path to video to convert
    output : str
        path to output converted video
    frame_frequency : int
        determines how many frames to skip before capturing/converting.
        Keep at 1 if you want to retain all frames
    image_reducer : float
        percentage of pixels in image to keep
    all other parameters can be found in convert_image
    """

    capture = cv2.VideoCapture(video)
    if not capture.isOpened():
        print ("Could not read video. Please enter a valid video file!")
        exit(0)
    
    fps = capture.get(cv2.CAP_PROP_FPS)
    bitrate = int(capture.get(cv2.CAP_PROP_BITRATE))
    print (bitrate)
    total_frames = np.int_(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    frames_included = int(total_frames / frame_frequency)
    # total_frames / fps gives us our video duration.
    # We divide that by how many frames we can fit in our video, which gives us frames / video duration, also known as fps
    new_fps = (total_frames / frame_frequency) / (total_frames / fps)

    capture.release()

    # First, we grab all the frames we need and store them in a temp folder
    # After that, we convert all the image frames in the temp folder, and save them back in the temp folder
    # Then, we write them to video and save to disk
    # To utilize mutli processing, we separate grabbing frames and converting the frames into batches

    # initial setup
    batches = multiprocessing.cpu_count()
    frames_per_batch = int(total_frames / batches / frame_frequency)
    temp_folder = "./temp_convert_video/"
    try:
        os.mkdir(temp_folder)
    except FileExistsError:
        print ("Cannot create a temporary folder.", temp_folder, "already exists.")
        print ("Please delete or rename this folder to something else")
        exit(0)

    # grab the frames, and write to separate batch folders
    all_args = []
    for batch in range(batches):
        starting_frame = batch * frames_per_batch * frame_frequency
        batch_folder = temp_folder + str(batch) + "/"
        os.mkdir(batch_folder)
        args = (
            starting_frame,
            starting_frame + frames_per_batch * frame_frequency,
            video,
            batch_folder,
            frame_frequency,
            batch
        )
        all_args.append(args)
    print("Getting frames...")
    with multiprocessing.Pool(batches) as p:
        p.starmap(save_frames, all_args)
        p.close()
        p.join()

    # convert all the frames in each batch folder
    all_args = []
    for batch in range(batches):
        batch_folder = temp_folder + str(batch) + "/"
        args = (
            batch_folder,
            frames_per_batch,
            image_reducer,
            fontSize,
            spacing,
            maxsize,
            batch
        )
        all_args.append(args)
    print("Converting frames...")
    with multiprocessing.Pool(batches) as p:
        p.starmap(convert_batch, all_args)
        p.close()
        p.join()

    # video settings
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_out = imageio.get_writer(output + ".txt.mp4", fps=new_fps, quality=None, bitrate=(bitrate * 1024 * 2.5))
    size = None

    print ("Writing to video...")
    for batch in range(1, batches + 1):
        batch_folder = temp_folder + str(batch - 1) + "/"
        for i in range(1, frames_per_batch + 1):
            img = cv2.imread(batch_folder + str(i) + ".txt.jpg", 2)
            if size is None:
                height, width = img.shape   
                size = (width, height)
            video_out.append_data(img)
            print ("- Batch", batch, "/", batches, ", frames:", i, "/", frames_per_batch, end="\r")
        print("- Finished writing batch", batch, "/", batches, "at", str(time.time() - start_time))
    video_out.close()
    shutil.rmtree(temp_folder)

    print("=" * 30)
    print ("SUMMARY:")
    print ("-" * 20)
    print ("Total frames:", str(total_frames))
    print ("Frames included and converted:", str(frames_per_batch * batches))
    print ("Original FPS:", str(fps))
    print("New FPS:", str(new_fps))
    print ("Resolution:", str(size))
    print ("Saved to " + output + ".txt.mp4")

if __name__ == "__main__":
    """You can also call this file with arguments
    """
    try:
        start_time = time.time()
        args = sys.argv[1:]
        video = args[0]
        output = args[1]
        frame_frequency = np.int_(args[2])
        image_reducer = np.int_(args[3])
        convert_video_from_path_and_save(video, output, frame_frequency=frame_frequency, image_reducer=image_reducer)
        print ("Time took:", str(time.time() - start_time), "secs")
    except IndexError:
        print ("Invalid parameters. Make sure you have all parameters!")
        print ("video output frame_frequency image_reducer")