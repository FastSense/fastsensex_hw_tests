#!/bin/bash

if [ "$EUID" -ne 0 ]
then
    echo "Please run as root"
    exit 0
fi

while getopts d: flag 
do
    case "${flag}" in
        d) DEVICE=${OPTARG};;
    esac
done

if [ -z "$DEVICE" ]
then
    DEVICE="/dev/sda1"
    echo "Device not entered, default selected: $DEVICE"
else
    echo "Device set to: $DEVICE"
fi

echo "To start testing press: y"

IFS=
read -n 1 -s key
if [ "$key" = "y" ] || [ "$key" = "Y" ]
then
    echo "Start USB testing. Read from $DEVICE"

    if [ $? -eq 0 ]
    then
        dd if=$DEVICE of=/dev/null bs=1M count=1024 iflag=direct status=progress
    else
        echo "Something went wrong with the mount..."
    fi

else
    echo "Typed key: \"$key\". Exiting"
fi
