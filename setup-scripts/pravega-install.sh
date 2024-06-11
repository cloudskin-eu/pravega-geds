# Add Helm Charts
helm repo add pravega https://charts.pravega.io
helm repo update

# Install Cert-Manager
kubectl apply -f https://github.com/jetstack/cert-manager/releases/latest/download/cert-manager.yaml

# Install Zookeeper
helm install zookeeper-operator pravega/zookeeper-operator
helm install zookeeper pravega/zookeeper

# Install Bookkeeper
kubectl apply -f https://github.com/pravega/bookkeeper-operator/raw/master/config/certmanager/certificate.yaml
helm install bookkeeper-operator pravega/bookkeeper-operator --set webhookCert.certName=selfsigned-cert-bk --set webhookCert.secretName=selfsigned-cert-tls-bk
helm install bookkeeper pravega/bookkeeper --timeout=10m0s 

# Install influxdb
kubectl apply -f manifests/influxdb.yaml
kubectl expose pod influxdb --port=8086 --name=influxdb-service
kubectl create deployment grafana --image=docker.io/grafana/grafana:7.5.17

# Expose minio and wipe the bucket
nohup kubectl port-forward svc/pravega-hl -n pravega 9000:9000 --address 10.15.123.10 &
mc rb pravega/tier-2-baseline --force
mc mb pravega/tier-2-baseline

# Install Pravega
kubectl apply -f https://github.com/pravega/pravega-operator/raw/master/config/certmanager/certificate.yaml
helm install pravega-operator pravega/pravega-operator --set webhookCert.certName=selfsigned-cert --set webhookCert.secretName=selfsigned-cert-tls
helm install pravega pravega/pravega -f manifests/baseline-values.yaml --timeout=10m0s
``

echo "...Installation complete!"
