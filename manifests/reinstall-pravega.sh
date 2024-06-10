# Uninstall existing Pravega, Bookkeeper and Zookeeper
helm uninstall zookeeper bookkeeper pravega 
helm uninstall zookeeper-operator bookkeeper-operator pravega-operator
mc rb --force pravega/tier-2-baseline
mc mb pravega/tier-2-baseline
./pravega-install.sh
