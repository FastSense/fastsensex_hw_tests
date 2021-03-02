import psutil
import subprocess
import time
import sys

max_stress_time = 60 * 10

warn_temp = 50
critical_temp = 60

if __name__ == '__main__':
    start_time = time.time()

    with subprocess.Popen("stress --cpu %d" % psutil.cpu_count(), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as stress_process:
        while time.time() < start_time + max_stress_time:
            temp = [temp.current for temp in psutil.sensors_temperatures()['coretemp'] if 'CORE' in temp.label.upper()]

            for core_temp in temp:
                if core_temp > warn_temp:
                    pass
                elif core_temp > critical_temp:
                    print("\nWarn temperature. Exit")
                    sys.exit()
            print(f"CPU temperature: {temp}\r", end='')
            time.sleep(0.5)
        print("\nTemperature is stable, CPU test will passed.")
