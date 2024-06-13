# Export the logged information about the run to a .json file. 
mkdir logs
export logs_dir="logs/logs-$(date +%Y-%m-%d_%H-%M)"
mkdir $logs_dir

echo "{\"Start Time\": \"$2 $3\", \"End Time\": \"$4 $5\", \"Pause Time\": \"$6 $7\", \"Resume Time\": \"$8 $9\"}" > $logs_dir/timestamps.json

