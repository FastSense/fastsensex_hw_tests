#!/usr/bin/env python3

import os
import time
import datetime
import csv
import argparse
import subprocess
from pathlib import Path


parser = argparse.ArgumentParser(description='TPU telemetry.')
parser.add_argument('--d', type=int, default=0, help='device number')
parser.add_argument('--out', type=str, help='csv-file save path')

args = parser.parse_args()
print(f"device for temperature readings /sys/class/apex/apex_{args.d}")

default_filename = str(Path.home() / '.telemetry' / datetime.datetime.now().strftime(f"tpu{args.d}_Y-%m-%d_%H-%M-%S")) + '.csv'



if not args.out:
    path = Path(default_filename)
else:
    path = Path(args.out)

path.parents[0].mkdir(parents=True, exist_ok=True)

with path.open(mode='w', newline='') as f:
    field_names = ['time']
    field_names += ['tpu_temp']
    writer = csv.DictWriter(f, fieldnames=field_names)
    writer.writeheader()

    while True:
        with subprocess.Popen(f"cat /sys/class/apex/apex_{args.d}/temp",
                            stdout=subprocess.PIPE,
                            stderr=None,
                            shell=True) as tpu_temp_process:
            row = {'time': datetime.datetime.now().isoformat(timespec='milliseconds')}
            tpu_temp = tpu_temp_process.communicate()
            tpu_temp = int(tpu_temp[0]) / 1000
            row['tpu_temp'] = tpu_temp
            writer.writerow(row)
            f.flush()
            print(tpu_temp)
            time.sleep(1)
