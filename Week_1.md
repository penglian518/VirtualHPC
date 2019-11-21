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
More details: [Redhat website](https://access.redhat.com/solutions/10021).
### Add the EPEL (Extra Packages for Enterprise Linux) repositories
    yum -y install https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
More details: [Fedora wiki](https://fedoraproject.org/wiki/EPEL)
### Add MySQL
    # Add MySQL5.7 repo
    yum -y install https://dev.mysql.com/get/mysql57-community-release-el7-11.noarch.rpm
    # Install MySQL Server
    yum -y install mysql-community-server
    # Remove MySQL
    yum -y remove mysql
### Install MariaDB with yum
    yum -y install mariadb-server
More details: [MariaDB wiki](https://mariadb.com/kb/en/library/yum/)
### Install Singularity3.5 from source code
    # install system dependencies
    yum groupinstall -y 'Development Tools'
    yum install -y epel-release
    
    # install golang
    yum install -y golang openssl-devel libuuid-devel libseccomp-devel squashfs-tools cryptsetup
    
    # install singularity v3.5.0
    mkdir -p tools/src
    cd tools/src
    git clone https://github.com/sylabs/singularity.git
    cd singularity
    git checkout v3.5.0
    ./mconfig --prefix=/root/tools/singularity
    cd builddir/
    make
    make install
    cd ../../../singularity/bin/
    ./singularity version
More details: [Singularity3.5 Github](https://github.com/sylabs/singularity/blob/master/INSTALL.md)  

## Exercise 2
### create users and groups
    groupadd surgery
    useradd -m -g surgery henry
    useradd -m -g surgery maria
    
    groupadd psychiatry
    useradd -m -g psychiatry luis
    useradd -m -g psychiatry alexandra

    groupadd busadmin
    useradd -m -g busadmin emil
    
    groupadd collaboration
    usermod -a -G collaboration maria
    usermod -a -G collaboration luis

    id lui
    getent group # show all groups and gids
    
## Exercise 3
### create a project directory
    cd /home
    # group members can read
    mkdir surgery_group
    chown -R root.surgery surgery_group
    chmod -R 750  surgery_group
    
    mkdir psychiatry_group
    chown -R root.psychiatry psychiatry_group
    chmod -R 750  psychiatry_group
    
    # group members can write
    chmod -R 770 surgery_group/ psychiatry_group/

    # newly created file belongs to the group
    mkdir collaboration_group
    chown -R root.collaboration collaboration_group
    chmod -R 770  collaboration_group
    chmod -R g+s collaboration_group
    
    # set ACL on the collaboration group
    setfacl -d -Rm u:emil:r collaboration_group/
TODO: fix ACL!
More details: [how to configure ACL](https://www.2daygeek.com/how-to-configure-access-control-lists-acls-setfacl-getfacl-linux/)

## Exercise 4
LVM: Logical Volume Manager, a system of managing logical volumes, or filesystems.
PV: Physical Volumes, the disks ...
VG: Volume Groups, a collect of PVs and LVs
LV: Logical Volumes, not physical disks, can span across multiple disks

LUN: logic units number,  
HBA: Host Bus Adapters, the interface card that connects the host to a fiber channel network or devices

### add a new disk
    # partition the new disk and assign 8e (Linux LVM) as the system id
    fdisk /dev/sdb # n p 1 t 8e w
    # create new pv
    pvcreate /dev/sdb1 
    # show the current VG and find the VG Name ('centos' in this case)
    vgdisplay
    # extend the current VG to include the new pv
    vgextend centos /dev/sdb1 
    # scan and see the new pv and VG
    pvscan
    # show the current LV and get the LV Path ('/dev/centos/root')
    lvdisplay
    # create a new LV with 2G from the VG centos
    lvcreate -n newLV -L +2G centos
    # extend to use all the space of the the new PV
    lvextend -l 100%PVS /dev/centos/newLV

    