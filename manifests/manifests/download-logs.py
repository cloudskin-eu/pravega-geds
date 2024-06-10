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

import subprocess
import json


def get_all_pod_names(namespace=None):
    command = ["kubectl", "get", "pods", "--output=json"]

    if namespace:
        command.extend(["-n", namespace])

    try:
        # Run the kubectl get pods command and capture the output
        result = subprocess.run(command, capture_output=True, check=True, text=True)

        # Parse the JSON output
        pod_list = json.loads(result.stdout)

        # Extract pod names from the items in the pod list
        pod_names = [item["metadata"]["name"] for item in pod_list.get("items", [])]

        return list(filter(lambda x: x.startswith("latency-reader"), pod_names))
    except subprocess.CalledProcessError as e:
        print(f"Error getting pod names: {e}")
        return []


def download_file_from_pods(pod_names, file_path, destination_path):
    for pod_name in pod_names:
        try:
            # Use kubectl cp command to copy the file from the pod to the local machine
            subprocess.run(["kubectl", "cp", f"{pod_name}:{file_path}", destination_path + pod_name + "-latency.log"], check=True)
            print(f"File downloaded from pod {pod_name}")
        except subprocess.CalledProcessError as e:
            print(f"Error downloading file from pod {pod_name}: {e}")


if __name__ == "__main__":
    # Replace these values with your pod names, file path, and destination path
    pod_names = get_all_pod_names()
    file_path = "/latency-log.log"
    destination_path = "./"

    download_file_from_pods(pod_names, file_path, destination_path)
