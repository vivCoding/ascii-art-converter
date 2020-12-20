import cv2
import glob

video = "./videos/costa.mp4"
temp = "./temp/"

capture = cv2.VideoCapture(video)
if not capture.isOpened():
    print ("nope")
    exit(0)

frame_frequency = 4
fps = capture.get(cv2.CAP_PROP_FPS)

total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
print ("Total frames:", str(total_frames))
frames_count = 0
frames_included = 0

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
new_fps = (total_frames / frame_frequency) / (total_frames / fps)
out = None

for i in range(total_frames):
    ret, frame = capture.read()
    if ret is False:
        continue
    frames_count += 1
    if frames_count % frame_frequency == 0:
        frames_included += 1
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if out is None:
            height, width = gray_frame.shape
            size = (width, height)
            out = cv2.VideoWriter("output.mp4", fourcc, new_fps, size, isColor=False)
        out.write(gray_frame)
    print ("Analyzing frames:", str(frames_count), "/", str(total_frames), "." * 10, "Frames included:", str(frames_included), end="\r")
print("")
out.release()

print("=" * 30)
print ("SUMMARY:")
print ("-" * 20)
print ("Total frames:", str(frames_count))
print ("Frames included:", str(frames_included))
print ("Original FPS:", str(fps))
print("New FPS:", str(new_fps))
print ("Resolution:", str(size))