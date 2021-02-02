#!/usr/bin/env python3

import os
import time
import datetime
import csv
import argparse
import subprocess
from pathlib import Path
from zipfile import ZipFile


# Max log size in bytes (10Mb)
max_logs_size = 1024 * 1024 * 10


def start_logging(csv_file_path, device):
    check_size_time = 0
    while True:
        path = Path(csv_file_path)
        path.parents[0].mkdir(parents=True, exist_ok=True)

        with path.open(mode='w', newline='') as f:
            field_names = ['time']
            field_names += ['tpu_temp']
            writer = csv.DictWriter(f, fieldnames=field_names)
            writer.writeheader()

            while True:
                with subprocess.Popen(f"cat /sys/class/apex/apex_{device}/temp",
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

                    if check_size_time < time.time():
                        check_size_time = time.time() + 10
                        if check_logs_size(path):
                            break

                    time.sleep(1)

        archive_logs(path)
        csv_file_path = str(Path.home() / '.telemetry' / datetime.datetime.now().strftime('tpu{device}_%Y-%m-%d_%H-%M-%S')) + '.csv'


def check_logs_size(path):
    logs_size = 0

    for log in path.parents[0].glob('tpu*'):
        logs_size += log.stat().st_size

    if logs_size > max_logs_size:
        return True
    else:
        return False


def archive_logs(path):
    with ZipFile("{}/.telemetry/old_tpu.zip".format(Path.home()), 'w') as archive:
        for log in path.parents[0].glob('tpu*'):
            archive.write(log)
            os.remove(log)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='TPU telemetry.')
    parser.add_argument('--d', type=int, default=0, help='device number')
    parser.add_argument('--out', type=str, help='csv-file save path')
    args = parser.parse_args()

    default_filename = str(Path.home() / '.telemetry' / datetime.datetime.now().strftime(f"tpu{args.d}_Y-%m-%d_%H-%M-%S")) + '.csv'
    if not args.out:
        csv_file_path = default_filename
    else:
        csv_file_path = args.out

    print(f"device for temperature readings /sys/class/apex/apex_{args.d}")

    start_logging(csv_file_path, args.d)
