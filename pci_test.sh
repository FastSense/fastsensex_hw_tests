#! /bin/bash

if [ "$EUID" -ne 0 ]
then
    echo "Please run as root"
    exit 0
fi

WIFI_ID="8086:2723"
SSD_ID="15B7:5004"
MYRYAD_ID="1B73:1100"
CORAL_ID="1AC1:089A"

WIFI_COUNT=$(lspci -d $WIFI_ID | wc -l)
SSD_COUNT=$(lspci -d $SSD_ID | wc -l)
MYRYAD_COUNT=$(lspci -d $MYRYAD_ID | wc -l)
CORAL_COUNT=$(lspci -d $CORAL_ID | wc -l)

take_names () {
    names=()
    while read -r device_name
    do
        name=$(echo $device_name | head -n1 | cut -d " " -f1)
        names+=("$name")
    done < <(lspci -d $1)
}

print_devices() {
    local i=0
    while read -r device_speed
    do
        device_speed=${device_speed##*LnkSta:}
        device_speed=${device_speed%%, TrErr*}
        echo "  ${names[$i]}: ${device_speed}"
        i=$(($i+1))
    done < <(lspci -vvd $1 | grep LnkSta:)
}


echo "Found:"

if [ $WIFI_COUNT -ne 0 ]
then
    echo "WiFi6 AX200 - ${WIFI_COUNT}x"
    take_names $WIFI_ID
    print_devices $WIFI_ID
    echo
fi

if [ $SSD_COUNT -ne 0 ]
then
    echo "SSD 128GB WD SN520 - ${SSD_COUNT}x"
    take_names $SSD_ID
    print_devices $SSD_ID
    echo
fi

if [ $MYRYAD_COUNT -ne 0 ]
then
    echo "PCIe->2xUSB bridge FL1100 for Myriad - ${MYRYAD_COUNT}x"
    take_names $MYRYAD_ID
    print_devices $MYRYAD_ID
    echo
fi

if [ $CORAL_COUNT -ne 0 ]
then
    echo "Google Coral's TPU - ${CORAL_COUNT}x"
    take_names $CORAL_ID
    print_devices $CORAL_ID
    echo
fi
