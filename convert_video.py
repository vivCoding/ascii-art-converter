import numpy as np
import cv2
import glob
from convert_image import convert_image

def convert_video_from_path_and_save(video, frame_frequency=24, image_reducer=100):
    capture = cv2.VideoCapture(video)
    if not capture.isOpened():
        print ("Could not read vide. Please enter a valid video file!")
    
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
            converted = np.array(convert_image(frame, image_reducer, logs=True))
            if video_out is None:
                height, width = converted.shape
                size = (width, height)
                video_out = cv2.VideoWriter("output.mp4", fourcc, new_fps, size, isColor=False)
            video_out.write(converted)
        print ("Analyzing frames:", str(frames_count), "/", str(total_frames), "." * 10, "Frames included:", str(frames_included), end="\r")
    print ("")
    video_out.release()

    print("=" * 30)
    print ("SUMMARY:")
    print ("-" * 20)
    print ("Total frames:", str(frames_count))
    print ("Frames included:", str(frames_included))
    print ("Original FPS:", str(fps))
    print("New FPS:", str(new_fps))
    print ("Resolution:", str(size))

convert_video_from_path_and_save("videos/cat.mp4", 4, 20)