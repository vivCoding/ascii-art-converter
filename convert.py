import numpy as np
import cv2
from PIL import Image, ImageFont, ImageDraw
import glob
import os
import shutil
import time
import imageio
from multiprocessing import Process, Pool, Value
import threading
import sys
import getopt
import argparse

IMG_EXT = [
    ".bmp", ".dib",
    ".jpeg", ".jpg", ".jpe",
    ".jp2",
    ".png",
    ".webp",
    ".pbm", ".pgm", ".ppm", ".pxm", ".pnm",
    ".pfm",
    ".sr", ".ras",
    ".tiff", ".tif",
    ".exr",
    ".hdr", ".pic"
]

VID_EXT = [
    ".mp4"
]

MAX_PROCESSES = 4
MAX_THREADS = 4

def convert_image(img=None, image_reducer=10, fontSize=10, spacing=1.1, maxsize=None,
                    chars=" .*:+%S0#@", logs=False, progress_tracker=None):
    """Converts a cv2 image object into ASCII art

    Parameters
    ---------
    img: cv2 image
        - cv2 image object to convert
    reducer : float
        - percentage of pixels to keep
    fontSize : int
        - determines font size when drawing on new picture
    spacing : int
        - how much font spacing between characters
    maxsize : (int, int)
        - tuple (width, height) representing max image size
    chars : string
        - determines the chars to use when converting pixels
        - lowest pixel intensity to highest, from left to right
    logs : bool
        - determines whether or not to print progress logs
    progress_tracker : multiprocessing.Value
        - used to track overall conversion progress between all processes/threads
        - Value("f", 0, lock=True)
    """
    
    try:
        if logs:
            print ("Converting image...")
            start_time = time.time()
        rows = len(img)
        cols = len(img[0])

        # reducer takes image_reducer percentage, and will skip nth pixels when converting
        reducer = int(100 / image_reducer)
        # set up image scaling based on font size and line spacing
        scale = fontSize * 0.8 / reducer * spacing
        # create new image with black bacground (because white text on black looks cooler)
        output_img = Image.new("L", (int(cols * scale), int(rows * scale)), color=0)
        draw = ImageDraw.Draw(output_img)
        # load ttf font
        font = ImageFont.truetype("NotoMono-Regular.ttf", fontSize, encoding="unic")

        # defines the subsets of pixel intensities
        # Can vary depending on max pixel intensity or length of char set
        div = np.amax(img) / (len(chars) - 1)

        # will be used to track our overall conversion progress
        if progress_tracker is None:
            progress_tracker = Value("f", 0, lock=True)
        progress_step = 100 / (rows / reducer * 2)

        final_results = []
        def convert_rows(start, end, progress_tracker):
            """Small function that converts a subset of rows into characters. Used in multithreading
            Does not draw to image yet. Just calculates which rows/cols have which chars

            Creates the final array of characters like so
            - col = (colNumber, char)
            - col_results = [col, ...]
            - row = (rowNumber, col_results)
            - results = [row, ....]
            - final_results = [results, ...] (length = number of threads)
            - final_results = [
                [
                    (rowNumber, [
                        (colNumber, char),
                        (colNumber, char),
                        (colNumber, char),
                        ...
                    ]),
                    (rowNumber, [
                        (colNumber, char),
                        (colNumber, char),
                        (colNumber, char),
                        ...
                    ]),
                    ...
                ],
                ...
            ]
            """
            rows = end - start
            results = []
            process_start = time.process_time()
            for row in range(start, end, reducer):
                col_results = []
                currentRow = row * scale
                for col in range(0, cols, reducer):
                    val = int(img[row, col] / div)
                    col_results.append((col * scale, chars[val]))
                results.append((currentRow, col_results))
                with progress_tracker.get_lock():
                    progress_tracker.value += progress_step
                    if logs : print ("Progress: %.4f%%" % progress_tracker.value, end="\r")
            final_results.append(results)

        # split up jobs with multithreading
        batches = MAX_THREADS
        rows_per_batch = int(rows / batches)
        threads = []
        for batch in range(batches):
            starting = rows_per_batch * batch
            convert_thread = threading.Thread(target=convert_rows, args=(
                starting,
                starting + rows_per_batch,
                progress_tracker
            ))
            convert_thread.start()
            threads.append(convert_thread)
        for t in threads:
            t.join()
        
        # after we converted, draw onto image (single thread)
        for r in range(1, len(final_results) + 1):
            result = final_results[r - 1]
            for row in range(len(result)):
                currentRow = result[row][0]
                cols = result[row][1]
                for col in cols:
                    currentCol = col[0]
                    val = col[1]
                    draw.text((currentCol, currentRow), val, 255, font=font)
                with progress_tracker.get_lock():
                    progress_tracker.value += progress_step
                    if logs : print ("Progress: %.4f%%" % progress_tracker.value, end="\r")

        # set max image
        if (maxsize is not None):
            output_img.thumbnail(maxsize)

        # when we are done, there might be some rounding errors when converting some stuff to integers, thus it doesn't appear to be done
        # So we just simply set it to 100
        with progress_tracker.get_lock():
            progress_tracker.value = 100
        
        if logs:
            print ("Progress: %.4f%%" % progress_tracker.value)
            print ("Time took: %.4f secs" % (time.time() - start_time))

        return output_img
    except Exception as e:
        # don't know what exceptions may pop up
        print ("")
        print ("Uh oh image converting went wrong!")
        print (e)
        exit(0)

def convert_image_path_and_save(image_path, output_path="output.jpg", override=False,
                                image_reducer=10, fontSize=10, spacing=1.1, maxsize=None, chars=" .*:+%S0#@",
                                logs=False, progress_tracker=None):
    """Converts an image from a given path into ASCII art and saves it to disk

    Parameters
    ---------
    image_path : string
        - path to image to convert
    output_file : string
        - filename/path to output the final result
        - if extension is not specified, will automatically save as .jpg
    all other parameters found in convert_image
    """

    # check if the file actually exists first
    if os.path.isfile(image_path):
        if logs : print ("Loading image...")
        img = cv2.imread(image_path, 2)
        output = convert_image(
            img, image_reducer=image_reducer, fontSize=fontSize, spacing=spacing, maxsize=maxsize, chars=chars,
            logs=logs, progress_tracker=progress_tracker
        )
        if logs : print ("Saving image...")
        # if extension was not specified, automatically assign .jpg
        output_name, output_ext = os.path.splitext(output_path)
        if output_ext == "":
            output_ext = ".jpg"
        # if final output path was specified, then modify it (append _Copy to it)
        final_output_path = output_name + output_ext
        while not override and os.path.isfile(final_output_path):
            if logs : print (final_output_path, "already exists!")
            final_output_path = os.path.splitext(final_output_path)[0] + "_Copy" + output_ext
        output.save(final_output_path)
        if logs : print ("Saved to", final_output_path)
    else:
        print ("File", image_path, "does not exist!")
        exit(0)

class ConvertImageProcess:
    """Represents an independent process for an image conversion process.
    Key feature includes the ability to track progress of a conversion process

    Properties
    ----------
    progress : multiprocessing.Value
        - stores the progress of the image conversion
    image_path : string
        - stores image_path 

    Methods
    --------
    terminate_process
        - terminates the conversion process and closes it
    get_progress
        - returns the current progress of the conversion
    """
    def __init__(self, image_path, output_path="output.jpg", override=False,
                image_reducer=100, fontSize=10, spacing=1.1, maxsize=None, chars=" .*:+%S0#@", logs=False):
        self.progress = Value("f", 0, lock=True)
        self.image_path = image_path
        self.output_path = output_path
        self._process = Process(target=convert_image_path_and_save, args=(
            image_path, output_path, override,
            image_reducer, fontSize, spacing, maxsize, chars,
            logs, self.progress
        ))
    
    def get_process(self):
        return self._process

    def start_process(self):
        self._process.start()
    
    def join_process(self):
        self._process.join()
    
    def terminate_process(self):
        self._process.terminate()
        self._process.join()
        self._process.close()
    
    def get_progress(self):
        with self.progress.get_lock():
            return self.progress.value

def _save_frames(start, end, video, output_folder,
                frame_frequency, logs=False, progress_tracker=None, progress_step=None):
    """Takes a portion of a video and saves the frames as .jpg on disk

    Parameters
    ---------
    start : int
        - starting frame to convert video (inclusive)
    end : int
        - ending frame to convert video (exclusive)
    video : string
        - path to video to get frames from
    output_folder : string
        - path to save frames to
    frame_frequency : int
        - determines how often to save frames
        - to retain all frames, keep 1
    logs : bool
        - determines whether or not to print progress logs
    progress_tracker : multiprocessing.Value("f")
        - used to track overall conversion progress between all processes/threads
        - Value("f", 0, lock=True)
    progress_step : float
        - amount to progress step
    """
    # we open a separate and independent video capture for each process
    capture = cv2.VideoCapture(video)
    capture.set(cv2.CAP_PROP_POS_FRAMES, start)
    total_frames = end - start
    frames_count = 0
    frames_included = 0
    # we utitlize multithreading for writing to disk
    threads = []
    for i in range(total_frames):
        ret, frame = capture.read()
        if ret is False:
            continue
        frames_count += 1
        if frames_count % frame_frequency == 0:
            frames_included += 1
            filename = output_folder + str(frames_included) + ".jpg"
            write_thread = threading.Thread(target=cv2.imwrite, args=(filename, frame))
            write_thread.start()
            threads.append(write_thread)
            with progress_tracker.get_lock():
                progress_tracker.value += progress_step
                if logs : print ("Progress: %.4f%%" % progress_tracker.value, end="\r")
    for t in threads:
        t.join()
    capture.release()


def _convert_batch(batch_folder, frames_per_batch,
                image_reducer, fontSize, spacing, maxsize, chars,
                logs=False, progress_tracker=None, progress_step=None):
    """Converts all images from batch folder to ASCII art
    Images in folder should be numbered

    Parameters
    ---------
    batch_folder : string
        - path get images from
        - Images should be numbered 1 to frames_per_batch
    frames_per_batch : int
        - number of frames in folder needed to convert
    logs : bool
        - determines whether or not to print progress logs
    progress_tracker : multiprocessing.Value("f")
        - used to track overall conversion progress between all processes/threads
        - Value("f", 0, lock=True)
    progress_step : float
        - amount to progress step
    
    all other parameters found in convert_image
    """
    for i in range(1, frames_per_batch + 1):
        filename =  batch_folder + str(i) + ".jpg"
        convert_image_path_and_save(
            filename, filename, True,
            image_reducer, fontSize, spacing, maxsize, chars, logs=False
        )
        with progress_tracker.get_lock():
            progress_tracker.value += progress_step
            if logs : print ("Progress: %.4f%%" % progress_tracker.value, end="\r")

def convert_video_path_and_save(video_path, output_path="output.mp4", temp_folder = "./temp",
                                frame_frequency=24, image_reducer=100, fontSize=10, spacing=1.1, maxsize=None, chars=" .*:+%S0#@",
                                logs=False, progress_tracker=None):
    """Converts video from given path to ASCII art and saves it to disk as .txt.mp4 format

    Parameters
    --------
    video_path : str
        - path to video to convert
    output_path : str
        - path to output converted video
    temp_folder : str
        - folder to use to temporarily store converted images
    frame_frequency : int
        - determines how many frames to skip before capturing/converting.
        - Keep at 1 if you want to retain all frames
    image_reducer : float
        - percentage of pixels in video frame image to keep
    logs : bool
        - determines whether or not to print progress logs
    progress_tracker : multiprocessing.Value("f")
        - used to track overall conversion progress between all processes/threads
        - Value("f", 0, lock=True)
    
    all other parameters can be found in convert_image
    """

    if logs:
        start_time = time.time()
        print ("Converting video...")
    
    # set up a capture temporarily so we can grab some basic info about it
    capture = cv2.VideoCapture(video_path)
    if not capture.isOpened():
        print ("Could not read video. Please enter a valid video file!")
        exit(0)

    fps = capture.get(cv2.CAP_PROP_FPS)
    bitrate = int(capture.get(cv2.CAP_PROP_BITRATE))
    total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    frames_included = int(total_frames / frame_frequency)
    # total_frames / fps gives us our video duration.
    video_duration = total_frames / fps
    # frames included / video duration gives new fps
    new_fps = (total_frames / frame_frequency) / video_duration

    capture.release()

    # First, we grab all the frames we need and store them in a temp folder
    # After that, we convert all the image frames in the temp folder, and save them back in the temp folder
    # Then, we write them to video and save to disk
    # To utilize mutli processing, we separate grabbing frames and converting the frames into batches

    while os.path.isdir(temp_folder):
        temp_folder += "_"
    temp_folder += "/"
    os.mkdir(temp_folder)

    # initial setup
    # we divide our work into batches
    batches = MAX_PROCESSES
    frames_per_batch = int(total_frames / batches / frame_frequency)
    if progress_tracker is None:
        progress_tracker = Value("f", 0, lock=True)
    # progress: saved frames + converted frames + written frames
    progress_step = 100 / (frames_included * 3)

    # grab the frames, and write to separate batch folders
    save_frames_processes = []
    for batch in range(batches):
        starting_frame = batch * frames_per_batch * frame_frequency
        batch_folder = temp_folder + str(batch) + "/"
        os.mkdir(batch_folder)
        args = (
            starting_frame,
            starting_frame + frames_per_batch * frame_frequency,
            video_path,
            batch_folder,
            frame_frequency,
            logs,
            progress_tracker,
            progress_step
        )
        p = Process(target=_save_frames, args=args)
        p.daemon = True
        p.start()
        save_frames_processes.append(p)
    for p in save_frames_processes:
        p.join()

    # convert all the frames in each batch folder
    convert_processes = []
    for batch in range(batches):
        batch_folder = temp_folder + str(batch) + "/"
        args = (
            batch_folder,
            frames_per_batch,
            image_reducer,
            fontSize, spacing, maxsize, chars,
            logs, progress_tracker, progress_step
        )
        p = Process(target=_convert_batch, args=args)
        p.daemon = True
        p.start()
        convert_processes.append(p)
    for p in convert_processes:
        p.join()

    # if no extension was assigned, automatically assign .mp4
    output_name, output_ext = os.path.splitext(output_path)
    if output_ext == "":
        output_ext = ".mp4"
    # if final output path was specified, then modify it (append _Copy to it)
    final_output_path = output_name + output_ext
    while os.path.isfile(final_output_path):
        if logs : print (final_output_path, "already exists!")
        final_output_path = os.path.splitext(final_output_path)[0] + "_Copy" + output_ext

    # video settings
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_out = imageio.get_writer(final_output_path, fps=new_fps, quality=None, bitrate=(bitrate * 1024 * 2.5))
    size = None

    # write images to new video
    for batch in range(1, batches + 1):
        batch_folder = temp_folder + str(batch - 1) + "/"
        for i in range(1, frames_per_batch + 1):
            img = cv2.imread(batch_folder + str(i) + ".jpg", 2)
            if size is None:
                height, width = img.shape
                size = (width, height)
            video_out.append_data(img)
            with progress_tracker.get_lock():
                progress_tracker.value += progress_step
                if logs : print ("Progress: %.4f%%" % progress_tracker.value, end="\r")
    video_out.close()
    shutil.rmtree(temp_folder)

    # when we are done, there might be some rounding errors when converting some stuff to integers, thus it doesn't appear to be done
    # So we just simply set it to 100
    with progress_tracker.get_lock():
        progress_tracker.value = 100

    if logs:
        print ("=" * 30)
        print ("SUMMARY:")
        print ("-" * 20)
        print ("Progress: %.4f%%" % progress_tracker.value)
        print ("Total frames found:", str(total_frames))
        print ("Frames included and converted:", str(frames_per_batch * batches))
        print ("Original FPS:", str(fps))
        print("New FPS:", str(new_fps))
        print ("Resolution:", str(size))
        print ("Saved to", final_output_path)
        print ("Time took: %.4f secs" % (time.time() - start_time))

class ConvertVideoProcess:
    """Represents an independent process for a video conversion process.
    Key feature includes the ability to track progress of a conversion process

    Properties
    ----------
    progress : multiprocessing.Value
        - stores the progress of the image conversion
    video_path : string
        - video path to convert
    output_path : string
        - output path of final video result
    process : multiprocessing.Process
        - Process where the function for converting video is executed
    
    Methods
    --------
    terminate_process
        - terminates the conversion process and closes it
    cleanup_temp
        - removes lingering files/folder in temp folder
    get_progress
        - returns the current progress of the conversion
    """
    def __init__(self, video_path, output_path="output.mp4", temp_folder = "./temp",
                frame_frequency=24, image_reducer=100, fontSize=10, spacing=1.1,
                maxsize=None, chars=" .*:+%S0#@", logs=False):
        self.progress = Value("f", 0, lock=True)
        self.video_path = video_path
        self.output_path = output_path
        self.temp_folder = temp_folder
        self._process = Process(target=convert_video_path_and_save, args =(
            video_path, output_path, temp_folder,
            frame_frequency, image_reducer, fontSize,
            spacing, maxsize, chars, logs, self.progress
        ))
    
    def get_process(self):
        return self._process

    def start_process(self):
        self._process.start()
    
    def join_process(self):
        self._process.join()

    def terminate_process(self):
        self._process.terminate()
        self._process.join()
        self._process.close()

    def cleanup_temp(self):
        shutil.rmtree(self.temp_folder)

    def get_progress(self):
        with self.progress.get_lock():
            return self.progress.value

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        usage="%(prog)s <path_to_image_video> [path_to_output] [OPTIONS] [-h]",
        description="ASCII Art Converter: Converts regular images/videos into ASCII art, adding some \"text-ure\" to it!"
    )
    parser.add_argument(
        "path_to_file",
        help="File path to file (image or video) to convert"        
    )

    parser.add_argument(
        "path_to_output",
        help="Optional. File path to put converted and final image/video. Default is ./output.jpg (.mp4 if video)",
        nargs="?",
        default="output"
    )

    parser.add_argument(
        "-i", "--image_reducer",
        type=int,
        dest="image_reducer",
        metavar="PERCENTAGE",
        choices=range(1, 101),
        default=10,
        help="Percentage (0 - 100) of how many pixels will be converted to text. The higher the value, the higher the final image size. Default is 10"
    )

    parser.add_argument(
        "-z", "--fontSize",
        type=float,
        dest="fontSize",
        metavar="SIZE",
        choices=range(0, 100),
        default=10,
        help="Font size for the characters. Default is 10"
    )

    parser.add_argument(
        "-s,", "--spacing",
        type=float,
        dest="spacing",
        metavar="SPACING",
        default=1.1,
        help="Line spacing between each character. Default is 1.1"
    )

    parser.add_argument(
        "-c", "--chars",
        dest="chars",
        metavar='"CHARS"',
        default=" .*:+%S0#@",
        help='Characters to use when converting the pixel intensities. From left to right, lower intensity to higher intensity. Default is " .*:+%%S0#@". Must wrap parameter in quotation marks'
    )

    parser.add_argument(
        "-wh", "--maxsize",
        type=int,
        dest="maxsize",
        metavar="PX",
        default=None,
        nargs=2,
        help="Max width and height of final output in pixels. Default is no max"
    )

    parser.add_argument(
        "-f", "--frame_frequency",
        type=int,
        dest="frame_frequency",
        metavar="FRAME_FREQUENCY",
        choices=range(1, 9999),
        default=24,
        help="VIDEO ONLY. Determines how many frames to skip before capturing/converting. Keep 1 to preserve all frames and FPS. Default is 24"
    )

    args = parser.parse_args()

    if os.path.isfile(args.path_to_file):
        file_type = os.path.splitext(args.path_to_file)[1]
        if file_type in IMG_EXT:
            convert_image_path_and_save(
                args.path_to_file, args.path_to_output, False,
                args.image_reducer, args.fontSize, args.spacing,
                args.maxsize, args.chars, logs=True
            )
        elif file_type in VID_EXT:
            convert_video_path_and_save(
                args.path_to_file, args.path_to_output, "./temp",
                args.frame_frequency, args.image_reducer, args.fontSize, args.spacing,
                args.maxsize, args.chars, logs=True
            )
    else:
        print ("File", args.path_to_file,"could not be found!")

    # try:
    #     args = sys.argv[1:]
    #     file_path = args[0]
    #     output_path = args[1]
    #     file_type = os.path.splitext(file_path)
    #     args = parser.parse_args()        
    # except:
    #     print ("Invalid parameters!")

