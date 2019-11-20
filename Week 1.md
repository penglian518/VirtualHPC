# Week 1: Build a template VM with VirtualBox.
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

1. VB GUI --> File --> Host Network Manager --> Create a new NIC 'vboxnet0'. ( set the IPv4 Address to 192.168.56.1)  
2. VM --> Network --> Adapter 2 --> Host-only Adapter --> vboxnet0  
3. In VM
  
    ip addr show # find the new NIC, in this case, it is enp0s8  
    cd /etc/sysconfig/network-scripts  
    cp ifcfg-enp0s3 ifcfg-enp0s8  
    vi ifcfg-enp0s8  # rename enp0s3 to enp0s8, delete the uuid, and add the following lines
 
        BOOTPROTO="static"
        IPADDR=192.168.56.101
        NETMASK=255.255.255.0
4. reboot the system
5. ssh root@192.168.56.101

## Exercise 1
### Update the kernel
    yum update kernel
Note: This command update the kernel to the version published by RedHat. [Here](https://www.cyberciti.biz/faq/how-to-install-latest-kernel-on-centos-linux-7-using-yum-command/) is the steps to install the latest kernel.
### Apply all security updates only. (Not all the updates)
    yum -y update --security
Ref: [Redhat website](https://access.redhat.com/solutions/10021).
### Add the EPEL (Extra Packages for Enterprise Linux) repositories
    yum -y install https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
Ref: [Fedora wiki](https://fedoraproject.org/wiki/EPEL)
### Add MySQL
    # Add MySQL5.7 repo
    yum -y install https://dev.mysql.com/get/mysql57-community-release-el7-11.noarch.rpm
    # Install MySQL Server
    yum -y install mysql-community-server
    # Remove MySQL
    yum -y remove mysql
### Install MariaDB with yum
    yum -y install mariadb-server
Ref: [MariaDB wike](https://mariadb.com/kb/en/library/yum/)
### Install Singularity3.5 from source code
    mkdir -p tools/src
    cd tools/src
    curl https://codeload.github.com/sylabs/singularity/tar.gz/v3.5.0 > singularity-3.5.0.tar.gz
    tar zxf singularity-3.5.0.tar.gz
    cd singularity-3.5.0
    
    # install system dependencies
    yum groupinstall -y 'Development Tools'
    yum install -y epel-release
    yum install -y golang openssl-devel libuuid-devel libseccomp-devel squashfs-tools cryptsetup
    
Ref: [Singularity3.5 Github](https://github.com/sylabs/singularity/blob/master/INSTALL.md)
TODO: finish the Singularity installation
