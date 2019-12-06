#!/bin/bash

#sudo date -s "Sat Aug  13 15:55:11 PDT 2016"
#sudo date -s "Sat Aug  13 15:55:11 UTC 2016" # During Daylight savings time
#cd /home/francesco/Dropbox/EH/Software/My_Code/Version_3_Light/

reqtemp(){ #Temp sensor
	sudo gatttool -b $ID --char-write-req -a 0x24 -n 01 >/dev/null 2>&1 #initiates (0x24)
	sleep 0.5
	tempOutput="$(sudo gatttool -b $ID --char-read -a 0x21)" #collects (0x21)
	sleep 0.2
	sudo gatttool -b $ID --char-write-req -a 0x24 -n 00 >/dev/null 2>&1 #disables (0x24)

	# Manipulating data
	outputPrefix="Characteristic value/descriptor: "
	raw_temp_data=${tempOutput#$outputPrefix} #Removes prefix of tempOutput
	#/bin/echo ${raw_temp_data} # raw temp bytes from sensortag
	celsius="$(python batt_conversion.py "${raw_temp_data}")" # Converts raw_temp_data to celsius
}
reqlux(){	#Lux sensor
	echo "Reading Light..."
	sudo gatttool -b $ID --char-write-req -a 0x44 -n 01 #initiates (0x44)
	sleep 1
	luxOutput="$(sudo gatttool -b $ID --char-read -a 0x41)" #collects 0x41)
	sleep 0.5
	sudo gatttool -b $ID --char-write-req -a 0x44 -n 00 #disables (0x44)
	sleep 0.5

	# Manipulating data
	outputPrefix="Characteristic value/descriptor: "
	raw_lux_data=${luxOutput#$outputPrefix} #Removes prefix of luxOutput
	/bin/echo ${raw_lux_data} # raw lux bytes from sensortag
	lux="$(python lux_conversion.py "${raw_lux_data}")" # Converts raw_lux_data to lux
}

reqhum(){	#Humidity sensor
	sudo gatttool -b $ID --char-write-req -a 0x2C -n 01 #initiates (0x44)
	sleep 1.9
	HumOutput="$(sudo gatttool -b $ID --char-read -a 0x29)" #collects 0x41)
	sleep 0.5
	sudo gatttool -b $ID --char-write-req -a 0x2C -n 00 #disables (0x44)
	sleep 0.5

	# Manipulating data
	outputPrefix="Characteristic value/descriptor: "
	raw_hum_data=${HumOutput#$outputPrefix} #Removes prefix of luxOutput
	/bin/echo ${raw_hum_data} # raw hum bytes from sensortag
	hum="$(python temp_conversion.py "${raw_hum_data}")" # Converts raw_hum_data to celsius
}

reqbar(){
	#echo "Reading " $Name
	sudo gatttool -b $ID --char-write-req -a 0x34 -n 01 > useless.txt #initiates (0x44)
	sleep 1
	barOutput="$(sudo gatttool -b $ID --char-read -a 0x31)" #collects 0x41)
	sleep 0.5
	sudo gatttool -b $ID --char-write-req -a 0x34 -n 00 > useless.txt #disables (0x44)

	# Manipulating data
	outputPrefix="Characteristic value/descriptor: "
	raw_bar_data=${barOutput#$outputPrefix} #Removes prefix of luxOutput
	bar="$(python batt_conversion.py "${raw_bar_data}")" # Converts raw_bar_data to celsius
}

reqmov(){
#        sudo gatttool -b $Sensor --char-write-req -a 0x3C -n 3F00 #initiates (0x44)
#        movOutput="$(sudo gatttool -b $Sensor --char-read -a 0x39)" #collects 0x41)
#        sudo gatttool -b $Sensor --char-write-req -a 0x34 -n 00 #disables (0x44)
	echo "mov"
}

Occupancy()
{
        #empty="";
        #ready="";
        #disaster="connect: Device or resource busy (16)";
        #echo "" > error.txt
        #ready="$(gatttool -b $ID --char-write-req -a 0x0024 -n 00 2> error.txt)" #disables (0x24)
        #line=$(head -n 1 error.txt)

        #if [ "$line" = "$disaster" ]; then
        #        sudo /etc/init.d/bluetooth restart
        #        sleep 5
        #fi
	#
        #if [ "$ready" != "$empty" ]; then

        echo "1" > wait.txt
	
	#reqbar
	reqtemp		
	#Write Data
    	dt=$(date '+%m/%d/%y %H:%M:%S');
	echo "inside Loop"
    	echo "${dt}|${log}|${celsius} degC|${lux} lux|${bar}|${raw_temp_data}|${raw_bar_data}" # prints data in celsius a$
    	printf "\n${dt}|${log}|${celsius}|${lux}|${bar}|${raw_temp_data}|${raw_bar_data}" >> $File #prints $
    	echo "2" > wait.txt
	#		sleep 10
	#fi
}

Name=$1
ID=$2
File=$3
Action=$4
log=$5

#echo "Detector"
Occupancy
#echo "Over"
exit

#        echo "Resetting..."
#        sudo hciconfig hci0 reset #reset the adapter
#        sleep 8
#done

#or reset the BLuethoot with: sudo /etc/init.d/bluetooth restartReset the adapter: sudo hciconfig hci0 reset or reset the BLuethoot with:
#sudo /etc/init.d/bluetooth restart
