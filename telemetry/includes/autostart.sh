#!/bin/bash

CPU="cpu-telemetry"
TPU="tpu-telemetry"

MYPATH=$0
TEMP=${MYPATH:0:2}
if [ $TEMP = "./" ]; then
        MYPATH=`pwd`${MYPATH:1}
fi
MYPATH=${MYPATH%%autostart*}

TELEMETRY_PATH=${MYPATH%%includes*}
sed "s|path_to_cpu_telemetry|$TELEMETRY_PATH$CPU.py|" "$MYPATH$CPU.service" > "/etc/systemd/system/$CPU.service"
sed "s|path_to_tpu_telemetry|$TELEMETRY_PATH$TPU.py|" "$MYPATH$TPU.service" > "/etc/systemd/system/$TPU.service"

systemctl enable $CPU
systemctl enable $TPU

systemctl start $CPU
systemctl start $TPU
