# VirtualHPC
Configuration files to build a small HPC cluster based on virtual machines.

# Day 1: Build a template VM with VirtualBox.
* ISO: /project/biohpcadmin/shared/isos/CentOS-7-x86_64-Minimal-1810.iso
* Network: NAT + host-only
* Proxy
* ssh passwordless login


## Proxy and update
    echo "export http_proxy=http://proxy.swmed.edu:3128" > /etc/profile.d/proxy.sh
    echo "export https_proxy=http://proxy.swmed.edu:3128" >> /etc/profile.d/proxy.sh
    echo "proxy=http://proxy.swmed.edu:3128" >> /etc/yum.conf
    
    yum -y update
    reboot
    
## Disable SELINUX
    vi /etc/sysconfig/selinux # set SELINUX=disabled
    
## Config ssh
    ssh-keygen -t rsa
    cat .ssh/id_rsa.pub > .ssh/authorized_keys  # passwordless
    ssh localhost  # test to see if it requires password

## Add host-only adapter (enables ssh login from host to guest)
This step could be done with the init VB installation. If so, skip this step.

i) VB GUI --> File --> Host Network Manager --> Create a new NIC 'vboxnet0'. ( set the IPv4 Address to 192.168.56.1)  
ii) VM --> Network --> Adapter 2 --> Host-only Adapter --> vboxnet0  
iii) In VM
  
    ip addr show # find the new NIC, in this case, it is enp0s8
    cd /etc/sysconfig/network-scripts
    cp ifcfg-enp0s3 ifcfg-enp0s8
    vi ifcfg-enp0s8
rename enp0s3 to enp0s8, delete the uuid, and add the following lines
 
    BOOTPROTO="static"
    IPADDR=192.168.56.101
    NETMASK=255.255.255.0
iv) reboot the system
v) ssh root@192.168.56.101

