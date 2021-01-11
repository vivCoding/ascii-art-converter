import os

class Config(object):
    CORS = os.environ.get("CORS")

    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH"))

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
        ".mp4",
        ".mkv"
    ]

    PROGRESS_RATE = float(os.environ.get("PROGRESS_RATE"))

    CONVERT_PROCESSES = int(os.environ.get("CONVERT_PROCESSES"))
    CONVERT_THREADS = int(os.environ.get("CONVERT_THREADS"))

    REDIS_URL = os.environ.get("REDIS_URL")
    FAILURE_TTL = int(os.environ.get("FAILURE_TTL"))
    RESULT_TTL = int(os.environ.get("RESULT_TTL"))
    JOB_TIMEOUT = int(os.environ.get("JOB_TIMEOUT"))

    FIREBASE_KEY = {
        "type": os.environ.get("TYPE"),
        "project_id": os.environ.get("PROJECT_ID"),
        "private_key_id": os.environ.get("PRIVATE_KEY_ID"),
        "private_key": os.environ.get("PRIVATE_KEY").replace("\\n", "\n"),
        "client_email": os.environ.get("CLIENT_EMAIL"),
        "client_id": os.environ.get("CLIENT_ID"),
        "auth_uri": os.environ.get("AUTH_URI"),
        "token_uri": os.environ.get("TOKEN_URI"),
        "auth_provider_x509_cert_url": os.environ.get("AUTH_PROVIDER"),
        "client_x509_cert_url": os.environ.get("CLIENT_CERTL_URL"),
    }
    FIREBASE_BUCKET = os.environ.get("FIREBASE_BUCKET")