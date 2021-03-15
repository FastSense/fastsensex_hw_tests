#!/usr/bin/env python3

import os
import time
import csv
import datetime
import argparse
import socket
from pathlib import Path
from zipfile import ZipFile

import numpy as np
from matplotlib import pyplot as plt

from log_processing_utils import LogProcessing
import psutil

start_time = time.time()

# Max log size in bytes (10Mb)
max_logs_size = 1024 * 1024 * 10
log_period = 1 # days

datetime_format = "%Y-%m-%d_%H-%M-%S"

device_name = socket.gethostname()
target = "cpu"

samba_server_ip = "192.168.194.51"
samba_login = "admin"
samba_password = "FastDakota21"

OUTPUT_TEMPLATE = """
\033[93m%.3fs\033[0m
\033[92mTemp:\t\033[1m%7.2f\033[0m\033[92m°C\033[0m    %r
\033[92mLoad:\t\033[1m%7.2f\033[0m\033[92m%%\033[0m     %r
\033[92mFreq:\t\033[1m%8.2f\033[0m \033[92mMHz\033[0m %r
"""


def start_logging(csv_file_path: str):
    check_time = 0

    lprocessor = LogProcessing(Path(csv_file_path).parents[0], target, device_name, datetime_format, max_logs_size, log_period)
    lprocessor.samba_setup(samba_server_ip, samba_login, samba_password)

    if lprocessor.check_logs_size() or lprocessor.check_old_logs():
        lprocessor.archive_logs()

    while True:
        path = Path(csv_file_path)
        path.parents[0].mkdir(parents=True, exist_ok=True)

        with path.open(mode='w', newline='') as f:
            field_names = ['time']

            for name in ('temp', 'freq', 'load'):
                field_names += ['cpu%d_%s' % (i, name) for i in range(psutil.cpu_count())]

            writer = csv.DictWriter(f, fieldnames=field_names)

            writer.writeheader()

            try:
                while True:
                    t = time.time() - start_time
                    temp = [temp.current for temp in psutil.sensors_temperatures()['coretemp'] if 'CORE' in temp.label.upper()]
                    cpu_loads = psutil.cpu_percent(percpu=True)
                    cpu_load = psutil.cpu_percent()
                    cpu_freqs = [f.current for f in psutil.cpu_freq(percpu=True)]
                    cpu_freq = psutil.cpu_freq().current

                    print(OUTPUT_TEMPLATE % (t, max(temp), temp, cpu_load,
                                            cpu_loads, cpu_freq, cpu_freqs))

                    row = {'time': datetime.datetime.now().isoformat(timespec='milliseconds')}

                    for i in range(psutil.cpu_count()):
                        row['cpu%d_temp' % i] = int(temp[i])
                        row['cpu%d_freq' % i] = int(cpu_freqs[i])
                        row['cpu%d_load' % i] = int(cpu_loads[i])

                    writer.writerow(row)
                    f.flush()

                    if check_time < time.time():
                        check_time = time.time() + 30
                        if lprocessor.check_logs_size() or lprocessor.check_old_logs():
                            break

                    time.sleep(1)
            except KeyboardInterrupt:
                return

        lprocessor.archive_logs()
        csv_file_path = str(Path.home() / '.telemetry' / datetime.datetime.now().strftime(f"{target}_{datetime_format}")) + '.csv'


def load_from_csv(file_path: str):
    with open(file_path, 'r') as csv_file:
        reader = csv.DictReader(csv_file)

        cpu_count = psutil.cpu_count()

        t = []
        temp = [[] for t in range(cpu_count)]
        load = [[] for t in range(cpu_count)]
        freq = [[] for t in range(cpu_count)]

        for row in reader:
            t.append(datetime.datetime.strptime(row['time'], datetime_format))
            for i in range(cpu_count):
                temp[i].append(float(row['cpu%d_temp' % i]))
                load[i].append(float(row['cpu%d_load' % i]))
                freq[i].append(float(row['cpu%d_freq' % i]))

        return t, temp, load, freq


def draw_subchart(t, data, ax, yrange, ylabel, label_template='%d', alpha=0.25,
                  draw_errorbar=False, errorbar_label='mean', start=0, end=-1):
    ax.grid()
    ax.set(yticks=yrange, ylabel=ylabel)

    for i in range(len(data)):
        ax.plot(t, data[i][start:end], alpha=alpha, label=label_template % i)

    if draw_errorbar and end < 0:
        r = range(0, len(t), 5)
        ax.errorbar([t[i] for i in r],
                    [np.mean([data[j][i] for j in range(len(data))]) for i in r],
                    [np.std([data[j][i] for j in range(len(data))]) for i in r],
                    fmt='k-', capthick=1, capsize=3, label=errorbar_label)

    ax.legend()


def save_chart(csv_file_path: str, image_file_path: str, start_time='1970-01-01T00:00:00.000',
               end_time='2100-01-01T00:00:00.000'):
    start_time = datetime.datetime.strptime(start_time, datetime_format)
    end_time = datetime.datetime.strptime(end_time, datetime_format)

    t, temp, load, freq = load_from_csv(csv_file_path)

    start, end = None, len(t) - 1

    for i in range(len(t)):
        if start is None and t[i] >= start_time:
            start = i
        if t[i] <= end_time:
            end = i

    fig, axs = plt.subplots(nrows=3, figsize=(14, 14))

    draw_subchart(t[start:end], temp[start:end], axs[0], range(0, 101, 5),
                  'CPU temperature, °C', 'CPU%d temperature',
                  1, False, start=start, end=end)

    draw_subchart(t[start:end], load[start:end], axs[1], range(0, 101, 5),
                  'CPU load, %', 'CPU%d load', 0.25, True,
                  'CPU load men', start=start, end=end)

    draw_subchart(t[start:end], freq[start:end], axs[2], range(0, 8000, 500),
                  'CPU frequency, MHz', 'CPU%d freq', 0.25, True,
                  'CPU frequency men', start=start, end=end)

    plt.savefig(image_file_path)


if __name__ == '__main__':
    default_filename = str(Path.home() / '.telemetry' / datetime.datetime.now().strftime(f"{target}_{datetime_format}"))

    parser = argparse.ArgumentParser(description='CPU telemetry.')
    parser.add_argument('--stress', action='store_true', help='run stress-test or not')
    parser.add_argument('--out', type=str, default=default_filename + '.csv', help='csv-file save path')
    parser.add_argument('--chart', type=str, default=default_filename + '.png', help='path to save the chart')
    parser.add_argument('--plot', action='store_true', help='plot chart from the specified csv-table')
    parser.add_argument('--csv', type=str, help='csv-file path for chart plotting')
    parser.add_argument('--from_time', type=str, help='start-time for chart plotting')
    parser.add_argument('--to_time', type=str, help='end-time for chart plotting')

    args = parser.parse_args()

    if args.plot or args.stress:
        if args.plot:
            save_chart(args.csv, args.chart, args.from_time, args.to_time)
        elif args.stress:
            with os.popen('stress --cpu %d' % psutil.cpu_count()) as p:
                start_logging(args.out)
                save_chart(args.out, args.chart)
    else:
        start_logging(args.out)
        save_chart(args.out, args.chart)

