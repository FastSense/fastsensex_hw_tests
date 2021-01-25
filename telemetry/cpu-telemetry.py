#!/usr/bin/env python3

import os
import time
import csv
import datetime
import argparse

import numpy as np
from matplotlib import pyplot as plt

import psutil

start_time = time.time()

OUTPUT_TEMPLATE = """
\033[93m%.3fs\033[0m
\033[92mTemp:\t\033[1m%7.2f\033[0m\033[92m°C\033[0m    %r
\033[92mLoad:\t\033[1m%7.2f\033[0m\033[92m%%\033[0m     %r
\033[92mFreq:\t\033[1m%8.2f\033[0m \033[92mMHz\033[0m %r
"""

def start_logging(csv_file_path: str):
    with open(csv_file_path, 'w', newline='') as f:
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

                time.sleep(1)
        except KeyboardInterrupt:
            return


def load_from_csv(file_path: str):
    with open(file_path, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        
        cpu_count = psutil.cpu_count()
        
        t, temp, load, freq = [], [[] for t in range(cpu_count)], [[] for t in range(cpu_count)], [[] for t in range(cpu_count)]

        for row in reader:
            t.append(datetime.datetime.strptime(row['time'], '%Y-%m-%dT%H:%M:%S.%f'))
            for i in range(cpu_count):
                temp[i].append(float(row['cpu%d_temp' % i]))
                load[i].append(float(row['cpu%d_load' % i]))
                freq[i].append(float(row['cpu%d_freq' % i]))
                
        return t, temp, load, freq


def save_chart(csv_file_path: str, image_file_path: str):
    t, temp, load, freq = load_from_csv(csv_file_path)

    fig, axs = plt.subplots(nrows=3, figsize=(14, 14))

    axs[0].grid()
    axs[0].set(yticks=range(0, 101, 5), ylabel='CPU temperature, °C')

    for i in range(len(temp)):
        axs[0].plot(t, temp[i], label='CPU%d' % i)
        
    axs[0].legend()


    axs[1].grid()
    axs[1].set(yticks=range(0, 101, 5), ylabel='CPU load, %')

    for i in range(len(load)):
        axs[1].plot(t, load[i], alpha=0.25, label='CPU%d load' % i)
        
    r = range(0, len(t), 5)
    axs[1].errorbar([t[i] for i in r],
                    [np.mean([load[j][i] for j in range(8)]) for i in r],
                    [np.std([load[j][i] for j in range(8)]) for i in r],
                    fmt='k-', capthick=1, capsize=3, label='CPU mean')

    axs[1].legend()


    axs[2].grid()
    axs[2].set(yticks=range(0, 8000, 500), ylabel='CPU frequency, MHz')

    for i in range(len(freq)):
        axs[2].plot(t, freq[i], alpha=0.25, label='CPU%d freq' % i)
        
    r = range(0, len(t), 5)
    axs[2].errorbar([t[i] for i in r],
                    [np.mean([freq[j][i] for j in range(8)]) for i in r],
                    [np.std([freq[j][i] for j in range(8)]) for i in r],
                    fmt='k-', capthick=1, capsize=3, label='CPU mean')

    axs[2].legend()

    plt.savefig(image_file_path)


if __name__ == '__main__':
    default_filename = datetime.datetime.now().strftime('cpu_%Y-%m-%d_%H-%M-%S')

    parser = argparse.ArgumentParser(description='CPU telemetry.')
    parser.add_argument('--stress', action='store_true', help='run stress-test or not')
    parser.add_argument('--out', type=str, default=default_filename + '.csv', help='csv-file save path')
    parser.add_argument('--chart', type=str, default=default_filename + '.png', help='path to save the chart')

    args = parser.parse_args()

    if args.stress:
        with os.popen('stress --cpu %d' % psutil.cpu_count()) as p:
            start_logging(args.out)
            save_chart(args.out, args.chart)
    else:
        start_logging(args.out)
        save_chart(args.out, args.chart)
