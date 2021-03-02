import nnio
import requests
import time
import sys
import subprocess
from pathlib import Path
from threading import Thread
from queue import Queue
from openvino.inference_engine import IECore


max_stress_time = 60 * 10

URL_TEST_IMAGE = 'https://raw.githubusercontent.com/FastSense/nnio/master/tests/dogs.jpg'
myriad_temp = 0
coral_temp = 0


class OpenvinoThread(Thread):
    def __init__(self):
        super().__init__()
        self.temperature = 0
        self.start_time = time.time()
        self.daemon = True

        self.warning_temp = 80
        self.critical_temp = 100

        self.device = "MYRIAD"

    def run(self):
        openvino_model = nnio.zoo.openvino.detection.SSDMobileNetV2(self.device)
        openvino_preproc = openvino_model.get_preprocessing()
        openvino_image = openvino_preproc('dogs.jpg')

        while time.time() < start_time + max_stress_time:
            boxes, info = openvino_model(openvino_image, return_info=True)
            self.temperature = round(openvino_model.model.ie.get_metric(metric_name="DEVICE_THERMAL", device_name="MYRIAD"), 2)
            if self.temperature > warning_temp:
                print("Warning {}".format(warning_temp))
            elif self.temperature > critical_temp:
                print("Critical {}".format(critical_temp))
                break


class TFliteThread(Thread):
    def __init__(self, device_id):
        super().__init__()
        self.temperature = 0
        self.start_time = time.time()
        self.daemon = True

        self.warning_temp = 80
        self.critical_temp = 100

        self.device_id = device_id
        self.device = f"TPU:{self.device_id}"
        print(self.device)

    def run(self):
        tflite_model = nnio.zoo.edgetpu.detection.SSDMobileNet(self.device)
        tflite_preproc = tflite_model.get_preprocessing()
        tflite_image = tflite_preproc('dogs.jpg')

        coral_temp_path = Path(f"/sys/class/apex/apex_{self.device_id}/temp")

        with open(coral_temp_path, 'r') as coral_temp:
            while time.time() < start_time + max_stress_time:
                boxes, info = tflite_model(tflite_image, return_info=True)
                self.temperature = coral_temp.readline()
                coral_temp.seek(0)
                self.temperature = int(self.temperature) / 1000

                if self.temperature > warning_temp:
                    print("Warning {}".format(warning_temp))
                elif self.temperature > critical_temp:
                    print("Critical {}".format(critical_temp))
                    break


def check_devices():
    device_ids = []
    apex_path = Path('/sys/class/apex/')
    for device in apex_path.glob('apex_*'):
        device_ids.append(str(device).split('_')[1])
    return device_ids


class NPUError(Exception):
    pass

if __name__ == '__main__':
    critical_temp = 100
    warning_temp = 80

    start_time = time.time()

    img_data = requests.get(URL_TEST_IMAGE).content
    with open('dogs.jpg', 'wb') as image_file:
        image_file.write(img_data)

    tflite_threads = []
    openvino_threads = []

    coral_ids = check_devices()
    if coral_ids:
        for coral_device in coral_ids:
            tflite_thread = TFliteThread(coral_device)
            tflite_threads.append(tflite_thread)
    else:
        print("Couldn't find coral devices")

    openvino_threads.append(OpenvinoThread())

    for tflite_thread in tflite_threads: tflite_thread.start()
    for openvino_thread in openvino_threads: openvino_thread.start()

    try:
        while time.time() < start_time + max_stress_time:
            output_string = ""
            if openvino_threads and tflite_threads:
                output_string += "Myriad temp-{"
                for count, openvino_thread in enumerate(openvino_threads):
                    output_string += f"d{count}:{openvino_thread.temperature:.2f}, "
                output_string = output_string[:-2] + "}. Coral temp-{"
                for count, tflite_thread in enumerate(tflite_threads):
                    output_string += f"d{count}:{tflite_thread.temperature:.2f}, "
                output_string = output_string[:-2] + '}\r'
                print(output_string, end='')
            elif openvino_threads:
                output_string += "Myriad temp-{"
                for count, openvino_thread in enumerate(openvino_threads):
                    output_string += f"d{count}:{openvino_thread.temperature:.2f}, "
                output_string = output_string[:-2] + '}\r'
            elif tflite_threads:
                output_string += "Coral temp:"
                for count, tflite_thread in enumerate(tflite_threads):
                    output_string += f"d{count}:{tflite_thread.temperature:.2f}, "
                output_string = output_string[:-2] + '}\r'
            else:
                raise NPUError
            print(output_string, end='')
            time.sleep(0.5)
    except Exception as exc:
        if exc == NPUError:
            print("Couldn't find NPU")
        print("Exit")
        sys.exit()

    print("\nTemperature is stable, neural processing unit test will passed.")
