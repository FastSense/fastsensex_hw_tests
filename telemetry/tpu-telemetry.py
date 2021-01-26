#!/usr/bin/env python3

import os
import time
import datetime
import csv
import argparse

parser = argparse.ArgumentParser(description='TPU telemetry.')
parser.add_argument('--d', type=int, default=0, help='device number')
args = parser.parse_args()
print(f"device for temperature readings /sys/class/apex/apex_{args.d}")

default_filename = datetime.datetime.now().strftime(f"tpu{args.d}_%Y-%m-%d_%H-%M-%S")
f = open(os.path.join(os.path.dirname(__file__),default_filename + ".csv"),'w', newline='')
field_names = ['time']
field_names += ['tpu_temp']
writer = csv.DictWriter(f, fieldnames=field_names)
writer.writeheader()

while True:
    row = {'time': datetime.datetime.now().isoformat(timespec='milliseconds')}
    tpu_temp = os.popen(f"cat /sys/class/apex/apex_{args.d}/temp").read()
    row['tpu_temp'] = int(tpu_temp) / 1000
    writer.writerow(row)
    f.flush()
    print(int(tpu_temp) / 1000)
    time.sleep(1)
