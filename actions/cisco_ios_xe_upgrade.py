from netmiko import ConnectHandler
from getpass import getpass
from netmiko.ssh_exception import NetMikoTimeoutException
from paramiko.ssh_exception import SSHException
from netmiko.ssh_exception import AuthenticationException
from ios_xe_varibales import hostip
from ios_xe_varibales import ios_image
from ios_xe_varibales import md5_checksum
import os
import time
import subprocess
import sys

""" 
Prompts the user for his username and Password, if the users hits enter 
by mistakes and does not type anything the while loop will prompt again for 
the username until he enters something, the same thing happens for the password.
 """

print("What is your Username:")
username = input()
while username == '':
    print("What is your Username:")
    username = input()

print("What is your Password:")
password = getpass()
while password == '':
    print("What is your Password:")
    password = getpass()
print(" ")



"""
Setting the device values for netmiko to connect to the device.
"""
device_profile = {
        'device_type' : 'cisco_ios',
        'ip' : hostip,
        'username': username,
        'password': password,
    }

"""
Handles connections errors and gives a friendly error message.
"""
try:
    net_connect = ConnectHandler(**device_profile)
except (AuthenticationException):
    print ("Authentication failure " + hostip)
except (NetMikoTimeoutException):
    print (' Timeout to device ' + hostip)
except (EOFError):
    print (' End of file while attempting device ' + hostip)
except (SSHException):
    print ('SSH issue. Are you sure SSH is enable ' + hostip)
except Exception as unknown_error:
    print (' Some other Error:' + unknown_error)

"""
Funcion below is to grab the current ROM-MON version of the device
and slice it to match the version code.
"""
def rom_mon_ver():
    rom_mon_ver = net_connect.send_command('sh rom-monitor R0 | in Version')
    rom_mon_ver_updated = rom_mon_ver.split(' ')[3][3]
    return int(rom_mon_ver_updated)

router_rom_mon_version = rom_mon_ver()
router_image_revision = int(ios_image.split('.')[2])

print("-------------------------------------------------")
print('Checking ROM-MON Version - Please Wait')
print("-------------------------------------------------")


if router_rom_mon_version < router_image_revision:
    print("-------------------------------------------------")
    print('Router version is HIGHER than ROM-MON Version')
    print('Please upgrade the ROM-MON before doing the OS Upgrade')
    print("-------------------------------------------------")
    exit()
else:
    print("-------------------------------------------------")
    print('Router Version is lower or equal to ROM-MON Version')
    print('Proceeding with the IOS Upgrade')    
    print("-------------------------------------------------")

print("-------------------------------------------------")
print('Checking MD5 Checksum - Please Wait')
print("-------------------------------------------------")
"""
Connects to the device via netmiko and run the command "verify /md5 bootflash:" and the ios image provided
"""
checking_md5 = net_connect.send_command('verify /md5 bootflash:{}'.format(ios_image))

"""
Check the current boot system for the device and sabes that as a varibale called "a"
then we split the string where it says bin.
"""
check_boot_system = net_connect.send_command('sh run | in boot system')
a = check_boot_system.split("bin")

"""
config template to configure the new boot variable with the new image as primary 
and the old image as a backup
"""
configs_change_boot = [
    'boot system bootflash:/{}'.format(ios_image),
    '{}bin'.format(a[0]),
    'exit',
    'wr',
]

"""
Perform MD5 Checksum match with the value provided when the image was transfer.
If the MD5 checksum matches it will clear the boot variables and configure the 
new boot template on the device, if the MD5 checksum does not match the sript will cancel himself
"""
if md5_checksum in checking_md5:
    print("-------------------------------------------------")
    print("MD5 Checksum Matched")
    print("-------------------------------------------------")
    print("Cleaning Boot Configurations")
    clearning_boot = net_connect.send_config_set('no boot system')
    print("-------------------------------------------------")
    print("Changing Boot Variable")
    print("-------------------------------------------------")
    boot_varaible_change = net_connect.send_config_set(configs_change_boot)
    print(boot_varaible_change)
else:
    print("-------------------------------------------------")
    print("ERROR MD5 CODE DOES NOT MATCH")
    print("-------------------------------------------------")
    exit()
"""
Checks that the device boot varibale has the new image, if is true it will say
that the change was done successfully. If the new image is not found on the boot variable
the script will cancel himself.
"""
print("-------------------------------------------------")
print("Checking boot varibale once more")
print("-------------------------------------------------")

boot_variable = net_connect.send_command('show bootvar')
print("-------------------------------------------------")
print(boot_variable)
print("-------------------------------------------------")

time.sleep(2)

if ios_image in boot_variable:
    print("-------------------------------------------------")
    print("The boot Varibale was changed successfully")
    print("-------------------------------------------------")
    time.sleep(2)
else:
    print("-------------------------------------------------")
    print("Boot Varibale was not changed")
    print("-------------------------------------------------")
    exit()

"""
Prompts if you want to continue with the reboot or not, if you press 1 it will continue
and we if you press 2 it will cancel the script.
"""
print("-------------------------------------------------")
print('Do you want to proceed and reboot the device?')
print('       Press 1 for Yes | Press 2 for NO '        )
print("-------------------------------------------------")
awnser = input()

if awnser == '1':
    print("-------------------------------------------------")
    print("Rebooting Device Now")
    print("-------------------------------------------------")
else:
    print("-------------------------------------------------")
    print('Breaking Script')
    print("-------------------------------------------------")
    exit()

"""
Reboots the router
"""
reboot = net_connect.send_command_timing('reload')

if "System configuration has been modified. Save? [yes/no]" in reboot:
    reboot += net_connect.send_command_timing("yes\n")

if "Proceed with reload" in reboot:
    reboot += net_connect.send_command_timing("\n")



time.sleep(30)

proc = subprocess.Popen(
    ['ping', '-q', '-c', '3', hostip],
    stdout=subprocess.DEVNULL)
proc.wait()


animation = "|/-\\"
idx = 0
"""
This is a loop that sends ping to the device and if it does not reply it will continue to send pings to the 
device, there is a animation configured so while we wait for the device to comeback the scripts looks like is loading,
once the device is backup the loop will end and the script will print that the device is back up.
"""
while proc.returncode != 0:
    proc = subprocess.Popen(
    ['ping', '-q', '-c', '1', hostip],
    stdout=subprocess.DEVNULL)
    proc.wait()
    print("Waitting for Device to Return: ", animation[idx % len(animation)], end="\r")
    idx += 1
else:
    sys.stdout.flush()
    print("-------------------------------------------------")
    print("Device is now up")
    print("-------------------------------------------------")

print("-------------------------------------------------")
print("Checking if IOS Upgrade was successful")
print("-------------------------------------------------")

time.sleep(10)
"""
initiates a new session to the device to check if the update was done.
"""
try:
    net_connect = ConnectHandler(**device_profile)
except (AuthenticationException):
    print ("Authentication failure " + hostip)
except (NetMikoTimeoutException):
    print (' Timeout to device ' + hostip)
except (EOFError):
    print (' End of file while attempting device ' + hostip)
except (SSHException):
    print ('SSH issue. Are you sure SSH is enable ' + hostip)
except Exception as unknown_error:
    print (' Some other Error:' + unknown_error)

"""
goes tot he device and runs a show version and saves that as a variable
"""
device_ver = net_connect.send_command('sh ver')
"""
if the new ios image is on the show version the script will consider the upgrade successful
"""
if ios_image in device_ver:
    print("-------------------------------------------------")
    print("IOS UPGRADE WAS SUCCESSFUL - COMPLETE")
    print("-------------------------------------------------")
else:
    print("-------------------------------------------------")
    print("IOS UPGRADE FAILED")
    print("-------------------------------------------------")
