# Letterbox Frame Detector

This Python script can be used to detect letterbox frames in a video file, and
extract the frames for further analysis or processing. A letterbox frame is a
video frame with black bars at the top and bottom. Such frames are often used to
preserve the aspect ratio of the original video, but they can also be used as a
visual cue for scene changes or other events.

The script uses OpenCV to read video frames from a file, and applies a simple
algorithm to detect letterbox frames. The frames that are detected as letterbox
frames are saved as JPEG images to a specified directory. The user can select
the video file to process through a file dialog.

The script also supports threading to read the frames from the video file in
parallel, and to process the frames in parallel. This can significantly speed
up the processing of large video files.

GPT Note: Used mostly OpenAI's GPT-4 for this, except for when I ran out of the allotted prompts for the time-block,
after which I went to GPT 3.5.

## Dependencies

- Python 3.x
- OpenCV (tested with version 4.5.2)
- tkinter (for the file dialog)
- tqdm (for progress bars)

## Usage

The script will prompt the user to select a video file to process. The
supported video file formats are: `.mp4`, `.avi`, `.mov`, `.mkv`, `.flv`, and
`.wmv`.

The script will then process the frames of the video file, and save the
detected letterbox frames as JPEG images to a `frames` directory in the same
directory as the script. The file names of the saved frames are in the format
`mmss.jpg`, where `mm` is the number of minutes and `ss` is the number of
seconds in the video where the frame appears.

The script can also be imported as a module, and the `find_letterbox_frames_threaded` function can be called with the
following arguments:

- `file_path`: The path to the video file to process.
- `detect_letterbox_func`: The function to use for detecting letterbox frames.
  Default is `detect_letterbox`.
- `threshold`: The threshold percentage of the video frame height to use for
  the top bar. Default is `2`.
- `black_value`: The black value to use for detecting black rows in the top
  bar. Default is `5`.
- `chunk_size`: The number of frames to read and process in each chunk.
  Default is `100`.
- `num_readers`: The number of threads to use for reading frames. Default is
  `8`.

# GPT Wins

GPT was quick to suggest a right starting point for this challenge, giving me a skeleton python. Comically, the actually
important part of the code needed to be prompted to begin the back-and-forth of building the script. It was also pretty
quick to suggest the general scaffolding in the approach, including breaking up logic into functions.

I was able to quickly add functionality like a file explorer to navigate to the exact file and start to build the
various functionality. Same with the progress bar.

# GPT Pitfalls

Even the latest version of GPT faces considerable issues with more structured programming or mapping
new intents to existing code structure and flow:

- Initially there was no multi-threading, and the processing, while not terribly slow, seemed like it could be improved.
  I asked GPT-4 to add multi-threading, and it added the typical Python threadpool code gleefully. In the spirit of the
  challenge, I didn't look into the code further, but I did notice that the speed didn't increase (in fact it slightly
  decreased) and I knew something was up. It turned out that when adding multi-threading, GPT-4 merely added logic to
  process the same chunks of frames multiple times. When initially asked to add the parallel processing logic, it wasn't
  able to properly "intuit" that doing so properly includes splitting the frames into chunks and processing independent
  chunks in parallel. It was only able to understand that the code should be run multiple times, and that's what it did.
- Attempting to add NVIDIA processing worked initially, but asking it to use the CUDA libraries for more processing in
  the code meant that it ended up hallucinating methods that don't exist. (note: this was taken out eventually)
- Main letterbox detection algorithm took many tries to actually get it to do what was intended.
    - Initially the code generated only considered a few pixels at the top/bottom instead of a continuous bar.
    - Related to above, the initial code also attempted to identify letterboxes by seeing how many pixels were black,
      but this was
      problematic because it would identify a frame as a letterbox if there was a black object in the frame.
    - It took much prompting back and forth to get it to use a reasonable algorithm.
- I asked it to lazy-load the imports, but it suggested adding a lazy-load library instead of just doing it inside a
  function. Maybe I should have been more specific.
- It initially suggested frame-skipping to increase performance, but that shouldn't have been the first suggestion, I
  had to prompt it directly by asking it to use a threadpool. (oh, and it forgot to bring the progress bar with it 🥴)
    - Furthermore, this suggestion pegged RAM usage to max. Had to further prompt it to use a chunked approach to
      processing.
- (had to stop it from giving me the entire file in the output every time with an explicit prompt - maybe I should use a
  skeleton approach in the beginning to set the expected behaviors)
- Asking it to increase performance actually made it slower (it added step for conversion to grayscale prior to
  analyzing)
- Asking it for formatted file name resulted in it giving me a name that creates an incompatible path for Windows (or
  UNIX-based systems probably).