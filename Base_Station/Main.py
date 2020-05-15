import sys
import subprocess
from time import sleep
import json
import os
import datetime
from subprocess import PIPE
from bs_pible_func import *

ID_List, Name_List, File_List = initialization()

#print(ID_List)
#print(Name_List)
#print(File_List)

#finder_time = 3 # time needed to avoid that multiple process are called and not completly killed. Put 3 for one sensor and 1 for several sensors
write_completed = 1 # after you write a data you avoid to call the sensor again.
tryals = 5 #number of trials it looks for a specific device. Each try is 0.5s.



print("Let us Start!!")
last_reset = datetime.datetime.now()

#Reset BLE drivers
#subprocess.Popen("sudo hciconfig hci0 reset &", shell=True)
#print(json.dumps(dict_dev, indent=1, sort_keys=True))

avoid = []  # in this list there are all the devices that have been read and that needs to be left alone for a bit to avoid to get the data read twice.
countarell = 360
count_empty = 0
action_imposed = -1
detector_error = 0

while(True):
    Name = ''
    File = ''
    #print("scanning")
    try:
    	os.remove('dev_found.txt')
    except:
        pass
    #subprocess.Popen("bash Find_New_BLE_Device.sh > dev_found.txt", shell=True)
    subprocess.Popen('sudo blescan -t 3 > dev_found.txt 2> ble_err.txt', shell=True)  #sometimes this could stuck in this loop so let's write down the file
    sleep(3.5)
    found = []
    if (os.stat('dev_found.txt').st_size < 2) or (os.stat('ble_err.txt').st_size > 1) or detector_error > 2:
        print('dev_found empty or blescan error')
        print("dev_found size: ", os.stat('dev_found.txt').st_size)
        print('blescan stderr file dimension: ', os.stat('ble_err.txt').st_size)
        print("detector_error: ", detector_error, " count_empty: ", count_empty)
        sleep(5)
        if count_empty >= 5 or detector_error > 2:
            print('List Empty. No devices found or detector_error positive for a while. Rebooting BS.')
            subprocess.Popen('sudo reboot', shell=True)
        else:
            print('something wrong? Resetting BLE hci0 adapter')
            subprocess.Popen('sudo hciconfig hci0 reset', shell=True)
            sleep(5)
            count_empty += 1

    else: # some devices were found
        count_empty = 0
        with open("dev_found.txt", 'r') as f:
            for line in f:
                line = line.strip()
                #print(len(line))
                splitted = line.split(' ')
                try:
                    ID = splitted[2][5:22]
                except:
                    ID = 'Not_found'
                if ID in ID_List and ID not in avoid and ID not in found:
                        #print('found')
                        found.append(ID)
                        #Action_1, Action_2, Action_3, Name, File = get_action_name(ID)
                        if file_valid(ID, ID_List, Name_List, File_List):
                            Action_1, Action_2, Action_3, Name, File = get_RL_actions(ID, ID_List, Name_List, File_List)
                            #print("selecting RL action")
                        else:
			    Action_1, Action_2, Action_3, Name, File = heuristic_energy_manag(ID, ID_List, Name_List, File_List)

                        log_temp = File.split('/')
                        log = log_temp[-1]

                        #t = time.strftime('%m/%d/%y %H:%M:%S')

                        #if action_imposed == 0:
                        #    Action_1 = '3C'
			#    Action_2 = '01'
			#    Action_3 = '-1'

                        #Action = "00000000"

                        #proc = subprocess.Popen("bash Detector.sh " + Name + " " + ID + " " + File + " " + Action_1 + " " + Action_2 + " " + Action_3 + " " + log + " 2>error.txt &", stdout=subprocess.PIPE, shell=True)
                        proc = subprocess.Popen("bash Detector.sh " + Name + " " + ID + " " + File + " " + Action_1 + " " + Action_2 + " " + Action_3 + " " + log + " &", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                        (out, err) = proc.communicate()

                        if err != '':
                            print("err ", err)
                            err_strip = err.strip()
                            err_split = err_strip.split(' ')
                            if '(38)' in err_split:
                                detector_error += 5

                        toprint = out.split('\n')
                        print(toprint[0])
                        splitt = toprint[0].split('|')
                        error = 'list index out of range'
                        if splitt[2] == error or splitt[4] == error or splitt[10] == error:
                                     #print("error detected")
                                     #contain = line.strip().split(' ')
                                #if (len(line.strip()) > 0) and '(107)' not in contain and '(111)' not in contain and 'unlikely' not in contain and 'Traceback' not in contain: # and '(38)' not in contain 
                                     detector_error += 1
                                     print('something wrong, detector_error: ', detector_error)
                                     sleep(12)
                                     if detector_error > 1: # otherwise let's put 2
                                         subprocess.Popen('sudo hciconfig hci0 reset', shell=True)
                                         print('something wrong, resetting')
                                         sleep(5)
                                     break
                        else:
                            if detector_error > 0:
                                print("reset detector_error")
                            	detector_error -= 1

    #print("found", found)
    if len(avoid) > 0:
        #print('remove avoiding last ID')
        for ID in ID_List:
            if ID in avoid:
                avoid.remove(ID)
                #print('removing ', ID)

    if len(found) > 0:   # There are some device that needs to be downloaded
        for ID in found:
            avoid.append(ID)
            avoid.append(ID)
            avoid.append(ID)
            #avoid.append(ID)
            #print('avoiding ', ID)

    sleep(1)
    # reboot BS in case
    countarell += 1
    if countarell >= 360: # Use 360 as default that is 60*30/5 sec
        action_imposed = check_reboot(last_reset)
        check_file_size_to_delete("screenlog.0")

        countarell = 0
        sleep(1)

print("It's Over")

#sudo hciconfig hci0 reset

#B0:B4:48:C9:EA:83
#gatttool -b $Sensor --char-write-req -a 0x0024 -n 00

#subprocess.Popen("gatttool -b B0:B4:48:C9:EA:83 --char-write-req -a 0x0024 -n 00")
