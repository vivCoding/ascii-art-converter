import numpy as np
import cv2
import sys, getopt
from PIL import Image, ImageFont, ImageDraw

try:
    args = sys.argv[1:]

    image_file = args[0]
    output_file = args[1]
    reducer = np.int_(args[2])

    print ("Starting...")

    # read and get size of image
    img = cv2.imread(image_file, 2)
    rows = len(img)
    cols = len(img[0])

    # set up image scaling based on font size and line spacing
    fontSize = 10
    spacing = 1.1
    scale = fontSize * 0.8 / reducer * spacing
    # create new image with white background
    output_img = Image.new("L", (np.int_(cols * scale), np.int_(rows * scale)), color=0)
    draw = ImageDraw.Draw(output_img)
    # load ttf font
    font = ImageFont.truetype("NotoMono-Regular.ttf", fontSize, encoding="unic")

    # set up txt file to write to
    write_file = open(output_file, "w")

    chars = " .*:+%S0#@"
    # defines the subsets of pixel intensities
    # Can vary depending on max pixel intensity or length of char set
    div = np.amax(img) / (len(chars) - 1)

    for row in range(0, rows, reducer):
        currentRow = row * scale
        for col in range(0, cols, reducer):
            val = np.int_(img[row, col] / div)
            write_file.write(chars[val] + " ")
            # we must write to exact pixel location, as to avoid varying line lengths
            draw.text((col * scale, currentRow), chars[val], 255, font=font)
        write_file.write("\n")
    
    # save the files
    write_file.close()
    output_img.save(output_file + ".png")
    print ("Saved to " + output_file + ".png")
except IndexError:
    print ("Invalid parameters. Make sure you have all parameters!")
    print ("imageToConvert nameForOutput reducer")

