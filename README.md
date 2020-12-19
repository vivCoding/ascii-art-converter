# Image to ASCII Converter
Converts regular images to text characters based on pixel intensity

## Installation

Dependencies (can be installed via `pip`):

- numpy
- cv2
- PIL

## Usage

`python path_to_input_image outputFilename image_pixels_reducer`

### Example:

`python input.png output 80`

Takes input.png and creates an output.png, keeping 80% of the original image pixels.

### Parameters description:
- `path_to_input_image`: path to your image to convert. Must include file extension
- `outputFileName`: filename for output file
- `image_pixels_reducer`: percentage of image pixels to preserver (100 to keep original). It is recommended to decrease this in order to be performant
