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
max_logs_size = 1024 * 1024 * 10
device_name = socket.gethostname()

samba_server_ip = "192.168.194.51"
samba_login = "admin"
samba_password = "FastDakota21"


def start_logging(log_file_path, device):
    field_names = ['time']
    field_names.append('tpu_temp')
    check_size_time = 0

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

                temp_process = temp_process_stack.enter_context(open("/sys/class/apex/apex_{}/temp".format(device_ids[id_num]), 'r'))

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

        archive_logs(log_file_path)


def check_devices():
    device_ids = []
    apex_path = Path('/sys/class/apex/')
    for device in apex_path.glob('apex_*'):
        device_ids.append(str(device).split('_')[1])
    return device_ids


def check_logs_size(path):
    logs_size = 0

    for log in path.glob('tpu*'):
        logs_size += log.stat().st_size

    if logs_size > max_logs_size:
        return True
    else:
        return False


def archive_logs(path):
    arhive_name = "{}/old_tpu_{}.zip".format(path, datetime.datetime.now().strftime(f"Y-%m-%d_%H-%M-%S"))

    old_archives = list(path.glob('old_tpu*'))
    if len(old_archives) > 0:
        for archive in old_archives:
            os.remove(archive)

    with ZipFile(arhive_name, 'w') as archive:
        for log in path.glob('tpu*'):
            archive.write(log)
            os.remove(log)

    samba_log_upload(arhive_name, device_name)


def log_file_path_gen(logs_file_path, device_ids):
    paths = []
    for device_id in device_ids:
        paths.append("{}/{}.csv".format(logs_file_path, datetime.datetime.now().strftime(f"tpu{device_id}_Y-%m-%d_%H-%M-%S")))
    return paths


def samba_log_upload(input_files, device_name):
    if isinstance(input_files, list):
        input_files = [input_files]

    for file in input_files:
        output_file = "/telemetry/{}/{}".format(device_name, file.name)
        load_files = subprocess.run("smbclient //{}/fssamba -U {}%{} -c 'mkdir /telemetry/{}; put \"{}\" \"{}\"'".format(samba_server_ip,
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
