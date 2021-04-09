# Autorun
Execute scripts when connecting external drives (USB / eSATA) on a Synology NAS. Script on the external drive needs to be owned by the root user and should be made executable.

## Install
Download autorun-1.8.spk from the releases and install via Manual Install in the Synology Package Center.

## Script Fingerprint Validation
Optional: for additional security only known scripts can be allowed to run. Setup as follows. Before installing autorun, make an empty text file, e.g. at /volume1/Admin/Autorun/known_scripts. During installation of autorun, paste the path to this file when asked for the path to 'known_scripts'. Also enable notifications for ease of use. Attach your external drive with your autorun script. You'll get an error (only if you enabled notifications) in the Notifications area in DSM, indicating that the fingerprint for this script can't be found inside your 'known_scripts' file. Copy the fingerprint from the notifications area inside your 'known_scripts' file. Alternatively manually generate a sha256 checksum for your script and paste this fingerprint inside the 'known_scripts' file. One fingerprint per line. Each line must have just the fingerprint and no additional characters (including spaces) in front or behind it. To deny a script from running in the future, remove the hash from 'known_scripts' or put for example a # character in front of the fingerprint.

```
### Sample contents of the 'known_scripts' text file

# Hash for test script on 16GB test USB stick
7f65da607d535abd1302422b06604b76a960c24ec231a75fb1dad3d548390ac9

# Skipping example: the # in front of the hash will ensure this fingerprint will be skipped
#0c9889cce6ef978ca676ed4c653a5f151b723de5e4b8c8a3c60ed9091d1b0191
```

## Hyper Backup + Integrity Check with Email Notifications
Put [this script](https://gist.github.com/Jip-Hop/b9ddb2cc124302a5558659e1298c36ec) on your external drive to automatically trigger a Hyper Backup, immediately run an integrity check afterwards and receive the corresponding log entries via email. For me the actual backup completes quickly, but the integrity check can take quite long. So I recommend to leave it running overnight. Read the comments inside the script to learn how to configure it.

## Build
Should run on any *nix box / subsystem.

* adjust the version number in INFO and build
* `./build`
* publish the created .spk
