
mkdir logs
export logs_dir="logs/logs-$(date +%Y-%m-%d_%H-%M)"
mkdir $logs_dir


kubectl logs pravega-pravega-segmentstore-0 --since-time=$1 > $logs_dir/segmentstore.log
kubectl logs pravega-pravega-segmentstore-0 --since=1h > $logs_dir/segmentstore-1h.log
kubectl logs pravega-pravega-segment-store-0 --since-time=$1 > $logs_dir/segmentstore.log
kubectl logs pravega-pravega-segment-store-0 --since=1h > $logs_dir/segmentstore-1h.log
# kubectl logs bookkeeper-bookie-0 --since-time=$1 > $logs_dir/bookie0.log 
# kubectl logs bookkeeper-bookie-1 --since-time=$1 > $logs_dir/bookie1.log 
# kubectl logs bookkeeper-bookie-2 --since-time=$1 > $logs_dir/bookie2.log 

touch $logs_dir/experiment_runner.log

echo "{\"Start Time\": \"$2 $3\", \"End Time\": \"$4 $5\", \"Pause Time\": \"$6 $7\", \"Resume Time\": \"$8 $9\"}" > $logs_dir/timestamps.json

