# Week 7: OpenHPC and Slurm
* Basic terms
* Setup OpenHPC server
* Deploy Slurm
* Combine with LDAP server
* Mount NFS filesystem

## Basic terms
* SMS, system management server, master node of OpenHPC
* BMC, baseboard management controllers, compute node
* BOS, base operating system

## Setup OpenHPC server (on NFS server)
Disable SELinux and Firewall
    
    # check the status of SELinux
    sestatus
    # Temporarily disable SELinux
    setenforce 0
    # Permanently disable SELinux
    vi /etc/selinux/config
    # set SELINUX=disabled
    # reboot system
    reboot
    
Disable firewall

    systemclt stop firewalld
    systemclt disable firewalld
    systemclt status firewalld

Install OpenHPC packages

    # Install OpenHPC repository 
    yum -y install http://build.openhpc.community/OpenHPC:/1.3/CentOS_7/x86_64/ohpc-release-1.3-1.el7.x86_64.rpm
    
    # Install the packages
    yum -y install ohpc-base
    yum -y install ohpc-warewulf

Configure NTP server [Ref](https://www.thegeekstuff.com/2014/06/linux-ntp-server-client/)

    # install the package
    yum -y ntp
    # make the following lines are in the ntp configure file
    vi /etc/ntp.conf
    
        restrict default nomodify notrap nopeer noquery
        restrict 127.0.0.1
        restrict 192.168.56.0 mask 255.255.255.0 nomodify notrap
    
        # set local clock as backup server in case the internet is disconnected
        server  127.127.1.0 # local clock
        fudge   127.127.1.0 stratum 10
    
        logfile /var/log/ntp.log
        driftfile /var/lib/ntp/drift

    # start the NTP server
    systemctl start ntpd
    systemctl enable ntpd
    
    # verify time sync
    ntpq -p
    
Install slurm server 

    yum -y install ohpc-slurm-server
    
    # set the nfsserver as the slurm-server 
    perl -pi -e "s/ControlMachine=\S+/ControlMachine=nfsserver/" /etc/slurm/slurm.conf
    
Complete basic Warewulf setup for mater node

    # config Warewulf provisioning to use the right internal interface
    perl -pi -e "s/device = eth1/device = enp0s8/" /etc/warewulf/provision.conf
    # enable tftp
    perl -pi -e "s/^\s+disable\s+= yes/ disable = no/" /etc/xinetd.d/tftp
    # enable internal interface for provisioning
    ifconfig enp0s8 192.168.56.103 netmask 255.255.255.0 up
    
    # start/enable relevant services
    systemctl restart xinetd
    systemctl restart mariadb
    systemctl restart httpd
    systemctl enable mariadb
    systemctl enable httpd

Setup DHCP server

    cp /usr/share/doc/dhcp-4.2.5/dhcpd.conf.example /etc/dhcp/dhcpd.conf 
    
    vi /etc/dhcp/dhcpd.conf
    # make sure the following lines are in the configuration file

        option domain-name "biohpc.swmed.edu";
        option domain-name-servers nfsserver;
        
        subnet 192.168.56.0 netmask 255.255.255.0 {
                option routers                  192.168.56.103;
                option subnet-mask              255.255.255.0;
                option domain-search              "biohpc.swmed.edu";
                option domain-name-servers       192.168.56.103;
                #option time-offset              -18000;     # Eastern Standard Time
                range 192.168.56.100 192.168.56.254;
        }
        
        
        host c1 {
           option host-name "c1";
           hardware ethernet 08:00:27:48:B8:B5;
           fixed-address 192.168.56.110;
        }
        
        host c2 {
           option host-name "c2";
           hardware ethernet 08:00:27:C1:AE:34;
           fixed-address 192.168.56.111;
        }

    systemctl restart dhcpd
    systemctl enable dhcpd

## Make compute image for provisioning
Set the default location

    export CHROOT=/opt/ohpc/admin/images/centos7.7

Build initial image

    wwmkchroot centos-7 $CHROOT

Install base meta-package

    yum -y --installroot=$CHROOT install ohpc-base-compute

Configure DNS resolution and /etc/hosts

    cp -p /etc/resolv.conf $CHROOT/etc/resolv.conf
    cp -p /etc/hosts $CHROOT/etc/hosts

Add Slurm client, NTP support, kernel drivers, and include modules user environment

    yum -y --installroot=$CHROOT install ohpc-slurm-client ntp kernel lmod-ohpc
    
Initialize warewulf database and ssh_keys

    wwinit database
    wwinit ssh_keys

Configure NFS client to mount /home and /opt/ohpc/pub

    echo "nfsserver:/home /home nfs nfsvers=3,nodev,nosuid,noatime 0 0" >> $CHROOT/etc/fstab
    echo "nfsserver:/opt/ohpc/pub /opt/ohpc/pub nfs nfsvers=3,nodev,noatime 0 0" >> $CHROOT/etc/fstab
    echo "nfsserver:/new_home /shared_home nfs defaults 0 0" >> $CHROOT/etc/fstab
    chroot $CHROOT/ mkdir shared_home
    
Configure NFS server

    echo "/home 192.168.56.0/24(rw,no_subtree_check,fsid=10,no_root_squash)" >> /etc/exports
    echo "/opt/ohpc/pub 192.168.56.0/24(ro,no_subtree_check,fsid=11)" >> /etc/exports
    exportfs -a
    showmount -e
    systemctl restart nfs

Configure NTP client

    chroot $CHROOT systemctl enable ntpd
    echo "server nfsserver" >> $CHROOT/etc/ntp.conf

Import files from provisioning server

    wwsh file import /etc/passwd
    wwsh file import /etc/group
    wwsh file import /etc/shadow
    
    wwsh file import /etc/slurm/slurm.conf
    wwsh file import /etc/munge/munge.key
    

Configure LDAP client

    # install packages
    yum -y --installroot=$CHROOT install openldap-clients pam_ldap nss-pam-ldapd authconfig
    # copy certificated file from server to client
    chroot $CHROOT/ mkdir /etc/openldap/cacerts/
    scp ldapserver:/etc/openldap/certs/ca.cert.pem $CHROOT/etc/openldap/cacerts/
    # disable SELINUX
    cp -p /etc/selinux/config $CHROOT/etc/selinux/config
    # configure LDAP client
    chroot $CHROOT/ authconfig --enableldap --enableldapauth --enablemkhomedir --ldapserver=ldapserver --ldapbasedn="dc=biohpc,dc=swmed,dc=edu" --enableldaptls --update
    
Assemble bootstrap image

    # include updated kernel drivers, overlayfs drivers for Singularity
    export WW_CONF=/etc/warewulf/bootstrap.conf
    echo "drivers += updates/kernel/" >> $WW_CONF
    echo "drivers += overlay" >> $WW_CONF
    
    # build bootstrap image
    wwbootstrap `uname -r`
    
    # assemble virtual node file system image
    wwvnfs --chroot $CHROOT
    
Register nodes for provisioning

    # set provisioning interface as the default networking device
    echo "GATEWAYDEV=enp0s8" > /tmp/network.$$
    wwsh -y file import /tmp/network.$$ --name network
    wwsh -y file set network --path /etc/sysconfig/network --mode=0644 --uid=0
    
    # add nodes to warewulf data store
    wwsh -y node new c1 --ipaddr=192.168.56.110 --hwaddr=08:00:27:48:B8:B5 -D enp0s8
    wwsh -y node new c2 --ipaddr=192.168.56.111 --hwaddr=08:00:27:C1:AE:34 -D enp0s8
    
    # Additional step required if desiring to use predictable network interface
    # naming schemes (e.g. en4s0f0). Skip if using eth# style names.
    wwsh provision set "c?" --kargs "net.ifnames=1,biosdevname=1"
    wwsh provision set --postnetdown=1 "c?"
    
    # define provisioning image for hosts
    wwsh -y provision set "c?" --vnfs=centos7.7 --bootstrap=`uname -r` --files=dynamic_hosts,passwd,group,shadow,slurm.conf,munge.key,network
    
    # wwsh made a lot of changes to dhcpd.conf, so restart DHCPD
    systemctl restart dhcpd
    wwsh pxe update
    