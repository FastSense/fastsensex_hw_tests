import os
import time
import datetime
import csv
import numpy as np
import argparse
from openvino.inference_engine import IECore

parser = argparse.ArgumentParser(description='VPU telemetry.')
parser.add_argument('--d', type=str, default="MYRIAD", help='device name')
args = parser.parse_args()

ie = IECore()
ie.set_config({'VPU_HW_STAGES_OPTIMIZATION': 'NO'}, f"{args.d}")
net = ie.load_network(ie.read_network('net.xml', 'net.bin'),f"{args.d}")

default_filename = datetime.datetime.now().strftime((f"vpu{args.d}_%Y-%m-%d_%H-%M-%S").replace('MYRIAD',''))
f = open(os.path.join(os.path.dirname(__file__),default_filename + ".csv"),'w', newline='')
field_names = ['time']
field_names += ['vpu_temp']
writer = csv.DictWriter(f, fieldnames=field_names)
writer.writeheader()

ut_in = np.load('ut_net_inp.npy')
while True:
    start = time.time()
    out = net.infer({ next(iter(net.inputs)) : ut_in})
    end = time.time()
    print("{:.4f}".format((end - start)/1))
    #print("DEVICE_THERMAL : ", ie.get_metric(metric_name="DEVICE_THERMAL", device_name=f"{args.d}"))

    row = {'time': datetime.datetime.now().isoformat(timespec='milliseconds')}
    row['vpu_temp'] = int(ie.get_metric(metric_name="DEVICE_THERMAL", device_name=f"{args.d}"))
    writer.writerow(row)
    f.flush()

out = out['StatefulPartitionedCall/pose_net/concatenate/concat']
print(out)

ut_out = np.load('ut_net_out.npy')
print(ut_out)      


