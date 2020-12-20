# Image/Video to ASCII Converter
Converts images or videos to text characters (ASCII art) based on pixel intensity.

Images are automatically outputted as `.txt.jpg` files, and videos as `.txt.mp4`

(The `.txt` is included to avoid accidentally overwriting original image)

## Installation

Be sure you have Python 3 or greater installed.

Developed on Python 3.8.6

### Dependencies:
- numpy
- opencv-python
- Pillow

These can be installed through `pip install -r requirements.txt`

## Image conversion

To convert images to ASCII art, use `convert_image.py`
```python convert_image.py path_to_image output_path image_reducer```

### Parameters explanation:
- `path_to_image`: path to your image to convert. Must include file extension
- `output_path`: path to output the final result
- `image_reducer`: percentage of image pixels to preserver
  - Use 100 to keep original
  - It is **highly recommended** to decrease this in order to be performant
  
### Examples

Converting `fox.png` and keeping 50% of pixels (skipping every other pixel). Final result will be `fox.txt.jpg`

```python convert_image.py fox.png fox 50```

## Video conversion

To convert videos to ASCII art, use `convert_video.py`
```python convert_video.py path_to_video output_path frame_frequency image_reducer```

### Parameters explanation:
- `path_to_video`: path to your video to convert. Must include file extension
- `output_path`: path to output the final result
- `frame_frequency`: determines how many frames to skip before capturing/converting a frame image
  - Keep 1 to keep all frames
  - It is **highly recommended** to increase this in order to be performant
- `image_reducer`: percentage of image pixels to preserver
  - 100 to keep original
  - It is **highly recommended** to decrease this in order to be performant
  
### Examples

Converting `funnyCatVideo.mp4`, keeping a third of the frames, and reducing image quality by 30%. Final result will be `funnyCatVideo.txt.mp4`

```python convert_video.py funnyCatVideo.mp4 funnyCatVideo 3 30```
