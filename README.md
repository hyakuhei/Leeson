# Leeson
Key broker for FDE with off-system key storage

# Development Note
This software is a proof of concept for a method to simply bind cryptographic
key material to the local network.

To understand what we are considering for the future development of Anchor,
which authentication factors we are looking to add and how the TPM might be
used please view ![the documentation](https://github.com/hyakuhei/Leeson/tree/master/docs)

# Leeson server
First, setup the database. Running the dbmodel.py script without any arguments
will cause it to create a database schema and populate it with some test data
with some servers and volume keys.
```
cd PecanBroker/database
python dbmodel.py
```

Setup the key broker in developer mode
--------------------------------------
```
python ./setup.py develop
```

Run the key broker
------------------
```
cd PecanBroker
pecan serve config.py
```

Registration Mode
-----------------
In registration mode the broker will insert keys into it's database when it
receives a POST request with appropriate data:

| field | value |
| ----- | ----- |
| addr  | The IP address of the server to add a volume key for. If this server is not known in the database it will be created |
| uuid | The UUID of the volume |
| keymat | The key used for cryptographic operations on said volume |
| registrationkey | The key that enables registration API usage |

To set registration mode the config.py file must be modified and the
"registrationmode" configuration item be set to True. Note that you should also
change the registrationkey configuration in config.py

```
...
app = {
    ...
    'registrationmode':True,
    'registrationkey':'aabbccddeeff',
    ...
}
...
```


# Leeson Client
NOTE: There is a bug in Ubuntu startup scripts that mean we dont get our leeson
IP passed through properly :-( in the script given below you have to manually
set the `leeson` variable to the server IP.

Making it work
--------------
To use Leeson, first setup and install a normal Ubuntu server and when asked,
pick to use an encrypted LVM. Give the LVM some passphrase and remember it for
later. Boot the machine. Once booted we need to make some modifications. First
add the Leeson client script by editing `/usr/local/sbin/leeson.sh` and add the
following:
```
leeson=${1}
echo "Leeson unlock..." >&2

uuid=$(ls -l /dev/disk/by-uuid/ | grep sda1 | cut -d' ' -f14)
echo "Disk is $uuid" >&2


key=$(curl -m 8 -k https://${leeson}/key?uuid=${uuid})
if [ -z "${key}" ]; then
  echo "No response from Leeson, falling back" >&2
  if [ -x /bin/plymouth ] && plymouth --ping; then
    plymouth ask-for-password --prompt "Enter passphrase"
  else
    /lib/cryptsetup/askpass "Enter passphrase"
  fi
fi
echo "Moving on." >&2
echo -en $key
```

Next, install 'dropbear' a simple ssh client `apt-get install dropbear` (this is
just needed to make networking come up with an IP etc, a better solution should
be found). Next we need a custom hook to install the curl utility into the
initrd. So edit `/usr/share/initramfs-tools/hooks/curl` and add:

```
#!/bin/sh -e
PREREQS="udev"
case $1 in
        prereqs) echo "${PREREQS}"; exit 0;;
esac
. /usr/share/initramfs-tools/hook-functions
copy_exec /usr/bin/curl /bin
```

The perquisite on udev is needed to make sure the UUIDs of disks are available
for the Leeson client script to read.

Now we need to configure things to use our scripts. First edit `/etc/cryptab`
it should look something like this:
```
sda5_crypt UUID=ef29ed41-ad41-4a6b-b8f3-aa8474af8cc2 none luks,discard
```
The UUID of the disk and the device name are unlikely to be the same, but that's
OK. Edit it to look like the following, using your correct UUID and dev name.

```
sda5_crypt UUID=ef29ed41-ad41-4a6b-b8f3-aa8474af8cc2 none luks,discard,keyscript=/usr/local/sbin/leeson.sh
```

Finally, setup the initial parameters to pass through to the various bits in our
initrd. To do this, edit `/etc/defualt/grub` and add to the
`GRUB_CMDLINE_LINUX_DEFAULT` line as follows:

```
GRUB_CMDLINE_LINUX_DEFAULT="ip=192.168.1.100::192.168.1.1:255.255.255.0:decrypt:eth0:off cryptkey=192.168.1.7"
```

The first section, starting 'ip' configures the dropbear stuff to setup a static
ip for the machine. The second section starting 'cryptkey' is a parameter that
will be passed through to the Lesson client script and tell us where the server
is. You can set this stuff as kernel params during boot, or in the grub menu if
you need to as well (PXE boot etc). Now update and grub and build our initrd by
running the following commands

```
update-grub2
update-initramfs -c -k `uname -r`
```

This will build a new initrd for the running Kernel, if a new kernel is installed,
or something else wants to mess with the initrd its all OK, our stuff will be
added correctly in the new one.

Reboot and enjoy. If Leeson server is not found then you will be prompted to
enter the unlock manually.

#Next Steps
TPM Support
-----------
There are a number of smart things that we might be able to do with a TPM to
enhance the level of assurance we can have that a host is who it claims to be.
One interesting prospect is to use the TPM to provide some system measurements or
attestation to Leeson to guarantee the identity of the host generating the
originating request.
Project Deo
-----------
We recently became aware of 'deo' a RedHat effort that similarly binds crypto to
the network but has some interesting enhancements based on Elgamal encryption methods
We intend to reach out and research this further in the near future to work out
how/if we can/should contribute to this project, combine projects etc.
* https://blog-ftweedal.rhcloud.com/2015/09/automatic-decryption-of-tls-private-keys-with-deo/
* http://www.snia.org/sites/default/files/SDC15_presentations/security/NathanielMcCallum_Network_Bound_Encryption.pdf
