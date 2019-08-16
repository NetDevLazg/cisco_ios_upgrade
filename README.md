# cisco_ios_upgrade

 This is a simple pack that allows users to transfer files from a folder inside /opt/stackstorm/files_repo/ to a cisco device and then easily perform an IOS upgrade or ROM MON upgradeon the device.

1. First this is to install the pack using "st2 pack install", after that is complete you will need to create a folder called files_repo in the directory /opt/stackstorm/ to store ios images and rom mon packages.

2. After you create the folder files_repo create two new folder inside and called them ios_repo and rom_mon_repo.

3. Store ios images insides ios_repo and rom_mon packages inside rom_mon_repo.

