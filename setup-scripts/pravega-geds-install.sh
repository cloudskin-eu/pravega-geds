# Add Helm Charts
helm repo add pravega https://charts.pravega.io
helm repo update

# Install Cert-Manager
kubectl apply -f https://github.com/jetstack/cert-manager/releases/latest/download/cert-manager.yaml

# Install GEDS
kubectl apply -f manifests/metadata-server.yml
kubectl apply -f manifests/geds-pv.yaml

# Install Zookeeper
helm install zookeeper-operator pravega/zookeeper-operator
helm install zookeeper pravega/zookeeper

# Install Bookkeeper
kubectl apply -f https://github.com/pravega/bookkeeper-operator/raw/master/config/certmanager/certificate.yaml
helm install bookkeeper-operator pravega/bookkeeper-operator --set webhookCert.certName=selfsigned-cert-bk --set webhookCert.secretName=selfsigned-cert-tls-bk
helm install bookkeeper pravega/bookkeeper  --timeout=10m0s

# Install Pravega
kubectl apply -f https://github.com/pravega/pravega-operator/raw/master/config/certmanager/certificate.yaml
helm install pravega-operator pravega/pravega-operator --set webhookCert.certName=selfsigned-cert --set webhookCert.secretName=selfsigned-cert-tls
kubectl create -f manifests/pravegacluster-geds.yaml

echo "...Installation complete!"



