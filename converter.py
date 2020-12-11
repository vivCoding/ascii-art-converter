import numpy as np
import cv2
import sys, getopt

try:
    opt, args = getopt.getopt(sys.argv[1:], "i:o:r:")

    image_file = opt[0][1]
    output_file = opt[1][1]
    reducer = int(opt[2][1])
    inverted = False

    print ("Starting...")

    img = cv2.imread(image_file, 2)
    write_file = open(output_file, "w")

    chars = " .*:+%S0#@"
    div = np.amax(img) / (len(chars) - 1)

    for row in range(0,len(img), reducer):
        for col in range(0,len(img[row]), reducer):
            val = np.int_(img[row, col] / div)
            write_file.write(chars[val] + " ")
        write_file.write("\n")
    write_file.close()

    print ("Saved to " + output_file)
except IndexError:
    print ("Invalid parameters. Make sure you have all parameters!")
    print ("\t-i image to convert")
    print ("\t-o .txt file to output")
    print ("\t-r specified how often to skip rows/columns (useful for shrinking images)")

