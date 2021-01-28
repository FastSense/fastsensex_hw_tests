## Телеметрия на CPU

Получает температуру, загрузку и частоту ядер.

Для использования нужно установть зависимости:
```
pip3 install psutil
pip3 install numpy
pip3 install matplotlib
sudo apt-get install stress
```

```
usage: cpu-telemetry.py [-h] [--stress] [--out OUT] [--chart CHART] [--plot]
                        [--csv CSV] [--from_time FROM_TIME]
                        [--to_time TO_TIME]

CPU telemetry.

optional arguments:
  -h, --help            show this help message and exit
  --stress              run stress-test or not
  --out OUT             csv-file save path
  --chart CHART         path to save the chart
  --plot                plot chart from the specified csv-table
  --csv CSV             csv-file path for chart plotting
  --from_time FROM_TIME
                        start-time for chart plotting
  --to_time TO_TIME     end-time for chart plotting                     
```

Результаты телеметрии сохряняются в CSV-файл, указанный в `OUT`. По ним же строится график и сохраняется в файл, указанный в `CHART`

Можно отдельно построить график по csv-файлу, указав флаг `--plot`, а также путь до csv-файла `--csv` и путь, по которому нужно сохранить график `--chart`. Можно также указать временной промежуток, по которому будет строиться график в формате `2020-05-08T10:55:34.513`, например:

```
./cpu-telemetry.py --plot --from_time 2021-01-28T15:08:46.910 --to_time 2021-01-28T15:08:55.110 --csv ~/.telemetry/cpu_2021-01-28_15-08-44.csv --chart out.png
```

Формат CSV-файла:
```
time,cpu1_temp,cpu1_freq,cpu1_load,cpu2_temp,cpu2_freq,cpu2_load, ...
2020-05-08T10:55:34.513,85,2000,100,85,2000,100, ...
2020-05-08T10:55:34.517,84,2000,100,85,2000,100, ...
```

## Телеметрия на TPU (Coral)

Запуск (--d номер устройства)
```
python3 tpu-telemetry.py --d 0
```

Формат CSV-файла:
```
time,tpu_temp
2020-05-08T10:55:34.513,55
2020-05-08T10:55:34.517,55
```

## Телеметрия на VPU (Myriad)

Запуск (--d имя устройства MYRIAD или полностью MYRIAD.1.7-ma2480)
```
source /opt/intel/openvino/bin/setupvars.sh
python3 vpu-stress.py --d MYRIAD
```

Формат CSV-файла:
```
time,vpu_temp
2020-05-08T10:55:34.513,55
2020-05-08T10:55:34.517,55
```
