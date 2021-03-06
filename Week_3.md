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
* Metadata, raw data, ones and zeros? In Lustre it means file names, paths (namespace), indexes etc. 

### Common types of RAID
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
    vi /etc/exports # add the following line "/new_home	192.168.56.0/24(rw,sync,root_squash)" # wildcard doesnot work with IP addresses!
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
    exportfs -v

    
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
    
    # write the fstab, so that it will mount during every reboot
    vi /etc/fstab   
        nfsserver:/new_home	/shared_home	nfs	defaults	0 0
    # mount all listed in fstab
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
        # soft ----> report an error but don't wait for the NFS server if it is unavailable.
        # intr ----> allow NFS requests to be interrupted if the server goes down or not reachable.
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
    
    # write the fstab, so that it will mount during every reboot
    vi /etc/fstab   
        //nfsserver/new_home /shared_home_smb cifs username=emil,password=emil123456,soft,rw 0 0
    mount -a
    
## Big Concepts
### NAS, network attached storage  
Share data within small network, "storage + a router", one failure will affect the 
whole network.   
### SAN, storage area network  
A high speed network that stores and provides access to large amounts of data. "disk arrays + switch + servers", 
Fault tolerant, scalable.   
### NFS  
A file system that allows users to access files across a network and treat them as if they resided in a local file 
directory. "Client ---- network (NFS protocol) ---- Server"  
### Parallel file system   
* Data is striped and distributed to multiple storage devices, with redundant.  
* A shared global namespace to facilitate data access
* Accessible from many clients
* Operated over high-speed networks
* Optimized I/O path for maximum bandwidth
* Separated Metadata server and object storage servers (in Lustre).
* Highly scalable 
#### Lustre
Good scalability tens of thousands of clients, tens of PB of storage, peak speed 2 TB/s tested in ORNL clusters.
* One or more metadata server (MDS) with one or more metadata target (MDT) devices. Stores namespcace metadata, such as 
filenames, directories, access permissions, and file layout. MDS of Lustre doesn't involve file I/O.
* One or more object storage server (OSS) stores one or more object storage target (OST) devices. 
* Clients. Accessible to universal namespaces of all files, almost no limits (>25 000 clients tested)

#### GPFS (IBM General Parallel File System, renamed to IBM Spectrum Scale in 2015)
* Distributed metadata, including the directory tree. There is no directory controller or index server.
* No limit on the number of files in a single directory
* Distributed locking. e.g. locking for exclusive file access
* Partition Aware. A failure of the network may only affect a portion of the system, the rest of the file system still 
alive. (Heartbeat protocol)
* Online filesystem maintenance. 

#### BeeGFS
Focus on Scalability, flexibility, and good usability
* Metadata Server. Metadata distributed over several servers on a directory level, with each server storing a part of
the complete file system tree.
* Storage Server. Save striped files
* Clients



## Linux Kernel Storage Stack
### VFS, virtual file system, or virtual filesystem switch
VFS is an abstract layer on top of a more concrete file system. The purpose of VFS is to allow client applications to 
access different types of concrete file systems in a uniform way. A VFS specifies an interface between the kernel and 
a concrete file system, so that it is easy to add support for new file system types.

### XFS
XFS was originally developed in the early 1990s by SGI. It is a 64-bit journaling file system that supports very 
large files and file systems on a single host. For example, Red Hat’s maximum supported XFS file system image is 100TB 
for RHEL 5, 300TB for RHEL 6, and 500TB for RHEL 7. 
However, XFS has a relatively poor performance for single threaded, metadata-intensive workloads, for example, 
a workload that creates or deletes large numbers of small files in a single thread.

### Ext4
Ext4 is the fourth generation of the Ext file system family. 
A more compact and efficient way to track utilized space in a file system is the usage of extent-based metadata and
 the delayed allocation feature. File system repair time (fsck) in Ext4 is much faster than in Ext2 and Ext3 (up to a 
 six-fold increase) Red Hat’s maximum supported size for Ext4 is 16TB in both RHEL 5 and 6, and 50TB in RHEL 7.

If both your server and your storage device are large, XFS is likely to be the best choice. 
Even with smaller storage arrays, XFS performs very well when the average file sizes are large 
(for example, hundreds of megabytes in size). Compared to Ext3, Ext4 has a faster file system check and repair times and
 higher streaming read and write performance on high-speed devices.  In general, Ext3 or Ext4 is better if 
 an application uses a single read/write thread and small files, 
 while XFS shines when an application uses multiple read/write threads and bigger files.

More details: [Red Hat articles](https://access.redhat.com/articles/3129891)

### Block I/O
Flexible block I/O structures (BIOs) consist of a list or a vector of segments that points to different pages in memory. This results in a dynamic 
allocation of pages to the sectors on the block device via block I/O. BIOs come up again with respect to the block 
layer. BIOs are grouped into requests before the kernel passes I/O operations to the driver's dispatch queue.

### Stacked Block Devices
As an important component of the Linux Storage Stack, it is located in front of the block layer, where logical block
devices are implemented. The LVM and software RAID are the best representatives of stacked block devices. 

### Block Layer
The block layer processes the BIOs and is responsible for forwarding application I/O requests to the storage devices.
It provides a uniform interface for data access includes both block devices such as SSD, Fibre Channel SAN, and memory
devices. The block layer also ensures an equitable distribution of I/O access, appropriate error handling, 
statistics, and a scheduling system.

Three paths for the data to get in or around the block layer.
* Traditional I/O Schedulers, such as NOOP, Deadline, or CFQ. 
* Linux multiqueue block I/O queuing mechanism (blk-mq). For high-performance flash memory.
* Diverting around the block layer directly to the BIO-based drivers.

### SCSI Layer (Small Computer System Interface layer)
SCSI is a set of standers for physical connecting and transfer data between computers and peripheral devices. SCSI layer
is between the block layer and the respective hardware drivers. 

* SCSI mid layer (SCSI upper-level drivers), scsi-mq, taking care of not only SCSI or SAS devices, but also SATA, RAID ,
and FC HBAs.
* SCSI low-lever drivers, the drivers that address the respective hardware components.


More details: [Admin Magazine](http://www.admin-magazine.com/Archive/2016/31/Linux-Storage-Stack) 
and [Thomas Krenn](https://www.thomas-krenn.com/de/wikiDE/images/e/e0/Linux-storage-stack-diagram_v4.10.png)