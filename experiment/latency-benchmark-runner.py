#!/usr/bin/env python3

#
# Copyright (c) Dell Inc., or its subsidiaries. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#

import os
import time
import subprocess
import shutil


def move_files_starting_with_to_folder(file_prefix, source_folder, destination_folder):
    # Iterate through files in the source folder
    for filename in os.listdir(source_folder):
        # Check if the file has the specified prefix
        if filename.startswith(file_prefix):
            source_path = os.path.join(source_folder, filename)
            destination_path = os.path.join(destination_folder, filename)

            # Move the file to the destination folder
            shutil.move(source_path, destination_path)
            print(f"Moved {filename} to {destination_folder}")


if __name__ == "__main__":
    # Assume that all the python scripts are in the current working directory
    directory_path = os.getcwd() + "/"
    pravega_controller_uri = "pravega-pravega-controller:9090"
    experiment_time_seconds = 600

    for num_writers_and_streams in [8]:
        for num_readers_per_stream in [8]:
            for pravega_buffer_size in [1024]:
                for video_height, video_width in [(1920, 1080)]:
                    for video_fps in [30]:
                        for video_bitrate_kbps in [20000]:
                            for reader_sleep_seconds in [5.0]:
                                try:
                                    # Get number of initial directories to find out the name for the benchmark dir.
                                    experiment_path = directory_path + "test-nw-" + str(num_writers_and_streams) + \
                                        "-nr-" + str(num_readers_per_stream) + "-buffer-" + str(pravega_buffer_size) + \
                                        "-height-" + str(video_height) + "-width-" + str(video_width) + "-fps-" + str(video_fps) + \
                                        "-br-" + str(video_bitrate_kbps) + "-sleep-" + str(int(reader_sleep_seconds))
                                    command = ["python3", directory_path + "latency-experiment-setup.py",
                                               "--num-writers-and-streams=" + str(num_writers_and_streams),
                                               "--num-readers-per-stream=" + str(num_readers_per_stream),
                                               "--pravega-controller-uri=" + pravega_controller_uri,
                                               "--pravega-buffer-size=" + str(pravega_buffer_size),
                                               "--video-height=" + str(video_height), "--video-width=" + str(video_width),
                                               "--video-fps=" + str(video_fps), "--video-bitrate=" + str(video_bitrate_kbps),
                                               "--reader-sleep-seconds=" + str(reader_sleep_seconds),
                                               "--output-dir=" + experiment_path]
                                    # Create the benchmark YAML files to deploy kubernetes pods.
                                    subprocess.run(command, check=True)
                                    print(f"Successfully invoked the script: {command}")
                                    # Now, create the pods and run the experiments
                                    command = ["kubectl", "create", "-f", experiment_path]
                                    result = subprocess.run(command, capture_output=True, check=True, text=True)
                                    # Wait for the benchmark to run for the required time.
                                    print("Deploying and executing benchmark...")
                                    time.sleep(experiment_time_seconds)
                                    # Collect the logs.
                                    print("Collecting latency logs...")
                                    command = ["python3", directory_path + "download-logs.py"]
                                    subprocess.run(command, check=True)
                                    # Move latency log files to the related benchmark folder.
                                    move_files_starting_with_to_folder("latency-reader", directory_path,
                                                                       experiment_path)
                                    # Shut down experiment
                                    print("Shutting down benchmark...")
                                    command = ["kubectl", "delete", "-f", experiment_path]
                                    result = subprocess.run(command, capture_output=True, check=True, text=True)

                                except subprocess.CalledProcessError as e:
                                    print(f"Error invoking the script: {e}")
