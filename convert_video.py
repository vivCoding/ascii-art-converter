import numpy as np
import cv2
import glob
import sys
import os
import time
import shutil
from convert_image import convert_image, convert_image_from_path_and_save
import multiprocessing
import threading

def save_frames(start, end, video, batch_folder, frame_frequency, process_id=1):
    # we open a separate and independent capture for each process
    capture = cv2.VideoCapture(video)
    capture.set(cv2.CAP_PROP_POS_FRAMES, start)
    total_frames = end - start
    frames_count = 0
    frames_included = 0
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


def convert_and_save_image(filename, image_reducer, fontSize, spacing, maxsize):
    convert_image_from_path_and_save(filename + ".jpg", filename, reducer=image_reducer, fontSize=fontSize, spacing=spacing, maxsize=maxsize, logs=False)
    os.remove(filename + ".jpg")

def convert_batch(batch_folder, frames_per_batch, image_reducer, fontSize, spacing, maxsize, process_id):
    threads = []
    process_start = time.process_time()
    print ("- Process", process_id, "started at", process_start, frames_per_batch)
    for i in range(1, frames_per_batch + 1):
        filename =  batch_folder + str(i)
        convert_and_save_image(filename, image_reducer, fontSize, spacing, maxsize)
    #     convert_thread = threading.Thread(target=convert_and_save_image, args=(filename, image_reducer, fontSize, spacing, maxsize))
    #     convert_thread.start()
    #     threads.append(convert_thread)
    # for t in threads:
    #     t.join()
    print ("- Process", process_id, "finished at", str(time.process_time() - process_start), "secs")


def convert_video_from_path_and_save(video, output="output", frame_frequency=24, image_reducer=100, fontSize=10, spacing=1.1, maxsize=None):
    """Converts video from given path to ASCII art and saves it to disk

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
    total_frames = np.int_(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    frames_included = int(total_frames / frame_frequency)
    # total_frames / fps gives us our video duration.
    # We divide that by how many frames we can fit in our video, which gives us frames / video duration, also known as fps
    new_fps = (total_frames / frame_frequency) / (total_frames / fps)

    capture.release()

    """
    TODO: multithread this shit
    - create a new thread when saving a frame to file. Or split up video read at different places, and multithread read them
    - after saving files, multithread the conversion to ascii
    - after converting, single thread read them again and write to video
    """

    batches = multiprocessing.cpu_count()
    frames_per_batch = int(total_frames / batches / frame_frequency)
    temp_folder = "./temp/"
    os.mkdir(temp_folder)

    if __name__ == "__main__":
        all_args = []
        for batch in range(batches):
            starting_frame = batch * frames_per_batch * frame_frequency
            batch_folder = temp_folder + str(batch) + "/"
            os.mkdir(batch_folder)
            # TODO: catch if folder already exists
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

    # begin conversion


    if __name__ == "__main__":
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


    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    # set this none, as we don't know the final size of our images
    video_out = None

    print ("Writing to video...")
    for batch in range(batches):
        batch_folder = temp_folder + str(batch) + "/"
        for i in range(1, frames_per_batch + 1):
            try:
                img = cv2.imread(batch_folder + str(i) + ".txt.jpg", 2)
                if video_out is None:
                    height, width = img.shape
                    size = (width, height)
                    video_out = cv2.VideoWriter(output + ".txt.mp4", fourcc, new_fps, size, isColor=False)
                video_out.write(img)
                print ("Batch", batch, "/", batches, ", frames written", i, "/", frames_per_batch, end="\r")
            except AttributeError:
                print ("Cannot read", batch_folder + str(i) + ".txt.jpg")
                exit(0)
        print("")
        print("Finished writing batch", batch, "/", batches, "at", str(time.time() - start_time))
    shutil.rmtree(temp_folder)
    video_out.release()

    # for i in range(total_frames + 1):
    #     ret, frame = capture.read()
    #     if ret is False:
    #         continue
    #     frames_count += 1
    #     if frames_count % frame_frequency == 0:
    #         frames_included += 1
    #         print ("")
    #         converted = np.array(convert_image(frame, reducer=image_reducer, fontSize=fontSize, spacing=spacing, maxsize=maxsize, logs=True))
    #         if video_out is None:
    #             height, width = converted.shape
    #             size = (width, height)
    #             video_out = cv2.VideoWriter(output + ".txt.mp4", fourcc, new_fps, size, isColor=False)
    #         video_out.write(converted)
    #     print ("Analyzing frames:", str(frames_count), "/", str(total_frames), "." * 10, "Frames included:", str(frames_included), end="\r")
    # print ("")
    # video_out.release()

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
    # convert_video_from_path_and_save("./videos/cat.mp4", "./output/cat", frame_frequency=1, image_reducer=10)
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