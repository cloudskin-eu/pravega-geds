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

'''
Script to create all the Kubernetes deployment files that will represent individual GStreamer processes
writing and reading from Pravega to measure latency in various ways.
'''
import argparse
import random
import os

entrypoint_writer = "/usr/src/gstreamer-pravega/python_apps/pravega_latency_writer.py " + \
                    "--pravega-controller-uri %s --scope %s --stream %s --pravega-buffer-size %s " + \
                    "--video-height %s --video-width %s --video-fps %s --video-bitrate %s --sleep-seconds %s"

entrypoint_reader = "/usr/src/gstreamer-pravega/python_apps/pravega_latency_reader.py " + \
                    "--pravega-controller-uri %s --scope %s --stream %s --sleep-seconds %s"

PODNAME = "PODNAME"
NODENAME = "NODENAME"
NODES = 3

pod_yaml = "apiVersion: v1\n" + \
           "kind: Pod\n" + \
           "metadata:\n" + \
           "    name: " + PODNAME + "\n" + \
           "spec:\n" + \
           "  affinity:\n" + \
           "  containers:\n" + \
           "    - name: " + PODNAME + "\n" + \
           "      image: ojundi03/gstreamer:pravega-prod\n" + \
           "      imagePullPolicy: Always\n" + \
           "      env:\n" + \
           "        - name: ENTRYPOINT\n" + \
           "          value: "

root_permission = "      securityContext:\n" + \
                  "        allowPrivilegeEscalation: false\n" + \
                  "        runAsUser: 0\n"

docker_run_file = "docker run --rm --network host --privileged --user root --log-driver json-file --log-opt max-size=10m " + \
                  "--log-opt max-file=2 -e ENTRYPOINT="

docker_image = " ojundi03/gstreamer:pravega-prod"

def main():
    '''
    Usage: python latency-experiment-setup.py --num-writers-and-streams 1
    '''
    parser = argparse.ArgumentParser(description='Pravega latency measurement writer.')
    parser.add_argument('--num-writers-and-streams', type=int, default=1, help='Number of Pravega GStreamer writers writing to individual streams')
    parser.add_argument('--num-readers-per-stream', type=int, default=1, help='Number of Pravega GStreamer readers per stream')
    parser.add_argument('--pravega-controller-uri', default='127.0.0.1:9090')
    parser.add_argument('--scope', default='', help='Scope for the stream. By default, scopes are randomly generated on a per-experiment basis')
    parser.add_argument('--stream', default='latency')
    parser.add_argument("--pravega-buffer-size", type=int, default=1024, help='Pravega writer buffer size in bytes')
    parser.add_argument("--video-height", type=int, default=600)
    parser.add_argument("--video-width", type=int, default=800)
    parser.add_argument("--video-fps", type=int, default=30)
    parser.add_argument("--video-bitrate", type=int, default=5000)
    parser.add_argument("--writer-sleep-seconds", type=float, default=0.0, help="Delay writer start by this many seconds")
    parser.add_argument("--reader-sleep-seconds", type=float, default=0.0, help="Delay reader start by this many seconds")
    parser.add_argument("--deployment-type", default='k8s', help='Whether experiments are going to be executed on k8s or a local VM.')
    parser.add_argument('--output-dir', default='')
    args = parser.parse_args()

    writers = 0
    while writers < args.num_writers_and_streams:
        # Configure the execution options for the writer/reader in this experiment
        experiment_id = str(random.randint(0, 10000))
        scope = "benchmark" + experiment_id
        output_dir = "./" + scope
        if args.scope != '':
            scope = args.scope
        if args.output_dir != '':
            output_dir = args.output_dir
        if not os.path.isdir(output_dir):
            os.mkdir(output_dir)
        configured_writer_entrypoint = entrypoint_writer % (args.pravega_controller_uri, scope, args.stream,
                                                            args.pravega_buffer_size, args.video_height, args.video_width,
                                                            args.video_fps, args.video_bitrate, args.writer_sleep_seconds)
        writer_name = "latency-writer-" + experiment_id + "-" + str(writers)
        writer_yaml_file = open(output_dir + "/" + writer_name + ".yaml", 'a')
        worker_node = "neardata-2204-work0" + str(writers % NODES + 1)
        writer_yaml_file.write(pod_yaml.replace(PODNAME, writer_name).replace(NODENAME, worker_node) + "\"" + configured_writer_entrypoint + "\"\n")
        writer_yaml_file.close()
        readers = 0
        while readers < args.num_readers_per_stream:
            configured_reader_entrypoint = entrypoint_reader % (args.pravega_controller_uri, scope, args.stream,
                                                                args.reader_sleep_seconds)
            reader_name = "latency-reader-" + experiment_id + "-" + str(readers)
            reader_yaml_file = open(output_dir + "/" + reader_name + ".yaml", 'a')
            reader_yaml_file.write(pod_yaml.replace(PODNAME, reader_name).replace(NODENAME, worker_node) + "\"" + configured_reader_entrypoint + "\"\n" + root_permission)
            reader_yaml_file.close()
            readers += 1

        writers += 1


if __name__ == "__main__":
    main()
