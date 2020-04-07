# Week 11: Security in HPC
* Why is Security important in Academic HPC
* UTSW Information Security Policies
* Account Security
* Network Security
* Filesystem Security
* Software Security

## Why is Security important in Academic HPC

[Sean Peisert's PPT](https://www.nist.gov/system/files/documents/2018/03/28/seannist_hpc_security.pdf)  


### Threats to HPC
* Confidentiality  
    * Data leakage
* Integrity
    * Alteration of code or data
    * Misuse of computing cycles
* Availability
    * Disruption/denial of service against HPC systems or networks that connect them
    
### Challenges & opportunities
* Key security challenges
    * Traditional security solutions often compete with priority of high-performance
    * Many HPC environments are highly 'open' to enable broad scientific collaboration
    
* Key security opportunities
    * HPC systems used for distinctive purposes, and have strong "regularity" of activity
    * Custom HW/SW stacks provide opportunities for enhanced security monitoring
    * Trend toward containerized operation & limited interfaces in HPC is likely to help

## UTSW Information Security Policies
* ISR-104 Acceptable use of information resources
* ISR-108 Password management
* ISR-110 Network security management
* ISR-111 Systems access management

## Account Security
PAM, Pluggable Authentication Modules

Location:  
    * /etc/pam.d  
    * /etc/pamd.d/login  
    * /etc/pamd.d/sshd  

Module interfaces:  
    * auth - Authenticates users  
    * account - verifies if access is permitted  
    * password - change a user's password  
    * session - manages user's sessions  
    
Locking and unlocking accounts

    passwd -l bob                   # lock. or set the login shell to nologin shell
    chsh -s /sbin/nologin bob       # lock bob 
    passwd -u bob                   # unlock
        
Check the authentication logs
        
    last                            # check the authentication logs
    lastb
    lastlog
    
Intrusion prevention with fail2ban

    fail2ban                        # monitors log files
    
/etc/securetty (all tty the root can use)

sudo
    
    export EDITOR=vi                # select editor for visudo
    visudo                          # config sudoers  
        bob ALL=(root) /usr/bin/yum     # allow bob to run yum as root
    visudo -f /etc/sudoers.d/bob    # additional configure file for bob
        bob ALL=(ALL) /usr/bin/whoami   # allow bob to run whoami as anyone
    sudo -l -U bob                  # list what bob can do
    sudo -ll -U bob                 # list what bob can do (more details)
    sudo -l                         # list what can i do with sudo
    sudo -u apache whoami           # use apache account to execute whoami
    cat /var/log/secure             # show all the history of sudoers

ssh

    vi /etc/ssh/sshd_config
        PermitRootLogin no              # disabling SSH root logins
        DenyUsers  user1 user2          # disabling direct logins from the accounts
        DenyGroups  group1 group2       # disabling direct logins from the accounts
        AllowUsers  user1 user2         # allow direct logins from the accounts
        AllowGroups  group1 group2      # allow direct logins from the accounts
        AllowTCPForwarding no           # disable TCP forwarding
        GatewayPorts no
        ListenAddress IP1               # listen address
        ListenAddress IP2
        Port 2222
    
    # copy pub key to remote server     
    ssh-copy-id [user@]host             # copy the pub key to the remote host [~/.ssh/authorized_keys]
    
    # SSH Port Forwarding
    ssh -L 3306:127.0.0.1:3306 server1

    # Reverse Port Forwarding
    ssh -R 2222:127.0.0.1:22 server1    # server1 2222 to local 22
    
    # Dynamic Port Forwarding / SOCKS
    ssh -D 8080 server1                 # forward all local request on 8080 to 22 through server1
    
    # add the new port to SELinux
    semanage port -a -t ssh_port_t -p tcp PORT
    # check 
    semanage port -l | grep ssh
    
    systemctl reload sshd
    
## Network Security

### Show active internet connections
    
    # netstat
    netstat -nutlp

    #Port Scanning
    nmap HOSTNAME_OR_IP
    # list open files
    lsof -i
    # testing a specific port
    telnet HOST_OR_IP PORT
    # netcat
    nc -v HOST_OR_IP PORT
    
### Linux Firewall = Netfilter + IPTables   
* Netfilter, a kernel framework
* IPTable, a packet selection system

IPtalbe, table, chain, rules

Default Tables
* Filter        - most commonly used
* NAT           - network address translation, share one IP address
* Mangle        - Alter packets, e.g. change TTL of the packet
* Raw           - to disable connection tracking
* Security      - used by  SELinux

Default Chains
* INPUT
* OUTPUT
* FORWARD
* PREROUTING
* POSTROUTING

Default Chain in Tables
* Filter        : INPUT, OUTPUT, FORWARD 
* NAT           : INPUT, OUTPUT, PREROUTING, POSTROUTING
* Mangle        : INPUT, OUTPUT, FORWARD, PREROUTING, POSTROUTING
* Raw           : OUTPUT, PREROUTING
* Security      : INPUT, OUTPUT, FORWARD

Traffic
* incoming packets, network --> PREROUTING --> INPUT --> local system
* forwarding packets, network --> PREROUTING --> FORWARD --> POSTROUTING --> network
* outgoing packets, local system --> OUTPUT --> POSTROUTING --> network

Rules = Match + Target  
Match on:
* Protocol
* Source/Dest IP or network
* Source/Dest Port
* Network interface

Target:
* Chain
* Built-in targets:
    * ACCEPT
    * DROP
    * REJECT
    * LOG
    * RETURN
     
### iptatbles / ip6tables

    iptables -L             # display the filter table
    iptables -t nat -L      # display the nat table
    iptables -nL            # using numeric output
    iptables -vL            # using verbose output
    iptables --line-numbers -L  # use line nums
    
    iptables -P CHAIN TARGET    # set the default TARGET for CHAIN
    iptables -A CHAIN RULE-SPECIFICATION        # append a rule to the CHAIN
    iptables [-t TABLE] -A CHAIN RELE           # append a rule to the CHAIN in TABLE
    iptables -I CHAIN [RULENUM] RULE            # insert a rule to the top of CHAIN
    iptables -D CHAIN RULE                      # delete a rule 
    iptables -D CHAIN RULENUM                   # delete a rule
    
    iptables [-t talbe] -F [chain]              # flush a rules in [chain] in [table]
    
Rule matching section
* -s SOURCE, match source, e.g. -s 10.11.12.0/255.255.255.0
* -d DESTINATION, match destination, e.g. -d 216.58.192.0/24
* -p PROTOCOL, match protocol, e.g. -p tcp, -p icmp
* -p PROTOCOL [-m PROTOCOL] --dport PORT, desitnation port, e.g. -p tcp --dport 80
* -p PROTOCOL [-m PROTOCOL] --sport PORT, source port, e.g. -p tcp --sport 80
* -p icmp [-m icmp] --icmp-type TYPE, ICMP packet type, e.g. -p icmp --icmp-type echo-reply
* -m limit --limit rate[/second/minute/hout/day], match until a limit is reached. e.g. -m limit --limit 5/m --limit-burst 10

Target section
* -j TARGET_OR_CHAIN, specify a jump point or target
* -j ACCEPT
* -j DROP
* -j LOGNDROP,  custom chain

### Examples

    # drop all packet from 216.58.219.174 (block this ip)
    iptables -A INPUT -s 216.58.219.174 -j DROP
    
    # accpet tcp visit on port 80 from anywhere
    iptables -A INPUT -p tcp --dport 80 -j ACCEPT
    
    # accpet tcp visit on port 22 from 10.0.0.0/24
    iptables -A INPUT -s 10.0.0.0/24 -p tcp --dport 22 -j ACCEPT
    
    # block all other tcp visit on port 22
    iptables -A INPUT -p tcp --dport 22 -j DROP
    
    # block all other visits 
    iptables -A INPUT -j DROP
    
    # delete the rule in line 1
    iptables -D INPUT 1
    
    # delete all rules (flush)
    iptables -F
    
    # fight against Dos attack
    iptables -I INPUT -p tcp --dport 80 -m limit --limit 50/min --limit-burst 200 -j REJECT
    
    # fight against Dos attack, only new connections
    iptables -I INPUT -p tcp --dport 80 -m limit --limit 50/min --limit-burst 200 -m state --state NEW -j REJECT
    
    # create a new CHAIN
    iptables [-t table] -N CHAIN
    
    # delete a new CHAIN
    iptables [-t table] -X CHAIN
    
    # save the rules in CentOS
    yum install iptables-services
    service iptables save
    
    # save the rules in Ubuntu
    apt-get install iptables-persistent
    netfilter-persistent save
    
    # accept tcp visits on 22 from 10.0.0.0, 
    # for all other visits, send to the new chain, LOGNDROP, 
    # log and drop them all
    iptables -A INPUT -p tcp -s 10.0.0.0/24 --dport 22 -j ACCEPT
    iptables -N LOGNDROP
    iptables -A LOGNDROP -p tcp -m limit --limit 5/min -j LOG --log-prefix "iptables BLOCK " # find from system log
    iptables -A LGONDROP -j DROP
    iptables -A INPUT -j LOGNDROP 
    
    service iptables save
    
### TCP Wrappers
* /etc/hosts.allow  # is checked first
* /etc/hosts.deny  

        # Format:  
        # SERVICE(S) : CLIENT(S) [: ACTION(S)]
        # services/clients seperated by ','
        # clients can be hostnames, wildcard supported
        
        sshd : 10.0.0.0
        sshd : 10.0.0.0/255.255.0.0
        sshd : 10.                      # ip starts with 10
        sshd : /etc/hosts.allow         # hosts in file
        sshd : ALL EXCEPT .hackers.net  # all except
        
        sshd, imapd : 10.0.0.1
        ALL : 10.0.0.1
        sshd : .examples.com
        sshd : jumpbox*.examples.com
        
        sshd : 10.0.0.1: severity emerg             # gene emergence message if 10.0.0.1 ssh
        sshd : 10.0.0.1: severity local0.alert
        sshd : 10.0.0.1: spawn /usr/bin/wall "attacking from %a" 

### Exercise

        # allow 10.0.0.0 to visit 22 via SSH
        iptabels -A INPUT -p tcp -s 10.0.0.0/24 --dport 22 -j ACCEPT 
        # drop all the other visits on 22
        iptabels -A INPUT -p tcp --dport 22 -j DROP
        # save the rules
        service iptables save
        
        # block 192.168.0.29 from visiting port 22 and 80
        iptables -A INPUT -s 192.168.0.29 --dport 22 -j DROP
        iptables -A INPUT -s 192.168.0.29 --dport 80 -j DROP
        # check the tables
        iptables -nL
        # save the rules
        service iptables save
    
## Filesystem Security

### Special modes
* Setuid, set user ID upon execution, runs using the OWNER's UID. e.g. /usr/bin/passwd, ping, chsh, 
* Setgid, set group ID upon execution, runs using the OWNER's GID. e.g. /usr/bin/wall, , 
* Sticky Bit, only allow the owner of the file/directory to delelet it. e.g. /tmp


        # Find all setuid files
        find / -perm /4000 -ls
        find / -perm +4000 -ls      # old version of find
        
        # Find all setgid files
        find / -perm /2000 -ls
        find / -perm +2000 -ls      # old version of find

### xatt for files, extended attrubits [ref](https://linoxide.com/how-tos/howto-show-file-attributes-in-linux/)
* i, immutable, file cannot be removed or modified or linked. The root users has to remove i first
* a, append only, file cannot be removed or modified. The root has to remove a first.

        # list all attr
        lsattr /etc/motd
        lsattr /var/log/messages
        
        # setting attr
        chattr +/-/=i/a
        

### ACLs
    
enable acl

    mount -o acl /path/to/dev /path/to/mount
    # set acl as default
    tune2fs -o acl /path/to/dev
    # check
    tune2fs -l /path/to/dev | grep options
    
set acl

    setfacl -m ACL_RULE FILE_OR_DIR
    setfacl -m u:jason:rwx xxx.sh
    setfacl -m m:rx xxx.sh                # all uid gid can't write
    
ACL_RULE format

    u:uid:perms         # set ACL for a user
    g:gid:perms         # set ACL for a group
    m:perms             # set the effective rights mask. 
    o:perms             # set the for others. 
    
set default acl (only to dir)

    d:[ugo]:perms
    
to remove a rule

    setfacl -x ACL_RULE FILE_OR_DIR
    
to remove all rules

    setfacl -b FILE_OR_DIR
    
to view ACLs

    getfacl FILE_OR_DIR    

### Rootkit  
[chkrootkit](http://www.chkrootkit.org)  
[rkhunter](http://rkhunter.sourceforge.net)  

    rkhunter --update       
    rkhunter --propupd      # trust the current state of the machine
    rkhunter --c
    cat /var/log/rkhunter.log
    rkhunter -c --rwo
    rkhunter --cronjob

[OSSEC](http://ossec.github.io)  

### Exercise

    su - jane
    mkdir project
    setfacl -m u:xin:r project
    setfacl -m u:kurt:r project
    setfacl -m u:lisa:000 project

    getfacl project


    
## Physical Security
keep the data center and computer rooms locked at all times  
maintain access controls  
allow access by need  

### Single user mode    

        GRUB boot loader
    
        press 'e'
        find the line starts with 'linux'
        append 's' or '1' or 'resuce'
        boot ctrl+x or 'b'
    
Set require root passwd in single user mode

        # old linux
        vi /ect/config/init
            change the following line to sulogin
            SINGLE=/sbin/sushell
            
            SINGLE=/sbin/sulogin
        
        # systemd linux
        cd /lib/systemd/system
        vi emergency.service     vi rescue.service
        
        ExecStart=.... change "sushell" to "sulogin"
    
Bypass the passwd for single user mode
    
        GRUB boot loader
    
        find the line starts with 'linux'
        append "init=/bin/bash"
    
Secure the boot loader (grub will ask for both username and password)

        cd /etc/grub.d
        vi 40_custom
            set superusers="root"
            password root root_pass_word
        
        #encrypt the root_pass_word
        # gene passwd hash
        grub2-mkpasswd-pbkdf2 
        
        password_pbkdf2 root the_hash
        
        # update the configuration
        # for centOS
        grub2-mkconfig -o /boot/grub2/grub.cfg
        # for ubuntu
        update_grub 
        
Bypass the secure the boot loader 

        Use a CD/USB to boot to a Rescue mode
        
        mount the disk and vi /boot/grub2/grub.cfg and comment out the following lines
        # set superusers="root"
        # password root root_pass_word
    
### Disk encryption
* dm-crypt
* LUKS (a front-end for dm-crypt)

          # install cryptsetup
          yum install cryptsetup
    
          fdisk -l
    
          # write random data to /dev/sdb
          shred -v -n 1 /dev/sdb
    
          # setup passphrase
          cryptsetup luksFormat /dev/sdb
    
          # create a virtual mapper for /dev/sdb
          cryptsetup luksOpen /dev/sdb opt
          ls -l /dev/mapper/opt
    
          # format to ext4
          mkfs -t ext4 /dev/mapper/opt
    
          # find the uuid 
          blkid
    
          # ask for password in every boot/mount
          vi /etc/cryptab
          #name   disk      passwd  format
          opt    /dev/sdb   none   luks
          opt    UUID="xxxxxxx"   none   luks
    
          # umount
          umount /opt
          # remove the mapper
          cryptsetup luksClose opt
    
Encrypt a file and use it as disk

        mkdir data
        # allocate a file
        fallocate -l 100M /data/opt
        
        # get the strings to check 
        strings /data/opt
        
        # optional. write random strings to the file
        dd if=/dev/urandom of=/data/opt bs=1M count=100
        
        # format with luks
        cryptsetup luksFormat /data/opt
        
        # crate a mapper
        cryptsetup luksOpen /data/opt opt
        
        # format as ext4
        mkfs -t ext4 /dev/mapper/opt
        
        # mount
        mount /dev/mapper/opt /opt
    

Disable virtual reboot "Ctrl+Alt+Delete"

        # disable 
        systemctl mask ctrl-alt-del.target
        # take effect
        systemctl daemon-reload
    
## Software Security

Three pillars of security
* Confidentiality, disclosing information to unauthorized parties
* Integrity, protecting information from being created or modified by unauthorized parties
* Availability, ensuring that authorized parties are able to access the system components when needed

Threats
* Spoofing of an identity
* Tampering, unauthorized modification that alters the system behavior
* Repudiation, a user plausibly denies that they performed an action
* Information disclosure, 
* Denial of service
* Elevation of privilege

Risk = impact x likelihood  
Weaknees and vulnerability  
Exploit, the process of attacking a vulnerability in a program  

An exploit through the eyes of an attacker  
    
    Attack surface --> program flow --> impact surface
    
Program flow
* control flow
* data flow




## GnuPG

Install package

    apt-get install gnupg
    
Gen key

    gpg --full-gen-key              # step-by-step

    gpg --gen-key                   # use default settings, expired in 2 years
    
List the key pairs

    gpg --list-keys
    
Export public keys

    gpg --armor --export --output xxx_pubkey.gpg KEY_ID
    # or
    gpg -a --export KEY_ID > xxx_pubkey.gpg
    
Submit keys to a key-server

    gpg --send-keys --keyserver keyserver.ubuntu.com KEY_ID
    
Import keys

    gpg --import-keys xxx_pubkey.gpg
    
Search keys

    gpg --search-keys --keyserver keyserver.ubuntu.com KEY_ID/E-Mail/NAME
    
Encrypt a secret file using your friend's public key

    gpg --encrypt [--armor] --recipient XXXX a.txt
    
Decrypt a file

    gpg --decrypt a.txt.gpg > secret.txt
    
Send an encrypted file to multiple recipient

    gpg -r xxx1 -r xxx2 -r xxx3 --encrypt a.txt

Sign a file

    gpg --sign file.txt                             # will generate a signed file file.txt.gpg
    gpg --clearsign file.txt --output file.sig      # sign in ASCII format 
    
Verify a signature

    gpg --verify file.txt.gpg
    
Extract the doc from the signed file

    gpg --output doc.txt --decrypt file.txt.gpg
    
Detached sign

    gpg --armor --detach-sig file.txt               # signature will be in file.txt.asc
    
Verity a detached signature

    gpg --verify file.txt.asc file.txt
    
Encrypt and Sign a file

    gpg --sign --encrypt --recipient XXX file.txt
    
Backup the private keys  

    gpg -a --export-secret-keys KEY_ID > xxx-secret-gpg.key
    gpg --export-ownertrust > xxx-ownertrust-gpg.txt
    
Restore the private keys

    gpg --import-ownertrust xxx-ownertrust-gpg.txt
    gpg --import xxx-secret-gpg.key
    
## VNC server

Install  

    yum install tigervnc-server
    cp /usr/lib/systemd/system/vncserver@.service /etc/systemd/system/vncserver@.service

Config  
 
    vim /etc/systemd/system/vncserver@.service
    
    # add the following lines
    ExecStart=/usr/sbin/runuser -l <USER> -c "/usr/bin/vncserver %i -geometry 1280x1024"
    PIDFile=/home2/<USER>/.vnc/%H%i.pid

Reload & start the service  

    systemctl daemon-reload
    # :5 is the display number ---> port 5095/tcp 
    systemctl start vncserver@:5.service
    systemctl status vncserver@:5.service
    systemctl enable vncserver@:5.service

Set vncpasswd  

    su - <USER>
    vncpasswd
    ls ~/.vnc/
    
Check if is running  

    systemctl status vncserver@:5.service
    netstat -anpt | grep vnc

Add to firewall  

    firewall-cmd --permanent --zone=public --add-port=5905/tcp
    firewall-cmd --reload

 

