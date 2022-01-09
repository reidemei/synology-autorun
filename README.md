# autorun
Execute scripts when connecting external drives (USB / eSATA) on a Synology NAS.


# install
Add https://www.cphub.net/ in the Package Center (current DSM only) or manually install one from the releases (for older DSM):

* DSM 7: 1.8
* DSM 6: 1.7
* DSM 5: 1.6
* older: 1.3

Third Party packages are restricted by Synology in DSM 7. Since autorun does require root 
permission to perform its job an additional manual step is required after the installation.

SSH to your NAS (as an admin user) and execute the following command:

```shell
sudo cp /var/packages/autorun/conf/privilege.root /var/packages/autorun/conf/privilege
```

# security considerations
Everybody with physical access to your Disc Station is able to execute any command as root by
plugging in a USB-Stick with an 'autorun' script. If this is an issue for you, there will be two options:

(1) set a different name for the autorun script (via installation wizard or by changing ``SCRIPT`` setting in file ``/var/packages/autorun/target/config``)

(2) set a key which must be present on the device in file ``/key`` (via installation wizard or by changing ``KEY`` setting in file ``/var/packages/autorun/target/config``)

# build
Should run on any *nix box / subsystem.

* adjust the version number in INFO and build
* `./build`
* publish the created .spk

*Note that almost all of the UI is currently not included in the build (since I got bored of updating that with more or less every DSM version).*
