# ASCII Art Converter
Converts regular images or videos into text characters (ASCII art), based on pixel intensity, giving it some extra "text-ure"!

Developed with Python 3.8.6

## Installation

Be sure you have Python 3 or greater installed.

Dependencies are found in `requirements.txt`. They can be installed using command: `pip install -r requirements.txt`

<!-- **Known issue with Pillow:** https://github.com/python-pillow/Pillow/issues/4225

Solution: `pip install --compile --install-option=-O1 Pillow` -->

## Usage

```
python convert.py <path_to_image_video> [path_to_output] [OPTIONS] [-h]
```

### Positional Arguments
- `path_to_file` : File path to file (image or video) to convert
- `path_to_output` : Optional. File path to put converted and final image/video. File extension is also optional. Default is ./output.jpg (.mp4 if video)

### Other Options
| Argument | Long Argument | Description | Default |
| -------- | ------------- | --- | ----- |
|`-i PERCENTAGE`|`--image_reducer PERCENTAGE`|Percentage (0 - 100) of pixels that will be converted to text. The higher the value, the higher the final image size.|10|
|`-z SIZE`|`--fontSize SIZE`|Font size for the characters.|10|
|`-s SPACING`|`--spacing SPACING`|Line spacing between each character|1.1|
|`-c "CHARS"`|`--chars "CHARS"`|Characters to use when converting the pixel intensities. From left to right, lower intensity to higher intensity. Must wrap parameter in quotation marks|` .*:+%S0#@`|
|`-wh WIDTH HEIGHT`|`--maxsize WIDTH HEIGHT`|Max width and height of final output in pixels|None|
|`-f FRAME_FREQUENCY`|`--frame_frequency FRAME_FREQUENCY`|VIDEO ONLY. Determines how many frames to skip before capturing/converting. Keep 1 to retain all frames and FPS|24|


  
## Examples

- Converting `lake.jpg` to `newLake.jpg`, converting 10% pixels to text characters
```
python convert.py lake.jpg newLake.jpg -i 10
```

- Converting `lake.jpg` to `coolerLake.jpg`, converting 10% pixels to text characters, with custom character set `.-:lo0@`
```
python convert.py lake.jpg coolerlake.jpg -i 10 -c ".:lo0@"
```
- Converting `meme.png` to `memeText.png`, converting 50% pixels to text characters with spacing of 0.9, max width of 1280, max height of 1000, and font size 20
```
python convert.py meme.png memeText.png -i 50 -s 0.9 -wh 1280 1000 -z 20
```

- Convert `cat.mp4` to `catText.mp4`, converting 15% pixels to text characters, and keeping every other frame (every 2nd frame)
```
python convert.py cat.mp4 catText.mp4 -i 15 -f 2
```

- Convert `costaRica.mp4` to `costaRicaText.mp4`, converting 5% pixels to text characters, with font size 12, spacing 1.2, and keeping every single frame (retaining that glorious 60FPS!)
```
python convert.py costaRica.mp4 costaRicaText.mp4 -i 5 -z -s 1.2 20 -f 1
```
