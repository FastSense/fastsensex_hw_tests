## Телеметрия на CPU

Получает температуру, загрузку и частоту ядер.

Для использования нужно установть зависимости:
```
pip3 install psutil
pip3 install numpy
sudo apt-get install stress
```

```
usage: cpu-telemetry.py [-h] [--stress] [--out OUT] [--chart CHART]

CPU telemetry.

optional arguments:
  -h, --help     show this help message and exit
  --stress       run stress-test or not
  --out OUT      csv-file save path
  --chart CHART  path to save the chart
                                        
```

Результаты телеметрии сохряняются в CSV-файл, указанный в `OUT`. По ним же строится график и сохраняется в файл, указанный в `CHART`

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
time,tpu0_temp
2020-05-08T10:55:34.513,55
2020-05-08T10:55:34.517,55
```
