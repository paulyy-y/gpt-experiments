# Letterbox Frame Detector

This Python script can be used to detect letterbox frames in a video file, and extract the frames for further analysis or processing. A letterbox frame is a video frame with black bars at the top and bottom. Such frames are often used to preserve the aspect ratio of the original video, but they can also be used as a visual cue for scene changes or other events.

The script uses OpenCV to read video frames from a file, and applies a simple algorithm to detect letterbox frames. The frames that are detected as letterbox frames are saved as JPEG images to a specified directory. The user can select the video file to process through a file dialog.

The script also supports threading to read the frames from the video file in parallel, and to process the frames in parallel. This can significantly speed up the processing of large video files.

## Dependencies

- Python 3.x
- OpenCV (tested with version 4.5.2)
- tkinter (for the file dialog)
- tqdm (for progress bars)

## Usage

The script will prompt the user to select a video file to process. The supported video file formats are: `.mp4`, `.avi`, `.mov`, `.mkv`, `.flv`, and `.wmv`.

The script will then process the frames of the video file, and save the detected letterbox frames as JPEG images to a `frames` directory in the same directory as the script. The file names of the saved frames are in the format `mmss.jpg`, where `mm` is the number of minutes and `ss` is the number of seconds in the video where the frame appears.

The script can also be imported as a module, and the `find_letterbox_frames_threaded` function can be called with the following arguments:

- `file_path`: The path to the video file to process.
- `detect_letterbox_func`: The function to use for detecting letterbox frames. Default is `detect_letterbox`.
- `threshold`: The threshold percentage of the video frame height to use for the top bar. Default is `2`.
- `black_value`: The black value to use for detecting black rows in the top bar. Default is `5`.
- `chunk_size`: The number of frames to read and process in each chunk. Default is `100`.
- `num_readers`: The number of threads to use for reading frames. Default is `8`.
