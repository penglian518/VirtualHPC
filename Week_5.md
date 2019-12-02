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