helm repo add minio-operator https://operator.min.io
helm search repo minio-operator

helm install \
  --namespace minio-operator \
  --create-namespace \
  operator minio-operator/operator

export JWT=$(kubectl get secret/console-sa-secret -n minio-operator -o json | jq -r ".data.token" | base64 -d)

# Install DirectPV
kubectl krew install directpv
kubectl directpv install
kubectl directpv discover
kubectl directpv init drives.yaml

echo "Login using $JWT at https://10.15.123.10:9090" 
