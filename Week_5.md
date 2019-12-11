# Week 5: LDAP Directories and Accounts.
* LDAP: Models, Schema, and Attributes
* The LDAP Naming Model
* LDIF
* Configuring TLS Security
* Slapadd/slapmodify
* Searching the Directory
* LDAP User Authentication.
* Configure LDAP client to autogenerate user home directory
* Add samba schema to the LDAP server
* Master-Slave Configuration
* Master-Master Configuration. Pros and cons for Master-Slave and Master-Master
* Graphical LDAP Client Utilities-Apache directory studio 


## 1. LDAP: Models, Schema, and Attributes
LDAP is a lightweight client-server protocol for accessing and maintaining distributed directory services over an IP 
network. A directory is similar to a database, but tends to contain more descriptive, attribute-based information. Read much
more often than written. quick-response to high-volume lookup or search operations. Directory services play an important
role in developing intranet and internet applications by allowing the sharing of information about users, systems,
networks, services, and applications throughout the network.  

### Basic terms 
* DC: domain component
* O: Organization
* OU: Organization Unit
* CN: Common name
* SN: Sur name


* User: InterOrgPerson, or GroupsOfUniqueName
* LDAP entry: each node of the tree, in the form attributeType=value. LDAP entries are somewhat similar to the 
object-oriented programming language.

    * An LDAP entry corresponds with and object
    * LDAP entries can implement multiple objectClasses
    * objectClasses can inherit zero, one, or many objectClasses
    * objectClasses hae a root class, known as 'top'
    * objectClasses are either STRUCTURAL or AUXILIARY; entries can only implement one STRUCTURAL objectClass
    * The objectClasses of an entry can be changed at will. Only need to take care that the entry has all the
    MUST attribute types.
    * Attributes of an entry may have multiple values.

* RDN: Relative Distinguished Name, RND must be unique among the children of its parent. e.g. cn=Jack E. Wiesel
* DN: Distinguished Name, list all the RDNs, separated by commas, from the node to root. 
e.g. dn: cn=Jack E. Wiesel,ou=Sales,ou=People,dc=example,dc=com. 
Setup an user on ldap with following DN: “dn: uid=s170229,ou=Bioinformatics,ou=users,dc=biohpc,dc=swmed,dc=edu”

* Attributetype: Commonly contains a global identifier (a list of period-sperated intergers), a list of names, 
a free-form description, and a reference to another attribute type this definition inherits from. May also have 
some other informations. The following is an example of attributeType definition.  

        attributetype ( 2.5.4.4 NAME ( 'sn' 'surname' )
            DESC 'RFC2256: last (family) name(s) for which the entity is known by'
            SUP name )

* Objectclass: A special attributeType, which lists all the objectcalsses the LDAP entry manifests. An object class
lists what attribute types an entry must have, and what optional attribute types it may have. The following is an example of objectClass definition
    
        objectclass ( 2.5.6.6 NAME 'person'
            DESC 'RFC2256: a person'
            SUP top STRUCTURAL
            MUST ( sn $ cn )
            MAY ( userPassword $ telephoneNumber $ seeAlso $ description ) )

* Schemas: A part of the configuration of the server, containing two things: definitions of attribute types and 
definition of objectclasses.


### LDIF, LDAP Data Interchange Format
LDIF is the standardized way of writting down the contents of LDAP directories, entries, and operations such as add,
delete and modify.

Rules to write an LDIF:
* A paragraph per entry, where paragraphs are separated by blank lines.
* Each paragraph contains lines in the format of "keyword: value"
* Entries start by listing the keyword dn and their DN, and then list all the attributes and values the entry has.
* Lines starting with space are appended to the previous line.
* The whole file starts with the keyword 'version' and 'value' 1.

### Searches and search filters
An LDAP search takes the following information as input:
* The base DN for the search
* A search filter
* Scope of the search, either look at the base DN only, one level bellow it, or the whole subtree
* Size limit of how many matching entries to return
* Attributes to return, or none for returning all attributes.

More details: [Introduction to LDAP](https://web.archive.org/web/20050716050926/http://twistedmatrix.com/users/tv/ldap-intro/ldap-intro.html)

## 2. OpenLDAP Server configuration

Install the packages  
    
    yum -y install openldap compat-openldap openldap-clients openldap-servers openldap-servers-sql openldap-devel
    
    yum -y install sssd nss-pam-ldapd nscd pam_ldap authconfig


    systemctl start slapd
    systemctl enable slapd
    systemctl status slapd  # check the status

Set the password

    slappasswd -s ldap123   # set the password to 'ldap123'. write down the output hash. {SSHA}RqpTJBI83gZTAjmAqBUyTpZcrbuDo2Hw
    
Configure the server  
We have to update some variables in the configuration file, /etc/openldap/slapd.d/cn=config/olcDatabase={2}hdb.ldif
* olcSuffix -- Database Suffix. It's the domain name
* olcRootDN -- Root Distinguished Name for the administration user
* olcRootPW -- LDAP admin password

To make changes to the configuration file, we'd better create a ldif file and use ldapmodify command to deploy it.

    vi 01_def_domain_and_adminuser.ldif


    # define the domain name as "biophc.swmed.edu"
    dn: olcDatabase={2}hdb,cn=config
    changetype: modify
    replace: olcSuffix
    olcSuffix: dc=biohpc,dc=swmed,dc=edu
    
    # define the root user as "ldapadmin"
    dn: olcDatabase={2}hdb,cn=config
    changetype: modify
    replace: olcRootDN
    olcRootDN: cn=ldapadmin,dc=biohpc,dc=swmed,dc=edu
    
    # define the hashed password for ldapadmin as the one generated in the previous step
    dn: olcDatabase={2}hdb,cn=config
    changeType: modify
    add: olcRootPW
    olcRootPW: {SSHA}RqpTJBI83gZTAjmAqBUyTpZcrbuDo2Hw
    
Execute ldapmodify to deploy the changes

    ldapmodify -Y EXTERNAL -H ldapi:/// -f 01_def_domain_and_adminuser.ldif 

Check to see if the changes have been made
    
    ldapsearch -Y EXTERNAL -H ldapi:/// -b cn=config olcDatabase=\*
    
Allow the 'ldapadmin' user to access the LDAP database by modifying the olcDatabase={1}monitor.ldif file    

    vi 02_allow_adminuser_access_LDAP.ldif


    dn: olcDatabase={1}monitor,cn=config
    changetype: modify
    replace: olcAccess
    olcAccess: {0}to * by dn.base="gidNumber=0+uidNumber=0,cn=peercred,cn=external, cn=auth" read by dn.base="cn=ldapadmin,dc=biohpc,dc=swmed,dc=edu" read by * none

Execute ldapmodify to deploy the changes

    dapmodify -Y EXTERNAL -H ldapi:/// -f 02_allow_adminuser_access_LDAP.ldif 

Configure LDAP Logging

    echo "local4.* /var/log/ldap.log" >> /etc/rsyslog.conf
    systemctl restart rsyslog    

Check to see if the changes have been made
    
    ldapsearch -Y EXTERNAL -H ldapi:/// -b cn=config olcDatabase=\*


## 3. Setup LDAP database
Copy the sample DB configuration file to /var/lib/ldap and update the permissions

    cp /usr/share/openldap-servers/DB_CONFIG.example /var/lib/ldap/DB_CONFIG
    chown ldap:ldap /var/lib/ldap/*
    
Add extend schemas

    ldapadd -Y EXTERNAL -H ldapi:/// -f /etc/openldap/schema/cosine.ldif
    ldapadd -Y EXTERNAL -H ldapi:/// -f /etc/openldap/schema/nis.ldif 
    ldapadd -Y EXTERNAL -H ldapi:/// -f /etc/openldap/schema/inetorgperson.ldif
    
Design the data structure of your LDAP database

    vi 03_base_structure.ldif
    
    
    dn: dc=biohpc,dc=swmed,dc=edu
    dc: biohpc
    objectClass: top
    objectClass: domain
    
    dn: cn=ldapadmin,dc=biohpc,dc=swmed,dc=edu
    objectClass: organizationalRole
    cn: ldapadmin
    description: LDAP Manager
    
    dn: ou=Users,dc=biohpc,dc=swmed,dc=edu
    objectClass: organizationalUnit
    ou: Users
    
    dn: ou=Bioinformatics,dc=biohpc,dc=swmed,dc=edu
    objectClass: organizationalUnit
    ou: Bioninformatics

Execute ldapadd to deploy the changes

    ldapadd -x -w ldap123 -D "cn=ldapadmin,dc=biohpc,dc=swmed,dc=edu" -f 03_base_structure.ldif 
    
Check to see if the changes have been made
    
    ldapsearch -Y EXTERNAL -H ldapi:/// -b dc=biohpc,dc=swmed,dc=edu

Delete the Bioinformatics ou, as there is a typo

    ldapdelete "ou=Bioinformatics,dc=biohpc,dc=swmed,dc=edu" -D "cn=ldapadmin,dc=biohpc,dc=swmed,dc=edu" -w ldap123

Create the bioinformatics ou

    vi 04_add_bioinformatics_ou.ldif
    
    
    dn: ou=Bioinformatics,ou=Users,dc=biohpc,dc=swmed,dc=edu
    objectClass: organizationalUnit
    ou: Bioinformatics


Execute ldapadd to deploy the changes

    ldapadd -x -w ldap123 -D "cn=ldapadmin,dc=biohpc,dc=swmed,dc=edu" -f 04_add_bioinformatics_ou.ldif
    
Check
    
    slapcat -b "dc=biohpc,dc=swmed,dc=edu" | less


More details: [goLinuxCloud](https://www.golinuxcloud.com/install-and-configure-openldap-centos-7-linux/), 
[ITzGeek](https://www.itzgeek.com/how-tos/linux/centos-how-tos/step-step-openldap-server-configuration-centos-7-rhel-7.html)
    

## 4. Secure OpenLDAP with TLS
Install packages

    yum -y install openssl

Generate a certificate and a private key

    cd /etc/pki/CA/
    
    # Make usre the 'hostname' set in CA generation is accessible from other machine!!!
    
    # create a CA
    openssl genrsa -aes256 -out /etc/pki/CA/private/ca.key.pem
    # create a CA certificate. 
    openssl req -new -x509 -days 3650 -key /etc/pki/CA/private/ca.key.pem -extensions v3_ca -out /etc/pki/CA/certs/ca.cert.pem
    # generate a key and certificate file for openLDAP
    openssl genrsa -out private/biohpc.swmed.edu.key
    openssl req -new -key private/biohpc.swmed.edu.key -out certs/biohpc.swmed.edu.csr
    # sign the certificate with our CA
    openssl ca -keyfile private/ca.key.pem -cert certs/ca.cert.pem -in certs/biohpc.swmed.edu.csr -out certs/biohpc.swmed.edu.cert
    # verify the issued certificate against our CA
    openssl verify -CAfile certs/ca.cert.pem certs/biohpc.swmed.edu.cert 

Copy the key and certificate to openLDAP and Change the owner

    cp certs/biohpc.swmed.edu.cert /etc/openldap/certs/
    cp private/biohpc.swmed.edu.key /etc/openldap/certs/
    cp certs/ca.cert.pem /etc/openldap/certs/
    
    chown -R ldap:ldap /etc/openldap/certs/

Check the current settings 

    slapcat -b "cn=config" | egrep "olcTLSCertificateFile|olcTLSCertificateKeyFile"

Modify the default settings

    vi 07_TLS.ldfi
    
    
    dn: cn=config
    changetype: modify
    replace: olcTLSCertificateFile
    olcTLSCertificateFile: /etc/openldap/certs/biohpc.swmed.edu.cert
    -
    replace: olcTLSCertificateKeyFile
    olcTLSCertificateKeyFile: /etc/openldap/certs/biohpc.swmed.edu.key

Deploy the changes to LDAP server

    ldapmodify -Y EXTERNAL -H ldapi:/// -f 07_TLS.ldfi 

Check the settings again 

    slapcat -b "cn=config" | egrep "olcTLSCertificateFile|olcTLSCertificateKeyFile"
    
    slaptest -u

Add the new ldaps:/// protocol to the server

    vi /etc/sysconfig/slapd 
    
    # add 'ldaps:///' to SLAPD_URLS
    SLAPD_URLS="ldapi:/// ldap:/// ldaps:///"

Change the authentication of the server

    vi /etc/openldap/ldap.conf
    
    # comment out TLS_CACERTDIR and add new TLS_REQCERT 
    #TLS_CACERTDIR /etc/openldap/certs
    TLS_REQCERT never
    
Restart the server

    systemctl restart slapd


Verify TLS connectivity for LDAP

    ldapsearch -x -ZZ   


Configure Firewall if necessary

    firewall-cmd --add-service=ldap
    firewall-cmd --add-service=ldaps
    
    # or disable the firewall
    #systemctl stop firewalld
    #systemctl disable firewalld



More details: [goLinuxCloud](https://www.golinuxcloud.com/configure-openldap-with-tls-certificates/)



## 5. Create a new user with LDAP
Design the features of the user

    vi 05_add_an_user.ldif
    
    dn: uid=user1,ou=Users,dc=biohpc,dc=swmed,dc=edu
    objectClass: top
    objectClass: account
    objectClass: posixAccount
    objectClass: shadowAccount
    # cn and uid should be the same value
    cn: user1
    uid: user1
    uidNumber: 1100
    gidNumber: 1006
    homeDirectory: /home/user1
    loginShell: /bin/bash
    userPassword: {crypt}x
    shadowLastChange: 17058
    shadowMin: 0
    shadowMax: 99999
    shadowWarning: 7


Execute ldapadd to deploy the changes

    ldapadd -x -w ldap123 -D "cn=ldapadmin,dc=biohpc,dc=swmed,dc=edu" -f 05_add_an_user.ldif
    
Check to see if the changes have been made
    
    ldapsearch -Y EXTERNAL -H ldapi:/// -b dc=biohpc,dc=swmed,dc=edu
    
    # or 
    
    slapcat -b "dc=biohpc,dc=swmed,dc=edu" | less
    
Go to the client to test if you can use user1


## 6. Configure LDAP client
Install pakcages

    yum -y install openldap-clients pam_ldap nss-pam-ldapd authconfig
    
Copy certificated file from server to client
    
    mkdir /etc/openldap/cacerts/
    scp ldapserver:/etc/openldap/certs/ca.cert.pem /etc/openldap/cacerts/

Configure client to user LDAP server for authentication
    
    # make sure the value for --ldapserver is the same as the 'hostname' that setted in CA generation!!
    authconfig --enableldap --enableldapauth --enablemkhomedir --ldapserver=ldapserver --ldapbasedn="dc=biohpc,dc=swmed,dc=edu" --enableldaptls --update
    
    # this step can be achieved by using authconfig-tui commond. In the "User Information" section select "Use LDAP"
    # and in the "Authentication" section select "User LDAP Authentication". At last provide the IP and the DN of the 
    # LDAP server
         
Check the configuration

    cat /etc/openldap/ldap.conf 
    
    # make sure following lines exist
    
    TLS_CACERTDIR /etc/openldap/cacerts
    URI ldap://ldapserver/
    BASE dc=biohpc,dc=swmed,dc=edu


    cat /etc/nslcd.conf 
    
    # make sure following lines exist
    ssl start_tls
    tls_cacertdir /etc/openldap/cacerts

Restart the client

    systemctl restart nslcd

Verify TLS connectivity for LDAP

    ldapsearch -x -ZZ
    # ldapsearch -x -ZZ -d7  # for debug
    
Test to see if the user1 is available

    getent passwd user1
    
    #or 
     
    getent passwd  # get all the users
    
    su - user1
       

Change passwd for the new user, user1

    ldappasswd -H ldap://ldapserver -D "cn=ldapadmin,dc=biohpc,dc=swmed,dc=edu" -W -S "uid=user1,ou=Users,dc=biohpc,dc=swmed,dc=edu"

## 7. SAMBA with LDAP authentication       
### Add the SAMBA LDAP Schema (on LDAP Server)
Copy the example samba schema from Samba server to LDAP directory

    scp nfsserver:/usr/share/doc/samba-4.9.1/LDAP/samba.ldif /etc/openldap/schema/
    scp nfsserver:/usr/share/doc/samba-4.9.1/LDAP/samba.schema /etc/openldap/schema/
    
    # if there is not nfsserver, install the samba to get the samba.ldif
    # yum install samba samba-client samba-common cifs-utils
    
Deploy to the LDAP server

    # Note: the inetorgperson.ldif is required by samba.ldif!
    ldapadd -Y EXTERNAL -H ldapi:/// -f /etc/openldap/schema/inetorgperson.ldif
    ldapadd -Y EXTERNAL -H ldapi:/// -f /etc/openldap/schema/samba.ldif
    
Check to see if the samba.scheme is implemented

    slapcat -b 'cn=config' | grep ^dn | grep samba

### Add LDAP support in SAMBA server (on SAMBA server)
Install the package

    yum -y install smbldap-tools


In the [global] section of /etc/samba/smb.conf add the following lines

    #passdb backend = tdbsam
    log file = /var/log/samba/smb.log
    max log size = 10000
    log level 5

    passdb backend = ldapsam:ldap://ldapserver/
    ldap suffix = dc=biohpc,dc=swmed,dc=edu
    ldap admin dn = cn=ldapadmin,dc=biohpc,dc=swmed,dc=edu
    ldap ssl = start tls
    ldap passwd sync = yes

    #idmap config * : backend = tdb


Add ldapadmin to the samba database 

    smbpasswd -w ldap123 ldapadmin
    
Restart the samba server

    systemctl restart smb

    
Copy certificated file from server to client (if use TLS)
    
    scp ldapserver:/etc/openldap/certs/ca.cert.pem /etc/openldap/cacerts/
    scp ldapserver:/etc/openldap/certs/biohpc.swmed.edu.cert /etc/openldap/certs/
    scp ldapserver:/etc/openldap/certs/biohpc.swmed.edu.key /etc/openldap/certs/

Get the unique SID (Security IDentifier) for Samba

    net getlocalsid

Config the smbldap-tools file, /etc/smbldap-tools/smbldap_bind.conf

    cat /etc/smbldap-tools/smbldap_bind.conf

    slaveDN="cn=ldapadmin,dc=biohpc,dc=swmed,dc=edu"
    slavePw="ldap123"
    masterDN="cn=ldapadmin,dc=biohpc,dc=swmed,dc=edu"
    masterPw="ldap123"

Config the smbldap-tools file, /etc/smbldap-tools/smbldap.conf

    cat /etc/smbldap-tools/smbldap.conf
    
    # $Id$
    #
    # smbldap-tools.conf : Q & D configuration file for smbldap-tools
    
    #  This code was developped by IDEALX (http://IDEALX.org/) and
    #  contributors (their names can be found in the CONTRIBUTORS file).
    #
    #                 Copyright (C) 2001-2002 IDEALX
    #
    #  This program is free software; you can redistribute it and/or
    #  modify it under the terms of the GNU General Public License
    #  as published by the Free Software Foundation; either version 2
    #  of the License, or (at your option) any later version.
    #
    #  This program is distributed in the hope that it will be useful,
    #  but WITHOUT ANY WARRANTY; without even the implied warranty of
    #  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    #  GNU General Public License for more details.
    #
    #  You should have received a copy of the GNU General Public License
    #  along with this program; if not, write to the Free Software
    #  Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307,
    #  USA.
    
    #  Purpose :
    #       . be the configuration file for all smbldap-tools scripts
    
    ##############################################################################
    #
    # General Configuration
    #
    ##############################################################################
    
    # Put your own SID. To obtain this number do: "net getlocalsid".
    # If not defined, parameter is taking from "net getlocalsid" return
    #SID="S-1-5-21-2252255531-4061614174-2474224977"
    SID="S-1-5-21-1738781231-3054933728-64485614"
    
    # Domain name the Samba server is in charged.
    # If not defined, parameter is taking from smb.conf configuration file
    # Ex: sambaDomain="IDEALX-NT"
    #sambaDomain="DOMSMB"
    
    ##############################################################################
    #
    # LDAP Configuration
    #
    ##############################################################################
    
    # Notes: to use to dual ldap servers backend for Samba, you must patch
    # Samba with the dual-head patch from IDEALX. If not using this patch
    # just use the same server for slaveLDAP and masterLDAP.
    # Those two servers declarations can also be used when you have
    # . one master LDAP server where all writing operations must be done
    # . one slave LDAP server where all reading operations must be done
    #   (typically a replication directory)
    
    # Slave LDAP server URI
    # Ex: slaveLDAP=ldap://slave.ldap.example.com/
    # If not defined, parameter is set to "ldap://127.0.0.1/"
    #slaveLDAP="ldap://ldap.example.com/"
    slaveLDAP="ldap://ldapserver/"
    
    # Master LDAP server URI: needed for write operations
    # Ex: masterLDAP=ldap://master.ldap.example.com/
    # If not defined, parameter is set to "ldap://127.0.0.1/"
    #masterLDAP="ldap://ldap.example.com/"
    masterLDAP="ldap://ldapserver/"
    
    # Use TLS for LDAP
    # If set to 1, this option will use start_tls for connection
    # (you must also used the LDAP URI "ldap://...", not "ldaps://...")
    # If not defined, parameter is set to "0"
    ldapTLS="1"
    
    # How to verify the server's certificate (none, optional or require)
    # see "man Net::LDAP" in start_tls section for more details
    verify="require"
    
    # CA certificate
    # see "man Net::LDAP" in start_tls section for more details
    #cafile="/etc/pki/tls/certs/ldapserverca.pem"
    cafile="/etc/openldap/cacerts/ca.cert.pem"
    
    # certificate to use to connect to the ldap server
    # see "man Net::LDAP" in start_tls section for more details
    #clientcert="/etc/pki/tls/certs/ldapclient.pem"
    clientcert="/etc/openldap/certs/biohpc.swmed.edu.cert"
    
    # key certificate to use to connect to the ldap server
    # see "man Net::LDAP" in start_tls section for more details
    #clientkey="/etc/pki/tls/certs/ldapclientkey.pem"
    clientkey="/etc/openldap/certs/biohpc.swmed.edu.key"
    
    # LDAP Suffix
    # Ex: suffix=dc=IDEALX,dc=ORG
    #suffix="dc=example,dc=com"
    suffix="dc=biohpc,dc=swmed,dc=edu"
    
    # Where are stored Users
    # Ex: usersdn="ou=Users,dc=IDEALX,dc=ORG"
    # Warning: if 'suffix' is not set here, you must set the full dn for usersdn
    #usersdn="ou=People,${suffix}"
    usersdn="ou=Users,${suffix}"
    
    # Where are stored Computers
    # Ex: computersdn="ou=Computers,dc=IDEALX,dc=ORG"
    # Warning: if 'suffix' is not set here, you must set the full dn for computersdn
    computersdn="ou=Computers,${suffix}"
    
    # Where are stored Groups
    # Ex: groupsdn="ou=Groups,dc=IDEALX,dc=ORG"
    # Warning: if 'suffix' is not set here, you must set the full dn for groupsdn
    groupsdn="ou=Group,${suffix}"
    
    # Where are stored Idmap entries (used if samba is a domain member server)
    # Ex: idmapdn="ou=Idmap,dc=IDEALX,dc=ORG"
    # Warning: if 'suffix' is not set here, you must set the full dn for idmapdn
    idmapdn="ou=Idmap,${suffix}"
    
    # Where to store next uidNumber and gidNumber available for new users and groups
    # If not defined, entries are stored in sambaDomainName object.
    # Ex: sambaUnixIdPooldn="sambaDomainName=${sambaDomain},${suffix}"
    # Ex: sambaUnixIdPooldn="cn=NextFreeUnixId,${suffix}"
    sambaUnixIdPooldn="sambaDomainName=${sambaDomain},${suffix}"
    
    # Default scope Used
    scope="sub"
    
    # Unix password hash scheme (CRYPT, MD5, SMD5, SSHA, SHA, CLEARTEXT)
    # If set to "exop", use LDAPv3 Password Modify (RFC 3062) extended operation.
    password_hash="SSHA"
    
    # if password_hash is set to CRYPT, you may set a salt format.
    # default is "%s", but many systems will generate MD5 hashed
    # passwords if you use "$1$%.8s". This parameter is optional!
    password_crypt_salt_format="%s"
    
    ##############################################################################
    # 
    # Unix Accounts Configuration
    # 
    ##############################################################################
    
    # Login defs
    # Default Login Shell
    # Ex: userLoginShell="/bin/bash"
    userLoginShell="/bin/bash"
    
    # Home directory
    # Ex: userHome="/home/%U"
    userHome="/home/%U"
    
    # Default mode used for user homeDirectory
    userHomeDirectoryMode="700"
    
    # Gecos
    userGecos="System User"
    
    # Default User (POSIX and Samba) GID
    defaultUserGid="513"
    
    # Default Computer (Samba) GID
    defaultComputerGid="515"
    
    # Skel dir
    skeletonDir="/etc/skel"
    
    # Treat shadowAccount object or not
    shadowAccount="1"
    
    # Default password validation time (time in days) Comment the next line if
    # you don't want password to be enable for defaultMaxPasswordAge days (be
    # careful to the sambaPwdMustChange attribute's value)
    defaultMaxPasswordAge="45"
    
    ##############################################################################
    #
    # SAMBA Configuration
    #
    ##############################################################################
    
    # The UNC path to home drives location (%U username substitution)
    # Just set it to a null string if you want to use the smb.conf 'logon home'
    # directive and/or disable roaming profiles
    # Ex: userSmbHome="\\PDC-SMB3\%U"
    userSmbHome="\\PDC-SRV\%U"
    
    # The UNC path to profiles locations (%U username substitution)
    # Just set it to a null string if you want to use the smb.conf 'logon path'
    # directive and/or disable roaming profiles
    # Ex: userProfile="\\PDC-SMB3\profiles\%U"
    userProfile="\\PDC-SRV\profiles\%U"
    
    # The default Home Drive Letter mapping
    # (will be automatically mapped at logon time if home directory exist)
    # Ex: userHomeDrive="H:"
    userHomeDrive="H:"
    
    # The default user netlogon script name (%U username substitution)
    # if not used, will be automatically username.cmd
    # make sure script file is edited under dos
    # Ex: userScript="startup.cmd" # make sure script file is edited under dos
    #userScript="logon.bat"
    userScript=""
    
    # Domain appended to the users "mail"-attribute
    # when smbldap-useradd -M is used
    # Ex: mailDomain="idealx.com"
    #mailDomain="example.com"
    mailDomain="biohpc.swmed.edu"
    
    # Allows not to generate LANMAN password hash
    lanmanPassword="0"
    
    ##############################################################################
    #
    # SMBLDAP-TOOLS Configuration (default are ok for a RedHat)
    #
    ##############################################################################
    
    # Allows not to use smbpasswd (if with_smbpasswd="0" in smbldap.conf) but
    # prefer Crypt::SmbHash library
    with_smbpasswd="0"
    smbpasswd="/usr/bin/smbpasswd"
    
    # Allows not to use slappasswd (if with_slappasswd="0" in smbldap.conf)
    # but prefer Crypt:: libraries
    with_slappasswd="0"
    slappasswd="/usr/sbin/slappasswd"
    
    # comment out the following line to get rid of the default banner
    # no_banner="1"
    no_banner="1"


Test to see of you can get the userlist and/or grouplist

    smbldap-userlist
    
    smbldap-grouplist
    
Create necessary entries in LDAP for SAMBA

    smbldap-populate
    
Add a new user with smbldap tools

    smbldap-useradd -a -P -m user2  #(type in passwd for user2, user2123)
    
    # test to get the passwd from LDAP server
    getent passwd user2

To remove a user

    smbldap-userdel user2
    
To give the access permit for user2 to the shared folder new_home 

    vi /etc/samba/smb.conf
    
    # in the [new_home] section add the Group or the user itself to the valid users list
    valid users = emil @collaboration @"Domain Users"
    
Restart the smb server

    systemctl restart nmb smb


### Test SAMBA-LDAP configurations from the Linux client

    smbclient -U user2 //192.168.56.103/user2
    
### Test SAMBA-LDAP configurations from the Windows client
Change the name of Workgroup to SAMBA

    Computer --(right click)--> Properties --> Computer name, domain, and workgroup settings 
    --> Change settings --> Computer Name --> Change... --> Member of Workgroup (set to 'SAMBA')

Browse to open the shared directories

    Computer --> Network --> VAGRANT ( this is the hostname of the samba server) --> user2, user2123 (username and passwd)
    
    
More details:  
smb.conf [7th zero blog](https://7thzero.com/blog/configure-centos-7-samba-server-use-secure-ldap-authentication)  
smbldap-tools [Linux/Network Admin's blog](https://admin.shamot.cz/?p=470), [Help Ubuntu](https://help.ubuntu.com/lts/serverguide/samba-ldap.html)


## 8. OpenLDAP Master-Slave configuration
### Setup Master server
Create a new user for pushing the changes

    vi 08_rpuser.ldif

    dn: uid=rpuser,ou=Users,dc=biohpc,dc=swmed,dc=edu
    objectClass: simpleSecurityObject
    objectclass: account
    uid: rpuser
    description: Replication  User
    userPassword: rpuser123
    
Enable the syncprov module

    vi 09_syncprov_mod.ldif
    
    dn: cn=module,cn=config
    objectClass: olcModuleList
    cn: module
    olcModulePath: /usr/lib64/openldap
    olcModuleLoad: syncprov.la
    
Enable syncprov for each directory 

    vi 10_syncprov.ldif
    
    dn: olcOverlay=syncprov,olcDatabase={2}hdb,cn=config
    objectClass: olcOverlayConfig
    objectClass: olcSyncProvConfig
    olcOverlay: syncprov
    olcSpSessionLog: 100

Deploy the changes

    ldapadd -x -w ldap123 -D "cn=ldapadmin,dc=biohpc,dc=swmed,dc=edu" -f 08_rpuser.ldif         
    ldapadd -Y EXTERNAL -H ldapi:/// -f 09_syncprov_mod.ldif
    ldapadd -Y EXTERNAL -H ldapi:/// -f 10_syncprov.ldif

### Setup Slave server
Configure the slave server

    vi 08_rp.ldif
    
    
    dn: olcDatabase={2}hdb,cn=config
    changetype: modify
    add: olcSyncRepl
    olcSyncRepl: rid=001
      provider=ldap://ldapserver/
      bindmethod=simple
      binddn="uid=rpuser,ou=Users,dc=biohpc,dc=swmed,dc=edu"
      credentials=rpuser123
      searchbase="dc=biohpc,dc=swmed,dc=edu"
      scope=sub
      schemachecking=on
      type=refreshAndPersist
      retry="30 5 300 3"
      interval=00:00:05:00

The meanings of the slave config fils
* add: olcSyncRepl          # add a new slave
* olcSyncRepl: rid=001      # the id of the slave, a three digit number
* provider=                 # master server
* binddn=                   # rpuser's dn
* credentials=              # rpuser's passwd
* searchbase=               # base of the DB

Deploy the changes

    ldapmodify -Y EXTERNAL -H ldapi:/// -f 08_rp.ldif 

Check the LDAP database

    slapcat -b "dc=biohpc,dc=swmed,dc=edu"  | less 

Configure the clients to bind with the slave server, too

    authconfig --enableldap --enableldapauth --enablemkhomedir --ldapserver=ldapserver,ldapserver2 --ldapbasedn="dc=biohpc,dc=swmed,dc=edu" --enableldaptls --update



More details: [Itzgeek.com](https://www.itzgeek.com/how-tos/linux/configure-openldap-master-slave-replication.html)


## 9. OpenLDAP Master-Master configuration
### on master1 (the master server in the previous section)
Set server ID

    vi 11_serverID.ldif
    
    
    dn: cn=config
    changetype: modify
    replace: olcServerID
    olcServerID: 1 ldap://ldapserver/
    olcServerID: 2 ldap://ldapserver2/

Set olcSyncRepl and turn on the mirror mode

    vi 12_mirrorMode.ldif
    
    
    dn: olcDatabase={2}hdb,cn=config
    changetype: modify
    replace: olcSyncRepl
    olcSyncRepl: rid=001
      provider=ldap://ldapserver/
      bindmethod=simple
      binddn="cn=ldapadmin,dc=biohpc,dc=swmed,dc=edu"
      credentials=ldap123
      searchbase="dc=biohpc,dc=swmed,dc=edu"
      scope=sub
      schemachecking=on
      type=refreshAndPersist
      retry="30 5 300 3"
      interval=00:00:05:00
    olcSyncRepl: rid=002
      provider=ldap://ldapserver2/
      bindmethod=simple
      binddn="cn=ldapadmin,dc=biohpc,dc=swmed,dc=edu"
      credentials=ldap123
      searchbase="dc=biohpc,dc=swmed,dc=edu"
      scope=sub
      schemachecking=on
      type=refreshAndPersist
      retry="30 5 300 3"
      interval=00:00:05:00
    -
    replace: olcMirrorMode
    olcMirrorMode: TRUE
    
Deploy the changes

    ldapmodify -Y EXTERNAL -H ldapi:/// -f 11_serverID.ldif
    ldapmodify -Y EXTERNAL -H ldapi:/// -f 12_mirrorMode.ldif

Config the slapd and add the full path for SLAPD_URLS

    vi /etc/sysconfig/slapd
    
    #SLAPD_URLS="ldapi:/// ldap:/// ldaps:///"
    SLAPD_URLS="ldapi:/// ldap://ldapserver/ ldaps:///"

Restart the server and check the log file

    systemctl restart slapd
    
    tail /var/log/ldap.log


### on master2 (the slave server in the previous section)
Enable the syncprov module

    vi 09_syncprov_mod.ldif
    
    dn: cn=module,cn=config
    objectClass: olcModuleList
    cn: module
    olcModulePath: /usr/lib64/openldap
    olcModuleLoad: syncprov.la
    
Enable syncprov for each directory 

    vi 10_syncprov.ldif
    
    dn: olcOverlay=syncprov,olcDatabase={2}hdb,cn=config
    objectClass: olcOverlayConfig
    objectClass: olcSyncProvConfig
    olcOverlay: syncprov
    olcSpSessionLog: 100

Deploy the changes

    ldapadd -Y EXTERNAL -H ldapi:/// -f 09_syncprov_mod.ldif
    ldapadd -Y EXTERNAL -H ldapi:/// -f 10_syncprov.ldif

Set server ID

    vi 11_serverID.ldif
    
    
    dn: cn=config
    changetype: modify
    replace: olcServerID
    olcServerID: 1 ldap://ldapserver/
    olcServerID: 2 ldap://ldapserver2/

Set olcSyncRepl and turn on the mirror mode

    vi 12_mirrorMode.ldif
    
    
    dn: olcDatabase={2}hdb,cn=config
    changetype: modify
    replace: olcSyncRepl
    olcSyncRepl: rid=003
      provider=ldap://ldapserver/
      bindmethod=simple
      binddn="cn=ldapadmin,dc=biohpc,dc=swmed,dc=edu"
      credentials=ldap123
      searchbase="dc=biohpc,dc=swmed,dc=edu"
      scope=sub
      schemachecking=on
      type=refreshAndPersist
      retry="30 5 300 3"
      interval=00:00:05:00
    olcSyncRepl: rid=004
      provider=ldap://ldapserver2/
      bindmethod=simple
      binddn="cn=ldapadmin,dc=biohpc,dc=swmed,dc=edu"
      credentials=ldap123
      searchbase="dc=biohpc,dc=swmed,dc=edu"
      scope=sub
      schemachecking=on
      type=refreshAndPersist
      retry="30 5 300 3"
      interval=00:00:05:00
    -
    replace: olcMirrorMode
    olcMirrorMode: TRUE
    
Deploy the changes

    ldapmodify -Y EXTERNAL -H ldapi:/// -f 11_serverID.ldif
    ldapmodify -Y EXTERNAL -H ldapi:/// -f 12_mirrorMode.ldif

Config the slapd and add the full path for SLAPD_URLS

    vi /etc/sysconfig/slapd
    
    #SLAPD_URLS="ldapi:/// ldap:/// ldaps:///"
    SLAPD_URLS="ldapi:/// ldap://ldapserver2/ ldaps:///"

Restart the server and check the log file

    systemctl restart slapd
    
    tail /var/log/ldap.log


### Test the master-master settings

To test the settings, one can connect to one of the servers, make some changes to user1, and see if the changes have
been pushed to the other server automatically.

On one server, search the info of user1
    
    ldapsearch -x -w ldap123 -D "cn=ldapadmin,dc=biohpc,dc=swmed,dc=edu" "cn=user1"

One the other server, change the gid of user1 to different value

    vi 14_test_change_user1.ldif
    
    dn: uid=user1,ou=Users,dc=biohpc,dc=swmed,dc=edu
    changetype: modify
    replace: gidNumber
    gidNumber: 513

    
    # deloy the changes 
    ldapmodify -x -w ldap123 -D "cn=ldapadmin,dc=biohpc,dc=swmed,dc=edu" -f 14_test_change_user1.ldif 

    # see the changes on this server
    ldapsearch -x -w ldap123 -D "cn=ldapadmin,dc=biohpc,dc=swmed,dc=edu" "cn=user1"


## 10. Apache directory studio
Install jdk

    yum -y install java-11-openjdk java-11-openjdk-devel

Install minimal gnome desktop

    yum -y groupinstall "X Window System"
    yum -y install gnome-classic-session gnome-terminal nautilus-open-terminal control-center liberation-mono-fonts

Install and run ApacheDirectoryStudio
    
    scp ApacheDirectoryStudio-2.0.0.v20180908-M14-linux.gtk.x86_64.tar.gz root@192.168.56.104:/root/tools/src
    tar zxf ApacheDirectoryStudio-2.0.0.v20180908-M14-linux.gtk.x86_64.tar.gz
    cd ApacheDirectoryStudio
    ./ApacheDirectoryStudio
    
Alternatively, you can run ApacheDirectoryStudio from local machine and connect to the LDAP server to manage it.
