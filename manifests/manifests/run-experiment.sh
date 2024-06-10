nohup python3 latency-benchmark-runner.py &
echo "Gstreamer started at: $(date +%T)"
export start_time=$(date +%Y-%m-%d" "%H:%M:%S)
export logs_time=$(date -d "1 hour ago" +%Y-%m-%dT%H:%M:%SZ)
# Wait a defined amount of time before forcing a network disruption.
sleep 60
export pause_time=$(date +%Y-%m-%d" "%H:%M:%S)

# Force a network nterruption to take place for a defined amount of time. 
./pause-tenant.sh 540
nohup kubectl port-forward svc/pravega-hl -n pravega 9000:9000 --address 10.15.123.10 &
export resume_time=$(date +%Y-%m-%d" "%H:%M:%S)
python3 clean_benchmark_scopes.py

# Wait a defined amount of time before finishing the experiment
sleep 60
rm -r test-nw-*
export end_time="$(date +%Y-%m-%d" "%H:%M:%S)"


./get-logs.sh $logs_time $start_time $end_time $pause_time $resume_time
echo "Run Complete."