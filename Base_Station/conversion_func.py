#!/usr/bin/python
import sys
import struct

def info_conversion():
    #try:
        raw_data = sys.argv[2]	# Start with raw data from SensorTag
        raw_bytes = raw_data.split() # Split into individual bytes
        batt_percent = int(raw_bytes[2], 16)
        PIR_reed = int(raw_bytes[3], 16)

        if PIR_reed == 0:
            PIR_Out = 0; reed = 0
        elif PIR_reed == 1:
            PIR_Out = 1; reed = 0
        elif PIR_reed == 2:
            PIR_Out = 0; reed = 1
        elif PIR_reed == 3:
            PIR_Out = 1; reed = 1
        else:
            print("error PIR/Reed")
        light_2 = int(raw_bytes[0], 16)
        light_1 = int(raw_bytes[1], 16)
        light = (light_1 << 8) | (light_2);
        #light = light*4  # if you use an external case
        light = light
        print(str(int(0))+"|"+str(batt_percent)+"|"+str(PIR_Out)+"|"+str(reed)+"|"+str(light)+"|perf-batt-PIR-reed-light")
    #except Exception as e: print(e)

def hum_conversion():
    #try:
        raw_hum_data = sys.argv[2]
        raw_hum_bytes = raw_hum_data.split()

        rawT_1 = int(raw_hum_bytes[1], 16)
        rawT_2 = int(raw_hum_bytes[0], 16)
        rawT = (rawT_1 << 8) | (rawT_2)

        rawH_1 = int(raw_hum_bytes[3], 16)
        rawH_2 = int(raw_hum_bytes[2], 16)
        rawH = (rawH_1 << 8) | (rawH_2)

        temp = -40.0 + 165.0 * (rawT / 65536.0)
        #print(rawT, temp)
        RH = 100.0 * (rawH / 65536.0)

        print(str(round(temp, 2)) + "|" + str(round(RH, 2)))
    #except Exception as e: print(e)

def bar_conversion():
    #try:
        raw_data = sys.argv[2] # Start with raw data from SensorTag
        raw_bytes = raw_data.split() # Split into individual bytes
        tL = int(raw_bytes[0], 16)
        tM = int(raw_bytes[1], 16)
        tH = int(raw_bytes[2], 16)

        pL = int(raw_bytes[3], 16)
        pM = int(raw_bytes[4], 16)
        pH = int(raw_bytes[5], 16)

        temp = (tH*65536 + tM*256 + tL) / 100.0
        press = (pH*65536 + pM*256 + pL) #/ 100.0
        print(str(temp) + "|" + str(press))
    #except Exception as e: print(e)

#if __name__ == '__main__':
   
arg = sys.argv[1]

if arg == "info":
    info_conversion()
elif arg == "hum":
    hum_conversion()
elif arg == "bar":
    bar_conversion()
else:
    print("error function")
