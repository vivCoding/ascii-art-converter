import numpy as np
import cv2
import sys, getopt
from PIL import Image, ImageFont, ImageDraw

try:
    args = sys.argv[1:]

    image_file = args[0]
    output_file = args[1]
    reducer = int(args[2])

    print ("Starting...")

    img = cv2.imread(image_file, 2)
    write_file = open(output_file, "w")

    rows = len(img)
    cols = len(img[0])
    # create new image with white background
    fontSize = 8
    output_img = Image.new("L", (1920, 1080), color=0)
    draw = ImageDraw.Draw(output_img)
    font = ImageFont.truetype("DejaVuSans.ttf", fontSize, encoding="unic")

    chars = " .*:+%S0#@"
    # defines the subsets of pixel intensities
    # Can vary depending on max pixel intensity or length of char set
    div = np.amax(img) / (len(chars) - 1)

    for row in range(0, rows, reducer):
        line = ""
        for col in range(0, cols, reducer):
            val = np.int_(img[row, col] / div)
            line += chars[val]
            draw.text((col * fontSize / reducer, row * fontSize / reducer), chars[val], 255, font=font)
        # print(row)
        # draw.text((0, row * fontSize), line, 255, font=font)
        write_file.write(line)
        write_file.write("\n")
    write_file.close()

    output_img.save(output_file + ".png")

    print ("Saved to " + output_file)
except IndexError:
    print ("Invalid parameters. Make sure you have all parameters!")
    print ("converter.py imageToConvert nameForOutput reducer")

