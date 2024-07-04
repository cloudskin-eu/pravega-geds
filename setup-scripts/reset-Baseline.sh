# This will reset the necessary components to perform a new run of the experiment, 
# while installing the baseline version of Pravega.

# Uninstall GEDS-integrated Pravega, Zookeeper, and bookkeeper.
helm uninstall zookeeper bookkeeper
kubectl delete pravegacluster pravega

# Clean the long-term minIO storage
mc rb --force pravega/tier-2-baseline
mc mb pravega/tier-2-baseline
mc rb --force pravega/tier-2-geds
mc mb pravega/tier-2-geds

# delete GEDS metadataserver
kubectl delete pod geds-metadataserver

# Install Zookeeper and Bookkeeper
helm install zookeeper pravega/zookeeper
kubectl patch ZookeeperCluster zookeeper -n default --type merge --patch '{"spec": {"replicas": 1}}'
helm install bookkeeper pravega/bookkeeper 

# Install baseline Pravega
helm install pravega pravega/pravega -f manifests/baseline-values.yaml