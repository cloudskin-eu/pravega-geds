# This will reset the necessary components to perform a new run of the experiment, 
# while installing the GEDS-integrated version of Pravega.

# Uninstall baseline Pravega, Zookeeper, and bookkeeper.
helm uninstall zookeeper bookkeeper pravega

# Clean the long-term minIO storage
mc rb --force pravega/tier-2-baseline
mc mb pravega/tier-2-baseline
mc rb --force pravega/tier-2-geds
mc mb pravega/tier-2-geds

# Create PV
kubectl apply -f manifests/geds-pv.yaml

# delete GEDS metadataserver
kubectl delete pod geds-metadataserver
kubectl apply -f manifests/metadata-server.yml

# Install Zookeeper and Bookkeeper
helm install zookeeper pravega/zookeeper
helm install bookkeeper pravega/bookkeeper 

# Install GEDS-Integrated Pravega
kubectl create -f manifests/pravegacluster-geds.yaml
