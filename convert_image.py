import numpy as np
import cv2
import sys
from PIL import Image, ImageFont, ImageDraw
import threading
import multiprocessing
import time

def convert_rows(img, start, end, reducer, scale, div, cols, chars, id=1):
    rows = end - start
    results = []
    process_start = time.process_time()
    if __name__ == "__main__" : print ("- Thread", str(id), "is starting at", process_start)
    for row in range(start, end, reducer):
        if __name__ == "__main__" : print ("Converted rows", row, "/", rows, end="\r")
        col_results = []
        currentRow = row * scale
        for col in range(0, cols, reducer):
            val = int(img[row, col] / div)
            col_results.append((col * scale, chars[val]))
            # we must write to exact pixel location, as to avoid varying line lengths
            # draw.text((col * scale, currentRow), chars[val], 255, font=font)
        results.append((currentRow, col_results))
    if __name__ == "__main__" : print ("- Thread", id ,"time took:", str(time.process_time() - process_start), "secs")
    return results


def convert_image(img, reducer=100, fontSize=10, spacing=1.1, maxsize=None, keepTxt=False, output_txt_file="output", logs=False):
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

    # try:
    if logs : print ("Initial configuring...")
    # converting image to grayscale and getting image size
    # img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    rows = len(img)
    cols = len(img[0])

    # set up image scaling based on font size and line spacing
    fontSize = 10
    spacing = 1.1
    reducer = int(100 / reducer)
    scale = fontSize * 0.8 / reducer * spacing
    # create new image with black bacground (because white text on black looks cooler)
    output_img = Image.new("L", (int(cols * scale), int(rows * scale)), color=0)
    draw = ImageDraw.Draw(output_img)
    # load ttf font
    font = ImageFont.truetype("NotoMono-Regular.ttf", fontSize, encoding="unic")

    # set up txt file to write to
    if keepTxt : write_file = open(output_txt_file + ".txt", "w")

    chars = " .*:+%S0#@"
    # defines the subsets of pixel intensities
    # Can vary depending on max pixel intensity or length of char set
    div = np.amax(img) / (len(chars) - 1)

    if logs : print("Creating...")

    """Regular way"""
    # for row in range(0, rows, reducer):
    #     if logs : print ("Converted rows", row, "/", rows, end="\r")
    #     currentRow = row * scale
    #     for col in range(0, cols, reducer):
    #         val = np.int_(img[row, col] / div)
    #         # we must write to exact pixel location, as to avoid varying line lengths
    #         draw.text((col * scale, currentRow), chars[val], 255, font=font)
    #         if keepTxt : write_file.write(chars[val] + " ")
    #     if keepTxt : write_file.write("\n")
    # if keepTxt : write_file.close()

    """Multithreading"""
    # def convert_rows(start, end, id=1):
    #     thread_start = time.thread_time()
    #     if logs : print ("- Thread", str(id), "is starting at", thread_start)
    #     for row in range(start, end, reducer):
    #         if logs : print ("Converted rows", row, "/", rows, end="\r")
    #         currentRow = row * scale
    #         for col in range(0, cols, reducer):
    #             val = int(img[row, col] / div)
    #             # we must write to exact pixel location, as to avoid varying line lengths
    #             draw.text((col * scale, currentRow), chars[val], 255, font=font)
    #     if logs : print ("- Thread", id ,"time took:", str(time.thread_time() - thread_start), "secs")

    # sections = 4
    # r = int(rows / sections)
    # threads = []
    # for section in range(sections):
    #     starting = r * section
    #     convert_thread = threading.Thread(target=convert_rows, kwargs={"start" : starting, "end" : starting + r, "id" : section})
    #     convert_thread.start()
    #     threads.append(convert_thread)

    # for t in threads:
    #     t.join()

    # def result_draw(result, draw, chars):
    #     for row in range(len(result)):
    #         currentRow = result[row][0]
    #         cols = result[row][1]
    #         for col in cols:
    #             currentCol = col[0]
    #             val = col[1]
    #             draw.text((currentCol, currentRow), chars[val], 255, font=font)
    #         if logs : print ("Converted rows", row, "/", len(result), end="\r")

    """Mutliprocessing"""
    if __name__ != "__main__":    
        batches = multiprocessing.cpu_count()
        rows_per_batch = int(rows / batches)
        all_args = []
        processes = []
        for batch in range(batches):
            starting = rows_per_batch * batch
            args = (img, starting, starting + rows_per_batch, reducer, scale, div, cols, chars, batch)
            all_args.append(args)
            # convert_process = multiprocessing.
        with multiprocessing.Pool(batches) as p:
            results = p.starmap(convert_rows, all_args)
            p.close()
            p.join()
        # for p in processes:
        #     p.join()
        for result in results:
            for row in range(len(result)):
                currentRow = result[row][0]
                cols = result[row][1]
                for col in cols:
                    currentCol = col[0]
                    val = col[1]
                    draw.text((currentCol, currentRow), val, 255, font=font)
                if logs : print ("Converted rows", row, "/", len(result), end="\r")
    else:
        """Multithreading again"""
        final_results = []
        def convert_rows2(start, end, id=1):
            rows = end - start
            results = []
            process_start = time.process_time()
            if logs : print ("- Thread", str(id), "is starting at", process_start)
            for row in range(start, end, reducer):
                if logs : print ("Converted rows", row, "/", rows, end="\r")
                col_results = []
                currentRow = row * scale
                for col in range(0, cols, reducer):
                    val = int(img[row, col] / div)
                    col_results.append((col * scale, chars[val]))
                results.append((currentRow, col_results))
            if logs : print ("- Thread", id ,"time took:", str(time.process_time() - process_start), "secs")
            final_results.append(results)

        threads = []
        batches = 4
        rows_per_batch = int(rows / batches)
        all_args = []
        for batch in range(batches):
            starting = rows_per_batch * batch
            # convert_thread = threading.Thread(convert_rows(starting, starting + rows_per_batch, batch))
            convert_thread = threading.Thread(target=convert_rows2, args=(starting, starting + rows_per_batch, batch))
            convert_thread.start()
            threads.append(convert_thread)
        for t in threads:
            t.join()
        for result in final_results:
            for row in range(len(result)):
                currentRow = result[row][0]
                cols = result[row][1]
                for col in cols:
                    currentCol = col[0]
                    val = col[1]
                    draw.text((currentCol, currentRow), val, 255, font=font)
                if logs : print ("Converted rows", row, "/", len(result), end="\r")



    if logs:
        print ("")
        print ("Completed creation!")

    # set max image
    if (maxsize is not None):
        if logs : print ("Reducing image size to " + str(maxsize) + "...")
        maxsize = (1920, 1080)
        output_img.thumbnail(maxsize, Image.NEAREST)

    if keepTxt:
        if logs : print ("Saving txt file to", output_txt_file + ".txt")
        write_file.close()

    return output_img
    # except Exception as e:
    #     print ("")
    #     print ("Uh oh image converting went wrong!")
    #     exit(0)


def convert_image_from_path_and_save(image_path, output_file="output", reducer=100, fontSize=10, spacing=1.1, maxsize=None, keepTxt=False, logs=True):
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
        output = convert_image(img, reducer=reducer, fontSize=fontSize, spacing=spacing, maxsize=maxsize, keepTxt=keepTxt, output_txt_file=output_file, logs=logs)
        if logs : print ("Saving image...")
        output.save(output_file + ".txt.jpg")
        if logs : print ("Saved to " + output_file + ".txt.jpg")
    except AttributeError:
        print ("File", image_path,"does not exist!")
        exit(0)

if __name__ == "__main__":
    """You can also call this file with arguments
    """

    # start_time = time.time()
    # convert_image_from_path_and_save("images/lake.jpg", "output/lake", reducer=50)
    # print ("Time took:", str(time.time() - start_time), "secs")
    try:
        start_time = time.time()
        args = sys.argv[1:]
        image_file = args[0]
        output_file = args[1]
        reducer = int(args[2])
        convert_image_from_path_and_save(image_file, output_file, reducer=reducer)
        print ("Time took:", str(time.time() - start_time), "secs")
    except IndexError:
        print ("Invalid parameters. Make sure you have all parameters!")
        print ("image output reducer")
