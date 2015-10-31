# Leeson Development Plans
This area contains various documentation artifacts, the main documentation
currently is still the main README for the project

Sequence diagrams
-----------------
To scratch out ideas we typically use http://websequencediagrams.com these let
us build quick models for software projects. Thanks WSD you guys are awesome.

Remote Key Wrapping
-------------------
An interesting alternative to local wrapping might be remote wrapping. In this
model a server would transmit a public key to Leeson along with the request for
a key. Leeson would encrypt the requested volume encryption key with the
provided public key.

![Remote PubKey Wrapping](https://raw.githubusercontent.com/hyakuhei/Leeson/master/docs/cert_wrapping.png)

# TPM usage
There are a number of options available for using the TPM with Leeson. The
Leeson threat model excludes using system measurements for locally deriving
encryption keys because in the event that an entire system chasis is stolen
the data at rest is not protected. However, there are ways that we can use the
TPM to enhance the security that Leeson can offer as a network bound crypto-key
delivery system.

Local Key Wrapping
------------------
Once a host has created a data encryption key (DEK) for a volume to be
encrypted it would normally send it to the Leeson server for archival. However
it could alternatively wrap this DEK using a key encryption key. The TPM is an
ideal way to do this, it can create and store a small symmetric encryption key
which would be used to encrypt the DEK before sending it to the Leeson server.

Using key-wrapping in this way (and using the TPM for it particularly)
enhances the security of the Leeson scheme significantly. The result is that
if the Leeson server is somehow compelled to give up encryption keys (because
it has a vulnerability or a malicious admin etc) those encryption keys would be
useless to an attacker without access to the TPM in the server that created
the encryption keys.

In reality this would protect individual drives very well but key wrapping
doesn't provide significantly enhanced protections in the event an entire
chassis is in the possession of an attacker, which is one threat that is
considered in our threat model. However, this doesn't mean we shouldn't enable
key wrapping, it's just important to realize what protection it provides: Key
wrapping is a great way to protect individual volumes when an attacker may also
have some level of network access but it does not enhance security for entire
chassis.

Entropy
-------
Servers using Leeson for storing key material will typically generate the
encryption keys locally and transmit them to Leeson. The potential problem here
is that a freshly PXE booted server may have very poor entropy (randomness)
available. This means that an attacker may be able to more easily guess the key
material that was used to protect encrypted drives.

The TPM (if present) could be used as a better source of Pseudo Randomness:
http://cryptotronix.com/2014/08/28/tpm-rng/

Attestation
-----------
We are very interested in how we might be able to use attestation as an
authentication factor for Leeson. The general idea is that Leeson might
maintain mappings between server Attestation Certificates and UUIDs.

It may also be possible to perform this using the manufacturer certificate (EC)
more investigation is required.

Registration and Private Certificate Authority
----------------------------------------------
![PCA registration](https://raw.githubusercontent.com/hyakuhei/Leeson/master/docs/tpm_registration.png)

TBC
