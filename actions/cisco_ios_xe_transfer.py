import paramiko
from scp import SCPClient
import sys
import time
from st2common.runners.base_action import Action

    

class cisco_ios_xe_transfer(Action):

    def run(self,IP,USERNAME,PASSWORD,IOS_IMAGE,IOS_MD5_CHECKSUM):
        """
        This function is used by stack storm to run the code and based
        on the return code see if is successful or if it failed.
        """

        ios_image = '/opt/stackstorm/files_repo/ios_repo/{}'.format(IOS_IMAGE)
        md5_checksum = IOS_MD5_CHECKSUM
        
        ssh_client=paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=IP,username=USERNAME,password=PASSWORD)
            
        
        print("-----------------------------------------------")
        print("---------Starting IOS Image Transfer-----------")
        print("-----------------------------------------------")
        print("-----------------------------------------------")
        print("----------File Transfer in Progress------------")
        print("-----------------------------------------------")
        
        starting_time = time.time()
        scp = SCPClient(ssh_client.get_transport())
        
        scp.put(ios_image, 'bootflash:/{}'.format(IOS_IMAGE))
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
ios_image = "{}"
md5_checksum = "{}"
'''
        
        with open('/opt/stackstorm/packs/st2_ios_upgrades/actions/ios_xe_varibales.py', 'w') as f:
            f.write(variables.format(IP,IOS_IMAGE,IOS_MD5_CHECKSUM))
        
        print("-----------------------------------------------")
        print("-----------Variable File Created---------------")
        print("-----------------------------------------------")
        print("-----You can now run the other script----------")
        print("-----------------------------------------------")

        return True, "Script ran without error and file is now on target device."