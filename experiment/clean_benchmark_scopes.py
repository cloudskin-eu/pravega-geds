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

PRAVEGA_CLI = "/home/ubuntu/pravega-0.12.0/"

if __name__ == "__main__":
    command = ["bash", PRAVEGA_CLI + "bin/pravega-cli", "scope", "list"]
    output = subprocess.run(command, check=True, capture_output=True, text=True)
    for output_scope in output.stdout.splitlines():
        output_scope = output_scope.strip()
        if output_scope.startswith("benchmark"):
            print(output_scope)
            command = ["bash", PRAVEGA_CLI + "bin/pravega-cli", "stream", "list", output_scope]
            output = subprocess.run(command, check=True, capture_output=True, text=True)
            for output_stream in output.stdout.splitlines():
                output_stream = output_stream.strip()
                if output_stream.startswith(output_scope + "/latency"):
                    print("Deleting stream: " + output_stream)
                    command = ["bash", PRAVEGA_CLI + "bin/pravega-cli", "stream", "delete", output_stream]
                    output = subprocess.run(command, check=True, capture_output=True, text=True)

            print("Deleting scope: " + output_scope)
            command = ["bash", PRAVEGA_CLI + "bin/pravega-cli", "scope", "delete", output_scope]
            output = subprocess.run(command, check=True, capture_output=True, text=True)
