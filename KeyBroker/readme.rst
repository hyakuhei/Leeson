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
