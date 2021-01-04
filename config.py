import os

class Config(object):
    CORS = os.environ.get("CORS")

    TEMP = os.environ.get("TEMP")
    OUTPUT = os.environ.get("OUTPUT")
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

    MAX_JOBS = int(os.environ.get("MAX_JOBS"))
    PROGRESS_RATE = float(os.environ.get("PROGRESS_RATE"))

    MAX_PROCESSES = int(os.environ.get("MAX_PROCESSES"))
    MAX_THREADS = int(os.environ.get("MAX_THREADS"))