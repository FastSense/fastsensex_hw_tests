#!/bin/bash

if [ "$EUID" -ne 0 ]
then
    echo "Please run as root"
    exit 0
fi

while getopts m:d: flag 
do
    case "${flag}" in
        m) MOUNT_POINT=${OPTARG};;
        d) DEVICE=${OPTARG};;
    esac
done

if [ -z "$MOUNT_POINT" ]
then
    MOUNT_POINT="/media/usb_test"
    echo "Mount point not entered, default selected directory: $MOUNT_POINT"
else
    echo "Mount point: $MOUNT_POINT"
fi

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

    echo "Start USB testing"
    mkdir $MOUNT_POINT
    mount $DEVICE $MOUNT_POINT

    if [ $? -eq 0 ]
    then
        dd if=/dev/urandom of=$MOUNT_POINT/test_file bs=1M count=128 oflag=direct status=none
        dd if=$MOUNT_POINT/test_file of=/dev/null bs=1M iflag=direct status=progress
        rm $MOUNT_POINT/test_file
        umount $DEVICE
    else
        echo "Something went wrong with the mount..."
    fi
    rm -r $MOUNT_POINT

else
    echo "Typed key: \"$key\". Exiting"
fi
