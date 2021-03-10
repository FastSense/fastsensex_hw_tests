#!/usr/bin/env python3

import os
import time
import datetime
import csv
import argparse
import socket
from pathlib import Path
from zipfile import ZipFile
from contextlib import ExitStack

from log_processing_utils import LogProcessing


# Max log size in bytes (10Mb)
max_logs_size = 1024 * 1024 * 10
log_period = 1 # days

datetime_format = "%Y-%m-%d_%H-%M-%S"

device_name = socket.gethostname()
target = "tpu"

samba_server_ip = "192.168.194.51"
samba_login = "admin"
samba_password = "FastDakota21"


def start_logging(log_file_path, device):

    field_names = ['time']
    field_names.append('tpu_temp')
    check_size_time = 0

    lprocessor = LogProcessing(log_file_path, target, device_name, datetime_format, max_logs_size, log_period)
    lprocessor.samba_setup(samba_server_ip, samba_login, samba_password)

    lprocessor.check_old_logs()

    device_ids = check_devices()

    while True:
        log_file_path.mkdir(parents=True, exist_ok=True)
        devices = []

        log_file_names = lprocessor.log_file_path_gen(device_ids)


        with ExitStack() as file_stack, ExitStack() as temp_process_stack:
            for id_num in range(len(device_ids)):
                log_file = file_stack.enter_context(open(log_file_names[id_num], 'w'))
                writer = csv.DictWriter(log_file, fieldnames=field_names)
                writer.writeheader()

                temp_process = temp_process_stack.enter_context(open(f"/sys/class/apex/apex_{device_ids[id_num]}/temp", 'r'))

                devices.append((log_file, writer, temp_process))

            while True:
                for device in devices:
                    row = {'time': datetime.datetime.now().isoformat(timespec='milliseconds')}
                    tpu_temp = device[2].readline()
                    device[2].seek(0)
                    tpu_temp = int(tpu_temp) / 1000
                    row['tpu_temp'] = tpu_temp
                    device[1].writerow(row)
                    device[0].flush()
                    print(tpu_temp)

                if check_size_time < time.time():
                    check_size_time = time.time() + 30
                    if lprocessor.check_logs_size() or lprocessor.check_old_logs():
                        break

                time.sleep(1)

        lprocessor.check_old_logs(archive=True)


def check_devices():
    device_ids = []
    apex_path = Path('/sys/class/apex/')
    for device in apex_path.glob('apex_*'):
        device_ids.append(str(device).split('_')[1])
    return device_ids


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='TPU telemetry.')
    parser.add_argument('--d', type=int, default=0, help='device number')
    parser.add_argument('--out', type=str, help='csv-file save path')
    args = parser.parse_args()

    default_log_path = Path(str(Path.home() / '.telemetry'))

    if not args.out:
        log_file_path = default_log_path
    else:
        log_file_path = args.out

    print(f"device for temperature readings /sys/class/apex/apex_{args.d}")

    start_logging(log_file_path, args.d)
