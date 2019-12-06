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


## LDAP: Models, Schema, and Attributes
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
some other informations.


    # An example of attributeType definition
    attributetype ( 2.5.4.4 NAME ( 'sn' 'surname' )
        DESC 'RFC2256: last (family) name(s) for which the entity is known by'
        SUP name )

* Objectclass: A special attributeType, which lists all the objectcalsses the LDAP entry manifests. An object class
lists what attribute types an entry must have, and what optional attribute types it may have. 

    
    # An example of objectClass definition
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

## OpenLDAP Server configuration

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

Check to see if the changes have been made
    
    ldapsearch -Y EXTERNAL -H ldapi:/// -b cn=config olcDatabase=\*


## Setup LDAP database
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
    

## Secure OpenLDAP with TLS
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



## Create a new user with LDAP
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


## Configure LDAP client
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

       
## Add the SAMBA LDAP Schema (on LDAP Server)
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

## Add LDAP support in SAMBA server (on SAMBA server)
In the [global] section of /etc/samba/smb.conf add the following lines

    #passdb backend = tdbsam
    passdb backend = ldapsam:ldap://ldapserver/
    ldap suffix = dc=biohpc,dc=swmed,dc=edu
    ldap admin dn = cn=ldapadmin,dc=biohpc,dc=swmed,dc=edu
    ldap ssl = start tls
    ldap passwd sync = yes

    idmap config * : backend = tdb


Add ldapadmin to the samba database 

    smbpasswd -w ldap123 ldapadmin
    
Restart the samba server

    systemctl restart smb
    
TODO: Samba status looks fine, but smb client can't mount!
