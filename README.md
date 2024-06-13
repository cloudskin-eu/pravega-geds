# pravega-geds

Integration of Pravega and GEDS for NCT computer-assisted surgery use case

# Repository Structure

This repository is divided into two main sections, `setup-scripts`, and `experiment`. Each section will be addressed individually below. There is also the `media` secion which contains a video and image example of the experiment.

## Instructions

### Prequisites

- 4 VM's with at least [current specs of VM] on the same network. One of these will act as a master node, with the other 3 acting as worker nodes. Each worker should have a 100Gb unmounted drive attached for MinIO.

### 1. Prepare Kubernes Cluster

- Run `adminit.sh` on the master node. Upon completion two things should be printed: A JWT token and a join command. Save these for later.
- Run the join command on each worker node.

### 2. Install MinIO

- On the master node, run `minio-install.sh`. This will install the MinIO operator on the kubernetes cluster.
- On the master node, run `kubectl expose svc/console -n minio-operator --name minio-operator-service --port 9090 --type NodePort`
- on the master node, run `kubectl get svc -n minio-operator`. In the output, you should see the newly created service, as well as the port it is exposed on. Make note of this port.
- The MinIO operator should now be accessible via the master node's IP address at the exposed port in your browser: `http://$MASTER_IP:$NODEPORT`. Enter the JWT you saved previously to login.
- In the MinIO Operator dashboard, click "create tenant" in the top-right corner. There will be multiple sections of options to configure. 
    - In the "Setup" section, configure the following:
        - `Name`: pravega
        - `Namespace`: pravega
        - `Number of servers`: 3
        - `Total Size`: 300
    - In the "Security" section, set `TLS` to off.
    - In the "Identity Provider" Section, set both the `username` and `password` to "minioadmin".
- On the master node, run `kubectl expose svc/console -n pravega --name pravega-console-service --port 9090 --type NodePort`. This will allow us to access the MinIO tenant dashboard.
- In the MinIO tenant dashboard, navigate to the "Access Keys" section. In the top-right corner, click "Create Access Key". Set both the `username` and `password` to "miniostorage", then click "create".
- First, run the command `kubectl port-forward svc/pravega-hl -n pravega 9000:9000 --address $MASTER_IP`. This will allow the minIO client to connect to the tenant. Note that this must be run after each run of the
- Install the MinIO Client by following the [official instructions](https://min.io/docs/minio/linux/reference/minio-mc.html?ref=docs). 
- Run `mc alias set pravega $MASTER_IP:9000 miniostorage miniostorage`.

### 3. Running the Experiment


- To configure the experiment, the following files can be modified:

    1. `latency-benchmark-runner`. Adjust `experiment_time_seconds` to the desired experiment runtime in seconds. the amount of reader and writer pods can be adjusted by changing the values of: \
   `for num_writers_and_streams in [`**3**`]:` \
   &nbsp;&nbsp;&nbsp;&nbsp; `for num_readers_per_stream in [`**3**`]:`

    2. `run-experiment.sh`. Adjust the argument passed to `pause-tenant.sh` to the desired duration of the network interruption.

- Navigate to `/experiments`. Run `./run-experiment.sh` to begin the experiment.
- Once complete, run `kubectl port-forward svc/pravega-hl -n pravega 9000:9000 --address $MASTER_IP` once again. It may take a minute or two for the functionality to resume.
- Navigate back to `/scripts`. Run `./Reset-GEDS.sh` to change to the GEDS-integrated version of Pravega.
- Navigate back to `/experiments` and run `./run-experiment.sh` for the second time.
- Once complete, run `kubectl port-forward svc/pravega-hl -n pravega 9000:9000 --address $MASTER_IP` once more. 
## setup-scripts

This collection of scripts streamlines the installation and setup process of the Kubernetes cluster used during the experiment.

### Files

|          File           |                                                       Description                                                        |
| :---------------------: | :----------------------------------------------------------------------------------------------------------------------: |
|       adminit.sh        |                    Performs the necessary setup steps for the master node in the Kubernetes cluster.                     |
|       admreset.sh       |                        Performs `Kubeadm reset` and necessary cleanup. must be run on each node.                         |
|    minio-install.sh     |                                       Installs MinIO on the Kubernetes cluster.                                        |
| metrics-install.sh | Installs InfluxDB and Grafana.
| pravega-geds-install.sh |                        Installs the GEDS-integrated configuration of pravega and its prequisites.                        |
|   pravega-install.sh    |                           Installs the baseline configuration of pravega and its prequisites.                            |
|  reinstall-pravega.sh   | Reinstalls Pravega, Zookeeper, Bookkeeper, and GEDS, as well as their corresponding operators, and clears MinIO buckets. |
|    reset-Baseline.sh    |                            Reinstalls experiment components for the Baseline Pravega version                             |
|      reset-GEDS.sh      |                         Reinstalls experiment components for the GEDS-Integrated Pravega version                         |
|  uninstall-pravega.sh   |                                   Uninstalls Pravega, Zookeeper, Bookkeeper, and GEDS.                                   |

## experiment

This collection of scripts will run the experiment.

First are a collection of python benchmark scripts. These deploy a defined amount of reader and writer pods into the Kubernetes cluster. Using gstreamer to generate data, the writer pods will append data to the appropriate Pravega streams, also created with these scripts.

Second are a collection of shell scripts. These will run the python benchmark scripts, and and after a defined amount of time will scale the MinIO long-term storage StatefulSet to 0. This will cause the long-term storage to become innaccessible, and we use this fact to measure the buffering capacity, buffering time, and cache latency incurred by the outage. After a defined amount of time, the StatefulSet will be scaled back to 3 nodes, allowing the long-term storage to become accessible.

### Files

|            File             |                                                     Description                                                     |
| :-------------------------: | :-----------------------------------------------------------------------------------------------------------------: |
|  clean_benchmark_scopes.py  |                          Cleans the Pravega scopes after the experiment run has completed.                          |
| latency-experiment-setup.py |                                    Performs setup operations for the experiment.                                    |
| latency-benchmark-runner.py |                                The runner file for the benchmark in the experiment.                                 |
|         get-logs.sh         |            This script will gather the logs of the Pravega segment store, each bookie replica, and GEDS.            |
|       pause-tenant.sh       | This script will scale the MinIO StatefulSet to 0 for a defined amount of time, based on the argument passed to it. |
|      run-experiment.sh      |                                        This script will run the experiment.                                         |

# Example

The following image showcases the experiment. Pravga is configured with an in-memory cache size of 1.5GB,
whereas the local storage configured in GEDS is 5GB. The ingestion throughput generated via
GStreamer video writers write at ≈ 15MBps. Visibly, Pravega alone can handle workload ingestion
for 77 seconds, whereas Pravega with GEDS can last 292 seconds. This represents an improvement of
3.8x in terms of ingestion buffering in front of long-term storage outages. Note that this experiment
uses a small GEDS volume; we could consider much larger GEDS volumes, as local storage may be
a more abundant Edge resource compared to memory.

![Ingestion Buffering Capacity Example](media/Ingestion%20Example.png)

Additionally, an example video can be found at [media/GEDS Pravega Demo](media/GEDS%20Pravega%20Demo%20-%20With%20Numbers.mp4).

