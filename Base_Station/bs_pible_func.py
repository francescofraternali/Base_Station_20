import subprocess
import os
from time import sleep
import datetime
import json

def initialization():
    ID_List = []; Name_List = []; File_List = []
    Name_spl = []; File_spl = []

    with open("../ID/ID.txt", "r") as f:
        for line in f:
            splitted = line.split(',')
            print(splitted)
            Name_spl.append(splitted[0])
            File_spl.append(splitted[1])

    if len(Name_spl) == len(File_spl):
        print("ID File Ok")
    else:
        print("Error: Check ID File")
        quit()

    dict_dev = {}

    with open('pible_dev_list.txt', 'r') as inf:
        for data in inf:
            line = data.strip().split(' ')
            dict_dev[line[0]] = line[1]

    for i in range(len(File_spl)):
        checker = 1
        for key, val in dict_dev.items():
            if Name_spl[i] == val:
                ID_List.append(key)
                checker = 0
                break
        if checker == 1:
            print('Huston we have a problem, sensor not found! Try updating device List!')
            quit()
        Name_List.append(str(Name_spl[i])) #["Sensor_5", "Sensor_1"]
        File_List.append('../Data/' + str(File_spl[i])) #["2142_Middle_Battery.txt", "2142_Middle_Pible.txt"]

    return ID_List, Name_List, File_List

def file_valid(ID, ID_List, Name_List, File_List):
    for i in range(len(ID_List)):
        if ID == ID_List[i]:
            Name = Name_List[i]
            File = File_List[i]
            break
    #print(Name)
    #print("../ID/" + Name + "_action.json")
    if os.path.exists("../ID/" + Name + "_action.json"):
        #print("here out")
        temp_sec = os.path.getmtime("../ID/" + Name + '_action.json')
        if temp_sec < 60*60*6: # 6 hours
            #print("here")
            return True

    return False


def heuristic_energy_manag(ID, ID_List, Name_List, File_List):
    for i in range(len(ID_List)):
        if ID == ID_List[i]:
            Name = Name_List[i]
            File = File_List[i]
            break

    with open('../ID/ID.txt', 'r') as f:
        found = 0
        for line in f:
            line = line.strip()
            splt = line.split(',')
            if Name == splt[0]:
                Action_3 = splt[4]
                Action_3_orig = Action_3
                exist = os.path.isfile("../Data/"+splt[1])
                if Action_3 == '-1':
                    Action_1 = '3C'; Action_2 = '01'; found = 1
                elif exist:
                    for line in reversed(list(open("../Data/"+splt[1]))):
                        line_splt = line.split('|')
                        try:
                            volt = int(line_splt[5])
                        except:
                            #print("line: ", line , ". volt string: ", volt_str, ". Problem, check")
                            volt = 0

                        if volt >= 90:
                            Action_1 = 'BC'; Action_2 = '0B';
                        elif volt >= 75 and volt < 90:
                            Action_1 = 'BC'; Action_2 = '09';
                        elif volt >= 65 and volt < 75:
                            Action_1 = '3C'; Action_2 = '03';
                        else:
                            Action_1 = '3C'; Action_2 = '01'; Action_3 = '-1'
                        if volt > 0:
                            found = 1
                            #print("final line: ", line)
                            break

                if found == 0: # it should not get here. Put the maximum availble so it will talk sooner with the BS and tell what to do
                    print("No valid voltage found, either a new file, always 0 or a problem")
                    Action_1 = 'BC'; Action_2 = '0B'; volt = 0

                file_splt = splt[1].split('_') # for Battery sensors let's leave all On
                if 'Batt' in file_splt or 'BattEH' in file_splt:
                    Action_1 = 'BC'; Action_2 = '0B'; Action_3 = Action_3_orig
                    #print(Name, Action_1, Action_2)
                break
    #print(Name, volt, Action_1, Action_2, Action_3)

    return (Action_1, Action_2, Action_3, Name, File)


def get_actions(ID, ID_List, Name_List, File_List):
    for i in range(len(ID_List)):
        if ID == ID_List[i]:
            Name = Name_List[i]
            File = File_List[i]
            break

    with open("../ID/" + Name + "_action.json") as f:
        actions = json.load(f)

        Action_1 = actions["Action_1"]
        Action_2 = actions["Action_2"]
        Action_3 = actions["Action_3"]

    return Action_1, Action_2, Action_3, Name, File



def check_reboot(last_reset):
    #proc = subprocess.Popen("cat /var/log/auth.log | grep 'Accepted password' > Accepted_file.txt", stdout=subprocess.PIPE, shell=True)
    proc = subprocess.Popen("cat /var/log/auth.log | grep 'Accepted password'", stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()

    now = datetime.datetime.now()
    #for line in reversed(open('Accepted_file.txt').readlines()):
    content = out.split('\n')
    for line in reversed(content):
        spl = line.rstrip()
        spl = spl.split(' ')
        if len(spl) > 1:
            #print(spl[1])
            if 'Accepted' in spl:
                if spl[1].isdigit():
                    index = 1
                else:
                    index = 2
                break

                #print(spl)
                day = spl[index]
                clock = spl[index+1].split(':')

                now_time = now.strftime('%m/%d/%y %H:%M:%S')

                month = datetime.datetime.strptime(spl[0], '%b')
                last_bs_read_time = datetime.datetime(int(now.year), int(month.month), int(day), int(clock[0]), int(clock[1]), int(clock[2]))
        else:
            last_bs_read_time = now

    #diff_1 = (now - last_bs_read_time).total_seconds()
    diff_1 = 0
    diff_2 = (now - last_reset).total_seconds()
    action_imposed = -1

    print("checking reboot: ", str(int(diff_1)) + "/3600, " + str(int(diff_2)) + "/86400")
    if diff_1 > 60*60*1:  # if nobody is reading into the BS for diff_1 time then I put all actions to 0 to avoid node dying
        action_imposed = 0
        print("action imposed to 0 since bs in not reading data")
    if diff_2 > 60*60*24:  # if nobody is writing for diff_1 time and the BS was On for one day, then reboot
        print("Nobody wants me. Or maybe I am broken? Reeboting...")
        subprocess.Popen("sudo reboot", shell=True)

    return action_imposed


def check_file_size_to_delete(file):
    if os.path.exists(file):
        size = os.path.getsize(file)
        #print(size)
        if size > 20000000:
            os.remove(file)


def kill_search():
    subprocess.Popen("killall Find_New_BLE_Device.sh 2>/dev/null", shell=True) 

def killer():
    subprocess.Popen("killall Detector.sh 2>/dev/null", shell=True)
    subprocess.Popen("killall gatttool 2>/dev/null" , shell=True)

def check():
    for ii in range(0,tryals):
        with open('wait.txt', 'r') as f:
            first_line = f.readline()
        first = first_line[:1]
        #print(first)
        if first == '2': # if it reads 2 that means that Detector.sh has already written everything
            #print "Sleep 1"
            sleep(write_completed)
            return
        if first == '1': #if it reads 1 it we five him other 10 extra seconds to finish to write the data
            for i in range(0,10):
                #print('here')
                with open('wait.txt', 'r') as f:
                    first_line = f.readline()

                first = first_line[:1]
                if first == '2':
                    sleep(write_completed)
                    return
                sleep(0.5)
        sleep(0.5)

def get_raw_data(ID):
    with open('wait.txt', 'w') as f:
        f.write('0')
        sleep(0.1)

    for i in range(len(ID_List)):
        if ID == ID_List[i]:
            Name = Name_List[i]
            File = File_List[i]
            break

    with open('ID.txt', 'r') as f:
        Action_1 = '-1'
        for line in f:
            line = line.strip()
            splt = line.split(',')
            if Name == splt[0]:
                #print(splt[0], splt[2])
                Action_1 = splt[2]
                break

        if Action_1 == '-1':
            print("Pay Attention: Name and Action not found")
            #Action = '51'

    #print("bash get_data_from_device.sh "+Name+" "+ID+" "+File+" "+Action)
    subprocess.Popen("bash get_data_from_device.sh "+Name+" "+ID+" "+File+" "+Action+" &", shell=True)

    #subprocess.Popen('bash get_data_from_device.sh ' +Name+' '+ID+' '+File+' '+Action+' &', shell=True)
    #print('checking')
    check()
    #print('checking over')
    killer()
    sleep(0.5)
