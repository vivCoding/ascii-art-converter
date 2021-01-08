import os

# class Config(object):
#     CORS = os.environ.get("CORS")

#     MAX_CONTENT_LENGTH = os.environ.get("MAX_CONTENT_LENGTH")

#     TEMP = os.getcwd() + os.environ.get("TEMP")
#     OUTPUT = os.getcwd() + os.environ.get("OUTPUT")
#     IMG_EXT = [
#         ".bmp", ".dib",
#         ".jpeg", ".jpg", ".jpe",
#         ".jp2",
#         ".png",
#         ".webp",
#         ".pbm", ".pgm", ".ppm", ".pxm", ".pnm",
#         ".pfm",
#         ".sr", ".ras",
#         ".tiff", ".tif",
#         ".exr",
#         ".hdr", ".pic"
#     ]

#     VID_EXT = [
#         ".mp4"
#     ]

#     PROGRESS_RATE = float(os.environ.get("PROGRESS_RATE"))

#     CONVERT_PROCESSES = int(os.environ.get("CONVERT_PROCESSES"))
#     CONVERT_THREADS = int(os.environ.get("CONVERT_THREADS"))

class Config(object):
    CORS = "*"

    MAX_CONTENT_LENGTH = 5242880

    TEMP = os.getcwd() + "/temp/"
    OUTPUT = os.getcwd() + "/output/"
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

    PROGRESS_RATE = 0.5

    CONVERT_PROCESSES = 4
    CONVERT_THREADS = 4