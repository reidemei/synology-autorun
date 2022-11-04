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


# build
Should run on any *nix box / subsystem.

* adjust the version number in INFO and build
* `./build`
* publish the created .spk

*Note that almost all of the UI is currently not included in the build (since I got bored of updating that with more or less every DSM version).*


# contributions

I will not accept any feature requests. This project has no priority anymore so I will only do the minimum to keep the base functionality working with newer DSM versions. Feel free to fork and provide your own versions.
