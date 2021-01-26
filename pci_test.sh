#! /bin/bash

WIFI_COUNT=$(lspci -d 8086:2723 | wc -l)
SSD_COUNT=$(lspci -d 15B7:5004 | wc -l)
MYRYAD_COUNT=$(lspci -d 1B73:1100 | wc -l)
CORAL_COUNT=$(lspci -d 1AC1:089A | wc -l)

echo "Found:"

if [ $WIFI_COUNT -ne 0 ]
then
    echo "WiFi6 AX200 - ${WIFI_COUNT}x"
fi

if [ $SSD_COUNT -ne 0 ]
then
    echo "SSD 128GB WD SN520 - ${SSD_COUNT}x"
fi

if [ $MYRYAD_COUNT -ne 0 ]
then
    echo "Myriad FL1100 - ${MYRYAD_COUNT}x"
fi


if [ $CORAL_COUNT != '0' ]
then
    echo "Google Coral TPU - ${CORAL_COUNT}x"
fi
