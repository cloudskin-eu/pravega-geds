# This will reset the necessary components to perform a new run of the experiment, 
# while installing the GEDS-integrated version of Pravega.

helm uninstall zookeeper bookkeeper pravega
kubectl delete pravegacluster pravega

kubectl delete pv geds-cache
kubectl apply -f manifests/geds-pv.yaml

mc rb --force pravega/tier-2-baseline
mc mb pravega/tier-2-baseline
mc rb --force pravega/tier-2-geds
mc mb pravega/tier-2-geds

kubectl delete pod geds-metadataserver
kubectl apply -f manifests/metadata-server.yml

helm install zookeeper pravega/zookeeper
helm install bookkeeper pravega/bookkeeper 


kubectl create -f manifests/pravegacluster-geds.yaml
