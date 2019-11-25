# Week 3: Storage: Redundancy, Network Storage Protocols & Performance.
* Storage Redundancy
* RAID 6 Configuration
* NFS Server Configuration
* NFS Client Configuration
* SAMBA Server & Client Configuration
* Big Concepts in Network Storage

## Storage redundancy
### What is RAID?
RAID, redundant array of independent disks, employs the techniques of striping, mirroring, or parity to create large 
reliable data stores from common hard disk drives (general-purpose HDDs). Data protection against and recovery from 
hardware defects.

### Concepts
* Mirroing, fully copy all the data from one disk to the other one  
* Striping, split the data between two or more disks
* Metadata, raw data, ones and zeros 

###Common types of RAID
#### RAID 0 (striping)
Strip/split data evenly across two or more disks, without redundancy, parity, or fault tolerance.  

Disks: n >= 2  
Capacity: x n  
I/O Speed: x n  
Redundancy: 0  
Parity: 0  
Fault tolerance: 0   

#### RAID 1 (mirroring)
Exactly copy (mirror) a set of data on two or more disks.  

Disks: n >= 2  
Capacity: 1
I/O Speed: 1 
Redundancy: n  
Parity: 0  
Fault tolerance: n   

#### RAID 10 (mirroring and striping)
A combination of RAID 1 and RAID 0.  

Disks: n >= 4  
Capacity: n/2
I/O Speed: n/2 
Redundancy: 1  
Parity: 0  
Fault tolerance: 1   

#### RAID 5 (striping and distribute parity)
Strip data from a block level and distribute the parity data among all the drives. If one disk is broken, the data can 
be fully recovered by calculating the distributed parity from the other disks. If two or more broken at the same time, 
the array fails.    

Disks: n >= 3  
Capacity: n-1
I/O Speed: 1< speed <n-1  
Redundancy: 1  
Parity: distributed across n disks   
Fault tolerance: 1   

#### RAID 6 (striping and distribute TWO parities)
Strip data from a block level and distribute two parity data among all the drives. If one or two disks are broken at 
the same time, the data can still be fully recovered by calculating the distributed parity from the other disks. 
If three or more broken at the same time, the array fails.    

Disks: n >= 4  
Capacity: n-2
I/O Speed: 1< speed < n-2  
Redundancy: 2  
Parity: distributed across n disks   
Fault tolerance: 2   

### Thoughts
RAID 6 is similar to RAID 5, but it provides an additional distributed parity data among all the disks. Therefore, it 
has a better redundancy and fault tolerance, but slightly worse I/O performance compared to RAID 5. The cost of RAID 6 
 is also higher than that of RAID 5. Overall, in terms data security, it's better than RAID 5.
 
RAID does not provide high availability, especially, when the size of the array getting larger and larger. The 
probability of at least one disk fails increase exponentially to the number of disks in the array. 


## RAID 6 Configuration
    #install the mdadm software   
    yum -y install mdadm
    #list all the disks  
    lsblk
    
    # create the array with disk sdb to sdi
    mdadm --create --verbose /dev/md0 --level=6 --raid-devices=8 /dev/sdb /dev/sdc /dev/sdd /dev/sde /dev/sdf /dev/sdg /dev/sdh /dev/sdi 
    # check the mdstat
    cat /proc/mdstat 
    # save the layout into configuration file
    mdadm --verbose --detail -scan > /etc/mdadm.conf
    
    # create new pv
    pvcreate /dev/md0 
    # show the current VG and find the VG Name ('centos' in this case)
    vgdisplay
    # extend the current VG to include the new pv
    vgextend centos /dev/md0 
    # scan and see the new pv and VG
    pvscan
    # show the current LV and get the LV Path ('/dev/centos/root')
    lvdisplay
    # create a new LV from the VG centos
    lvcreate -n newLV -l 100%FREE centos
    
    # format the new LV to ext4
    mkfs.ext4 /dev/centos/newLV
    # mount the volume
    mount /dev/centos/newLV /new_home
    # add to the fstab.    "/dev/centos/newLV /new_home/ ext4 defaults 0 0"
    vi /etc/fstab
    # check
    df -h

The RAID implemented with Mdadm is software RAID. It uses some CPU resources to compute, read, and write data, so its 
slower than the hardware RAID. Hardware RAID requires RAID card/controller to read/write data. It's faster than soft 
RAID, but the cost is higher. Also, once the RAID card is broken, have to find the same type of RAID card to recover
the data.

## NFS server configuration 
    # install the packages
    yum -y install nfs-utils
    # write the configuration file for NFS
    vi /etc/exports # add the following line "/new_home	192.168.56.*(rw,sync,root_squash)"
    chmod 777 /new_home
    # restart the services
    systemctl restart rpcbind  # RPC, Remote Procedure Call, required by NFS
    systemctl enable rpcbind
    systemctl start nfs-server
    systemctl enable nfs-server
    # check the nfs server
    systemctl status nfs
    # check the export list
    showmount -e localhost
    
    # firewall
    systemctl stop firewalld
    systemctl disable firewalld
    
    # or 
    firewall-cmd --add-service=nfs --zone=internal --permanent
    firewall-cmd --add-service=mountd --zone=internal --permanent
    firewall-cmd --add-service=rpc-bind --zone=internal --permanent


options for the host in /etc/exports
* ro(default): read-only
* rw: read and write
* sync(default): NFS not reply the requests until the changes made by the previous requests are written completely.
* async: <--> sync
* wdelay(default):  delay writing to the disk if the server suspects another request is imminent.
* no_wdelay: no delay writing. Only available if sync is also specified.
* root_squash(default): treat the remote root user as local user (user ID nfsnobody). 
* no_root_squash: <--> root_squash
* all_squash: squash all the remote users
* anonuid,anongid: assign uid or gid to the remote users. e.g. anonuid=500,anongid=1000
* no_acl: disable ACL when exporting the file system

Use 'exportfs' command to refresh the NFS settings without restarting the NFS server.
* -r export all directories in /etc/exports
* -a all directories exported/unexported, depends on other options
* -i ignores /etc/exports
* -u unexports all. -ua suspends file sharing while keeping all daemons up. use -r to re-enable sharing
* -v verbose
* -o file-systems add new directories to be exported that are not in /etc/exports


More details: [Redhat Doc](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/7/html/storage_administration_guide/nfs-serverconfig), 
[Geek Diary](https://www.thegeekdiary.com/centos-rhel-7-configuring-an-nfs-server-and-nfs-client/)

## NFS client configuration 
    # install the packages
    yum -y install nfs-utils
    # create a mount point
    mkdir /shared_home
    
    # define nfs host
    vi /etc/hosts  
        192.168.56.103 nfsserver
    
    # mount
    mount -t nfs nfsserver:/new_home /shared_home
    # umount
    umount /shared_home
    
    # write the fstable, so that it will mount during every reboot
    vi /etc/fstable   
        nfsserver:/new_home	/shared_home	nfs	defaults	0 0
    # mount all listed in fstable
    mount -a
    
    # test with other users
    sudo - emil
    mkdir /shared_home/a
    ll /shared_home/

### Autofs configuration for NFS
    # install packages
    yum -y install autofs
    
    # change the default timeout options (default is 600s)
    # this step can be skipped, one can add the options to the /etc/auto.master as well
    vi /etc/sysconfig/autofs 
        OPTIONS="--timeout=60"
    systemctl restart autofs
    systemctl status autofs
    
    # config /etc/auto.master, add the following line
    vi /etc/auto.master  
        # /- ----> (direct map), use absolutaly path
        # /etc/auto.nfs ---->  configuration file
        /-	/etc/auto.nfs --timeout=60 

    # config /etc/auto.nfs
    vi /etc/auto.nfs        
        # /shared_home ----> mount point
        # -rw,soft,intr ----> options
        # nfsserver:/new_home ----> remote server
        /shared_home	-rw,soft,intr	nfsserver:/new_home	

    # restart autofs
    systemctl restart autofs
    # check to see if it works
    ll /shared_home
    df -h
    less /var/log/messages


## SAMBA server configuration
    # install the packages
    yum -y install samba samba-client
    # start and enable the smb service
    systemctl start smb     # smb listens on TCP ports 139, 445
    systemctl start nmb     # nmb, NetBIOS over IP, UDP 137
    systemctl enable smb
    systemctl enable nmb
    
    # config the firewall or disable it
    firewall-cmd --permanent --zone=public --add-service=samba
    firewall-cmd --zone=public --add-service=samba
    
    # add user to SAMBA database and set password
    smbpasswd -a emil
    # check the status of the user
    smbpasswd -e emil
    # config the smb service by adding the following block
    vi /etc/samba/smb.conf
        [new_home]
            path = /new_home                # folder to share
            browseable = yes                # 
            read only = no                  #
            writable = yes                  #
            guest ok = no                   #
            force create mode = 0660        #
            force directory mode = 2770     #
            valid users = emil @collaboration   # users, or groups (user "@" as prefix) 
    # restart the services
    systemctl restart smb
    systemctl restart nmb

## SAMBA client configuration
    # install the packages
    yum -y install samba-client cifs-utils
    # create a directory to mount
    mkdir /shared_home_smb
    # mount 
    mount -t cifs -o username=emil,password=emil123456 //nfsserver/new_home /shared_home_smb
    ll /shared_home_smb/
    touch /shared_home_smb/c
    
    # write the fstable, so that it will mount during every reboot
    vi /etc/fstable   
        //nfsserver/new_home /shared_home_smb cifs username=emil,password=emil123456,soft,rw 0 0
    mount -a
    
## Big Concepts
###NAS, network attached storage
Share data within small network, "storage + a router", one failure will affect the 
whole network. 
###SAN, storage area network
A high speed network that stores and provides access to large amounts of data. "disk arrays + switch + servers", 
Fault tolerant, scalable. 
###NFS
A file system that allows users to access files across a network and treat them as if they resided in a local file 
directory. "Client ---- network (NFS protocol) ---- Server"
###Parallel file system
* Data is striped and distributed to multiple storage devices, with redundant.  
* A shared global namespace to facilitate data access
* Accessible from many clients
* Operated over high-speed networks
* Optimized I/O path for maximum bandwidth
* Separated Metadata server and object storage servers (in Lustre).
* Highly scalable 
