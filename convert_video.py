import numpy as np
import cv2
import glob
import sys
from convert_image import convert_image

def convert_video_from_path_and_save(video, output="output", frame_frequency=24, image_reducer=100, fontSize=10, spacing=1.1, maxsize=None):
    """Converts video from given path to ASCII art and saves it to disk

    Parameters
    --------
    video : str
        path to video to convert
    output : str
        path to output converted video
    frame_frequency : int
        determines how many frames to skip before capturing/converting.
        Keep at 1 if you want to retain all frames
    image_reducer : float
        percentage of pixels in image to keep
    all other parameters can be found in convert_image
    """

    capture = cv2.VideoCapture(video)
    if not capture.isOpened():
        print ("Could not read video. Please enter a valid video file!")
        exit(0)
    
    fps = capture.get(cv2.CAP_PROP_FPS)
    total_frames = np.int_(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    # total_frames / fps gives us our video duration.
    # We divide that by how many frames we can fit in our video, which gives us frames / video duration, also known as fps
    new_fps = (total_frames / frame_frequency) / (total_frames / fps)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    # set this none, as we don't know the final size of our images
    video_out = None
    
    frames_count = 0
    frames_included = 0

    for i in range(total_frames + 1):
        ret, frame = capture.read()
        if ret is False:
            continue
        frames_count += 1
        if frames_count % frame_frequency == 0:
            frames_included += 1
            print ("")
            converted = np.array(convert_image(frame, reducer=image_reducer, fontSize=fontSize, spacing=spacing, maxsize=maxsize, logs=True))
            if video_out is None:
                height, width = converted.shape
                size = (width, height)
                video_out = cv2.VideoWriter(output + ".txt.mp4", fourcc, new_fps, size, isColor=False)
            video_out.write(converted)
        print ("Analyzing frames:", str(frames_count), "/", str(total_frames), "." * 10, "Frames included:", str(frames_included), end="\r")
    print ("")
    video_out.release()

    print("=" * 30)
    print ("SUMMARY:")
    print ("-" * 20)
    print ("Total frames:", str(frames_count))
    print ("Frames included and converted:", str(frames_included))
    print ("Original FPS:", str(fps))
    print("New FPS:", str(new_fps))
    print ("Resolution:", str(size))
    print ("Saved to " + output + ".txt.mp4")

if __name__ == "__main__":
    """You can also call this file with arguments
    """
    try:
        args = sys.argv[1:]
        video = args[0]
        output = args[1]
        frame_frequency = np.int_(args[2])
        image_reducer = np.int_(args[3])
        convert_video_from_path_and_save(video, output, frame_frequency=frame_frequency, image_reducer=image_reducer)
    except IndexError:
        print ("Invalid parameters. Make sure you have all parameters!")
        print ("video output frame_frequency image_reducer")