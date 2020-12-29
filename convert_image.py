import numpy as np
import cv2
import sys
from PIL import Image, ImageFont, ImageDraw
import threading
from multiprocessing import Process, Value
import time

def convert_image(img, image_reducer=100, fontSize=10, spacing=1.1, maxsize=None, chars=" .*:+%S0#@", logs=False, progress_tracker=None):
    """Converts a cv2 image object into ASCII art

    Parameters
    ---------
    image: cv2 image
        cv2 image object to convert
    reducer : float
        percentage of pixels to keep
    fontSize : int
        determines font size when drawing on new picture
    spacing : int
        how much font spacing between characters
    maxsize : (int, int)
        tuple (width, height) representing max image size
    keepTxt : bool
        determines if to write the characters in an additional .txt file
    output_txt_file : string
        if keepTxt, output txt files to this path
    logs : bool
        determines if to print progress logs
    """

    try:
        if logs:
            start_time = time.time()
            print ("Initial configuring...")
        rows = len(img)
        cols = len(img[0])

        # set up image scaling based on font size and line spacing
        fontSize = 10
        spacing = 1.1
        reducer = int(100 / image_reducer)
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
        def convert_rows(start, end, progress_tracker, id=1):
            """Small function that converts a subset of rows into characters
            Does not draw to image yet. It just calculates which rows/cols have which chars

            Creates the final array of characters like so
            - col = (colNumber, char)
            - col_results = [col, ...]
            - row = (rowNumber, col_results)
            - results = [row, ....]
            - final_results = [result, ...] (length = number of threads)
            """
            rows = end - start
            results = []
            process_start = time.process_time()
            # if logs : print ("- Thread", str(id), "is starting at", process_start)
            for row in range(start, end, reducer):
                # if logs : print ("Converted rows", row, "/", rows, end="\r")
                col_results = []
                currentRow = row * scale
                for col in range(0, cols, reducer):
                    val = int(img[row, col] / div)
                    col_results.append((col * scale, chars[val]))
                results.append((currentRow, col_results))
                with progress_tracker.get_lock():
                    progress_tracker.value += progress_step
                    if logs : print ("Progress:", progress_tracker.value, "%", end="\r")
            # if logs : print ("- Thread", id ,"time took:", str(time.process_time() - process_start), "secs")
            final_results.append(results)

        # split up jobs with multithreading
        batches = 4
        rows_per_batch = int(rows / batches)
        threads = []
        if logs : print("Converting to ASCII...")
        for batch in range(batches):
            starting = rows_per_batch * batch
            convert_thread = threading.Thread(target=convert_rows, args=(starting, starting + rows_per_batch, progress_tracker, batch))
            convert_thread.start()
            threads.append(convert_thread)
        for t in threads:
            t.join()
        # after we converted, draw onto image (single thread)
        # if logs : print("Drawing to image...")
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
                    if logs : print ("Progress:", progress_tracker.value, "%", end="\r")
                # if logs : print ("- Batch", r, "/", batches, ", converted rows", row, "/", len(result), end="\r")
            # if logs : print ("")

        # if logs : print ("Completed creation!")

        # set max image
        if (maxsize is not None):
            if logs : print ("Reducing image size to " + str(maxsize) + "...")
            maxsize = (1920, 1080)
            output_img.thumbnail(maxsize, Image.NEAREST)

        with progress_tracker.get_lock():
            progress_tracker.value = 100
        
        if logs:
            print ("")
            print ("Progress:", progress_tracker.value, "%")
            print ("Time took:", str(time.time() - start_time), "secs")

        return output_img
    except Exception as e:
        print ("")
        print ("Uh oh image converting went wrong!")
        print (e)
        exit(0)


def convert_image_from_path_and_save(image_path, output_file="output", image_reducer=100, fontSize=10, spacing=1.1, maxsize=None, chars=" .*:+%S0#@", logs=False, progress_tracker=None):
    """Converts a cv2 image from a given path into ASCII art and saves it to disk

    Parameters
    ---------
    image_path : string
        path to image to convert
    output_file : string
        filename/path to output the final .jpg to
    all other parameters found in convert_image
    """
    if logs : print ("Loading image...")
    img = cv2.imread(image_path, 2)
    try:
        if img.size == 0 : print ("bad file")
        output = convert_image(img, image_reducer=image_reducer, fontSize=fontSize, spacing=spacing, maxsize=maxsize, chars=chars, logs=logs, progress_tracker=progress_tracker)
        if logs : print ("Saving image...")
        output.save(output_file + ".txt.jpg")
        if logs : print ("Saved to " + output_file + ".txt.jpg")
    except AttributeError:
        print ("File", image_path,"does not exist!")
        exit(0)

class convert_image_process:
    def __init__(self, image_path, output_file="output", image_reducer=100, fontSize=10, spacing=1.1, maxsize=None, chars=" .*:+%S0#@", logs=False):
        self.progress = Value("f", 0, lock=True)
        self.image_path = image_path
        self.output = output_file + ".txt.jpg"
        self.process = Process(target=convert_image_from_path_and_save, args=(
            image_path, output_file,
            image_reducer, fontSize, spacing, maxsize, chars,
            logs, self.progress
        ))
    
    def get_process(self):
        return self.process

    def start_process(self):
        self.process.start()
    
    def terminate_process(self):
        self.process.terminate()
        self.process.join()
        self.process.close()

    def get_progress(self):
        with self.progress.get_lock():
            return self.progress.value

if __name__ == "__main__":
    """You can also call this file with arguments
    """
    try:
        args = sys.argv[1:]
        image_file = args[0]
        output_file = args[1]
        reducer = int(args[2])
        convert_image_from_path_and_save(image_file, output_file, image_reducer=reducer, logs=True)
    except IndexError:
        print ("Invalid parameters. Make sure you have all parameters!")
        print ("image output reducer")
