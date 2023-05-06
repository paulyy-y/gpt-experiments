import os
import threading
from queue import Queue

import cv2
import numpy as np

import tkinter as tk
from tkinter import filedialog
from tqdm import tqdm


def select_video_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4;*.avi;*.mov;*.mkv;*.flv;*.wmv")])
    return file_path


def format_unix_friendly_timestamp(timestamp):
    minutes, seconds = divmod(int(timestamp), 60)
    return f"{minutes:02d}m{seconds:02d}s"


def process_chunks(detect_letterbox_func, threshold, black_value, frame_queue, frame_rate, queue_semaphore,
                   save_path="frames", min_interval=5):
    if save_path is not None:
        save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), save_path)
        os.makedirs(save_path, exist_ok=True)

    last_saved_timestamp = None
    while True:
        chunk = frame_queue.get()
        if chunk is None:
            break

        for frame_idx, frame in chunk:
            if detect_letterbox_func(frame, threshold, black_value):
                timestamp = frame_idx / frame_rate

                # Check if the time difference since the last saved frame is greater than the minimum interval
                if last_saved_timestamp is None or (timestamp - last_saved_timestamp) >= min_interval:
                    last_saved_timestamp = timestamp
                    formatted_timestamp = format_unix_friendly_timestamp(timestamp)
                    save_frame_path = os.path.join(save_path, f"{formatted_timestamp}.jpg")
                    cv2.imwrite(save_frame_path, frame)

        queue_semaphore.release()  # Release a semaphore slot


def detect_letterbox(frame, threshold_percentage=2, black_value=5, tolerance=10):
    height, width, _ = frame.shape
    threshold = int(height * threshold_percentage / 100)
    top_bar = frame[:threshold, :]

    def is_uniform_row(row, value, tolerance):
        return np.all(np.abs(row - value) <= tolerance)

    def black_row_ratio(bar, black_value, tolerance):
        black_rows = 0
        for i in range(bar.shape[0]):
            if is_uniform_row(bar[i], [black_value, black_value, black_value], tolerance):
                black_rows += 1
        return black_rows / bar.shape[0]

    top_black_row_ratio = black_row_ratio(top_bar, black_value, tolerance)

    return top_black_row_ratio > 0.9


def process_frame(args):
    frame, frame_number = args
    if detect_letterbox(frame):
        return frame_number
    return None


def read_frames(file_path, chunk_size, frame_queue, pbar, start_frame, end_frame, queue_semaphore):
    cap = cv2.VideoCapture(file_path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    chunk = []

    for i in range(start_frame, end_frame):
        ret, frame = cap.read()
        if not ret:
            break

        chunk.append((i, frame))

        if len(chunk) == chunk_size:
            queue_semaphore.acquire()  # Acquire a semaphore slot
            frame_queue.put(chunk)
            pbar.update(len(chunk))
            chunk = []

    if chunk:
        queue_semaphore.acquire()  # Acquire a semaphore slot
        frame_queue.put(chunk)
        pbar.update(len(chunk))

    frame_queue.put(None)  # Signal the end of the frame stream
    cap.release()


def find_letterbox_frames_threaded(file_path, detect_letterbox_func=detect_letterbox, threshold=2, black_value=5,
                                   chunk_size=100, num_readers=8):
    queue_slots = num_readers * 4
    frame_queue = Queue(maxsize=queue_slots)
    queue_semaphore = threading.Semaphore(queue_slots)  # Create a semaphore with the same number of slots as the queue

    cap = cv2.VideoCapture(file_path)
    frame_rate = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()

    with tqdm(total=frame_count, desc="Processing frames") as pbar:
        # Start the frame reading threads
        read_threads = []
        frames_per_reader = frame_count // num_readers
        for i in range(num_readers):
            start_frame = i * frames_per_reader
            end_frame = (i + 1) * frames_per_reader if i < num_readers - 1 else frame_count
            read_thread = threading.Thread(target=read_frames,
                                           args=(file_path, chunk_size, frame_queue, pbar, start_frame, end_frame,
                                                 queue_semaphore))
            read_thread.start()
            read_threads.append(read_thread)

        # Process the chunks in the main thread
        process_chunks(detect_letterbox_func, threshold, black_value, frame_queue, frame_rate, queue_semaphore)

        # Wait for the frame reading threads to finish
        for read_thread in read_threads:
            read_thread.join()


if __name__ == '__main__':
    video_path = select_video_file()
    if video_path:
        find_letterbox_frames_threaded(video_path)
    else:
        print("No video file selected.")
        exit()
