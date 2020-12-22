import numpy as np
import cv2
import sys
from PIL import Image, ImageFont, ImageDraw
import threading
import time

tests = 10

def convert_image(image, reducer=100, fontSize=10, spacing=1.1, maxsize=None, keepTxt=False, output_txt_file="output", logs=False):
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
        if logs : print ("Initial configuring...")
        # converting image to grayscale and getting image size
        img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
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

        for row in range(0, rows, reducer):
            print ("Converted rows", row, "/", rows, end="\r")
            currentRow = row * scale
            for col in range(0, cols, reducer):
                val = np.int_(img[row, col] / div)
                # we must write to exact pixel location, as to avoid varying line lengths
                draw.text((col * scale, currentRow), chars[val], 255, font=font)
                if keepTxt : write_file.write(chars[val] + " ")
            if keepTxt : write_file.write("\n")
        if keepTxt : write_file.close()

        # def convert_rows(start, end, id=1):
        #     thread_start = time.thread_time()
        #     print ("Thread", str(id), "is starting at", thread_start)
        #     for row in range(start, end, reducer):
        #         # if logs : print ("Converted rows", row, "/", rows, end="\r")
        #         currentRow = row * scale
        #         for col in range(0, cols, reducer):
        #             val = int(img[row, col] / div)
        #             # we must write to exact pixel location, as to avoid varying line lengths
        #             draw.text((col * scale, currentRow), chars[val], 255, font=font)
        #     print ("Thread", id ,"time took:", str(time.thread_time() - thread_start), "secs")
        #     print ("Thread", id, "ended at", time.time() - start_time, "secs")

        # sections = 4
        # r = int(rows / sections)
        # threads = []
        # print ("Starting threads...")
        # for section in range(sections):
        #     starting = r * section
        #     convert_thread = threading.Thread(target=convert_rows, kwargs={"start" : starting, "end" : starting + r, "id" : section})
        #     convert_thread.start()
        #     threads.append(convert_thread)

        # print ("Waiting...")
        # for t in threads:
        #     t.join()
        
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
    except Exception as e:
        print ("")
        print ("Uh oh image converting went wrong!")
        exit(0)


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
    img = cv2.imread(image_path)
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

    start_time = time.time()
    convert_image_from_path_and_save("images/lake.jpg", "output/lake", reducer=50)
    print ("Time took:", str(time.time() - start_time), "secs")
    # try:
    #     start_time = time.time()
    #     args = sys.argv[1:]
    #     image_file = args[0]
    #     output_file = args[1]
    #     reducer = int(args[2])
    #     convert_image_from_path_and_save(image_file, output_file, reducer=reducer)
    #     print ("Time took:", str(time.time() - start_time), "secs")
    # except IndexError:
    #     print ("Invalid parameters. Make sure you have all parameters!")
    #     print ("image output reducer")
