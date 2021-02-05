#!/usr/bin/env python3

import os
import time
import datetime
import csv
import argparse
import subprocess
import socket
from pathlib import Path
from zipfile import ZipFile
from contextlib import ExitStack


# Max log size in bytes (10Mb)
max_logs_size = 1024 * 1

datetime_format = "Y-%m-%d_%H-%M-%S"

device_name = socket.gethostname()
target = "tpu"

samba_server_ip = "192.168.194.51"
samba_login = "admin"
samba_password = "FastDakota21"


def start_logging(log_file_path, device):
    field_names = ['time']
    field_names.append('tpu_temp')
    check_size_time = 0

    check_old_logs(log_file_path)

    device_ids = check_devices()

    while True:
        log_file_path.mkdir(parents=True, exist_ok=True)
        devices = []

        log_file_names = log_file_path_gen(log_file_path, device_ids)

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
                    check_size_time = time.time() + 10
                    if check_logs_size(log_file_path):
                        break

                time.sleep(1)

        check_old_logs(log_file_path, archive=True)


def check_devices():
    device_ids = []
    apex_path = Path('/sys/class/apex/')
    for device in apex_path.glob('apex_*'):
        device_ids.append(str(device).split('_')[1])
    return device_ids


def check_logs_size(log_path):
    logs_size = 0

    for log in log_path.glob(f"{target}*"):
        logs_size += log.stat().st_size

    if logs_size > max_logs_size:
        delete_old(log_path, delete='archive')
        return True
    else:
        return False


def archive_logs(log_path, first_time, last_time):
    arhive_name = f"{log_path}/old_{target}.{first_time}-{last_time}.zip"

    with ZipFile(arhive_name, 'w') as archive:
        for log in log_path.glob(f"{target}*"):
            archive.write(log)
            os.remove(log)

    samba_log_upload(arhive_name)


def delete_old(log_path, delete='log'):
    if delete == 'archive':
        olds = list(log_path.glob(f"old_{target}*"))
    elif delete == 'log':
        olds = list(log_path.glob(f"{target}*"))

    if len(olds) > 0:
        for archive in olds:
            os.remove(archive)


def log_file_path_gen(logs_file_path, device_ids):
    # Generate string paths to devices
    paths = []
    for device_id in device_ids:
        paths.append("{}/{}.csv".format(logs_file_path, datetime.datetime.now().strftime(f"{target}{device_id}_{datetime_format}")))
    return paths


def check_old_logs(log_path, archive=False):
    current_time = datetime.datetime.now()
    first_log_time = current_time
    last_log_time = current_time

    for old_log in log_path.glob(f"{target}*"):
        file_time = old_log.stem
        # Divides the string according to the standard time format
        # Searches for the first occurrence of a letter specifying the year 'Y'
        file_time = file_time[file_time.find('Y'):]
        file_time = datetime.datetime.strptime(file_time, datetime_format)
        print(file_time)

        if file_time < first_log_time:
            first_log_time = file_time
        if file_time > last_log_time:
            last_log_time = file_time

        if file_time.day + 2 < current_time.day:
            archive = True

    if archive:
        archive_logs(log_path, first_log_time.strftime(f"{datetime_format[2:]}"), last_log_time.strftime(f"{datetime_format[2:]}"))


def samba_log_upload(input_files):
    if not isinstance(input_files, list):
        input_files = [input_files]

    for file in input_files:
        if not isinstance(input_files, Path):
            file = Path(file)

        output_file = f"/telemetry/{device_name}/{file.name}"
        load_files = subprocess.run("smbclient //{}/fssamba -U {}%{} -c 'mkdir /telemetry/{}; put {} {}'".format(samba_server_ip,
                                                                                                                 samba_login,
                                                                                                                 samba_password,
                                                                                                                 device_name,
                                                                                                                 file,
                                                                                                                 output_file),
                                    shell=True)


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
