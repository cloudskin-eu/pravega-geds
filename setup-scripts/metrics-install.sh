# Install InfluxDB
kubectl apply -f manifests/influxdb.yaml
kubectl expose pod influxdb --port=8086 --name=influxdb-service

# Install Grafana
kubectl create deployment grafana --image=docker.io/grafana/grafana:7.5.17