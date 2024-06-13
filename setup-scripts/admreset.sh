sudo kubeadm reset
sudo rm -r /etc/cni/net.d
sudo rm  $HOME/.kube/config
sudo ifconfig cni0 down    
sudo ip link delete cni0
sudo systemctl restart containerd
echo "Kubeadm reset complete."
