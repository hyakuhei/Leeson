KeyBroker
=========

The Leeson key broker is responsible for receiving, validating and responding
to key material requests from machine that need to decrypt their drives.

Validation
==========
The prototype simply validates machines based on their IP address, and returns
only key material that is known to belong to disks within that machine.

Configuration
=============
Prototype doesn't include the installer magic to setup the initial IP->UUID
mappings but it's assumed that a robustly authenticated API call will be
all that's required.

Database
========
The database for the prototype is a single table SQLite instance with the
following layout:

CREATE TABLE mapping(
 ip varchar(255) not null,
 uuid varchar(255) not null,
 keymat varchar(255) not null
);

For this example we have a host at IP address 10.1.1.1 this host has a single
hard drive with a UUID of aa-bb-cc-dd-ee. The encryption key for this disk is
"DEADBEEFCAFEBABE"

The following SQLite3 commands will update the database with this information

$sqlite3 brokerdb
sqlite> INSERT INTO mapping VALUES ("10.1.1.1","aa-bb-cc-dd-ee", "DEADBEEFCAFEBABE");
sqlite> .exit
$
