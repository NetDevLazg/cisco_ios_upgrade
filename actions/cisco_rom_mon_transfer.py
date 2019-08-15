import paramiko
from scp import SCPClient
import sys
import time
from st2common.runners.base_action import Action

    

class cisco_rom_mon_transer(Action):

    def run(self,IP,USERNAME,PASSWORD,ROM_MON_IMAGE,ROM_MON_MD5_CHECKSUM):
        """
        This function is used by stack storm to run the code and based
        on the return code see if is successful or if it failed.
        """

        rom_mon_image = '/opt/stackstorm/files_repo/rom_mon_repo/{}'.format(ROM_MON_IMAGE)
        md5_checksum = ROM_MON_MD5_CHECKSUM
        
        ssh_client=paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=IP,username=USERNAME,password=PASSWORD)
        
        
        def progress4(filename, size, sent, peername):
            print("(%s:%s) %s\'s progress: %.2f%%   \r" % (peername[0], peername[1], filename, float(sent)/float(size)*100) )
        
        
        print("-----------------------------------------------")
        print("---------Starting IOS Image Transfer-----------")
        print("-----------------------------------------------")
        
        starting_time = time.time()
        scp = SCPClient(ssh_client.get_transport(), progress4=progress4)
        
        scp.put(rom_mon_image, 'bootflash:/{}'.format(ROM_MON_IMAGE))
        print(" ")
        print('Script took ',int(time.time()-starting_time), 'Seconds')
        print(" ")
        print("-----------------------------------------------")
        print("------------Transfer Completed-----------------")
        print("-----------------------------------------------")
        scp.close()
        
        print(" ")
        print(" ")
        print("-----------------------------------------------")
        print("-----------Creating Variable File--------------")
        print("-----------------------------------------------")
        time.sleep(5)
        
        variables = '''
#------------------------------------------------#
# Below are the variables for the ROM-MON Upgrade
#------------------------------------------------#
        
hostip = "{}"
rom_image = "{}"
md5_checksum = "{}"
'''
        
        with open('/opt/stackstorm/packs/st2_ios_upgrades/actions/rom_mon_varibales.py', 'w') as f:
            f.write(variables.format(IP,ROM_MON_IMAGE,ROM_MON_MD5_CHECKSUM))
        
        print("-----------------------------------------------")
        print("-----------Variable File Created---------------")
        print("-----------------------------------------------")
        print("-----You can now run the other script----------")
        print("-----------------------------------------------")

        return True, "Script ran without error and file is now on target device."