# Uninstall existing Pravega, Bookkeeper and Zookeeper, as well as their operators
helm uninstall zookeeper bookkeeper pravega
helm uninstall zookeeper-operator bookkeeper-operator pravega-operator
kubectl delete pod geds-metadataserver
kubectl delete svc geds-metadataserver
kubectl delete pravegacluster pravega
kubectl delete pv geds-cache

mc rb pravega/tier-2-baseline --force
mc rb pravega/tier-2-geds --force