# Add Helm Charts
helm repo add pravega https://charts.pravega.io
helm repo update

# Install Cert-Manager
kubectl apply -f https://github.com/jetstack/cert-manager/releases/latest/download/cert-manager.yaml

# Install Zookeeper
helm install zookeeper-operator pravega/zookeeper-operator
helm install zookeeper pravega/zookeeper
kubectl patch ZookeeperCluster zookeeper -n default --type merge --patch '{"spec": {"replicas": 1}}'

# Install Bookkeeper
kubectl apply -f https://github.com/pravega/bookkeeper-operator/raw/master/config/certmanager/certificate.yaml
helm install bookkeeper-operator pravega/bookkeeper-operator --set webhookCert.certName=selfsigned-cert-bk --set webhookCert.secretName=selfsigned-cert-tls-bk
helm install bookkeeper pravega/bookkeeper --timeout=10m0s 

# Install Pravega
kubectl apply -f https://github.com/pravega/pravega-operator/raw/master/config/certmanager/certificate.yaml
helm install pravega-operator pravega/pravega-operator --set webhookCert.certName=selfsigned-cert --set webhookCert.secretName=selfsigned-cert-tls
helm install pravega pravega/pravega -f manifests/baseline-values.yaml --timeout=10m0s
``
# Create bucket
mc mb pravega/tier-2-baseline
echo "...Installation complete!"