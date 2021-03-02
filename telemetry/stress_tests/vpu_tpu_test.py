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
            self.temperature = openvino_model.model.ie.get_metric(metric_name="DEVICE_THERMAL", device_name="MYRIAD")
            if self.temperature > warning_temp:
                print("Warning {}".format(warning_temp))
            elif self.temperature > critical_temp:
                print("Critical {}".format(critical_temp))
                break


class TFliteThread(Thread):
    def __init__(self):
        super().__init__()
        self.temperature = 0
        self.start_time = time.time()
        self.daemon = True

        self.warning_temp = 80
        self.critical_temp = 100

        self.device = "TPU"

    def run(self):
        tflite_model = nnio.zoo.edgetpu.detection.SSDMobileNet(self.device)
        tflite_preproc = tflite_model.get_preprocessing()
        tflite_image = tflite_preproc('dogs.jpg')

        device_id = 0
        coral_temp_path = Path(f"/sys/class/apex/apex_{device_id}/temp")

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


if __name__ == '__main__':
    critical_temp = 100
    warning_temp = 80

    start_time = time.time()


    img_data = requests.get(URL_TEST_IMAGE).content
    with open('dogs.jpg', 'wb') as image_file:
        image_file.write(img_data)

    openvino_thread = OpenvinoThread()
    tflite_thread = TFliteThread()
    openvino_thread.start()
    tflite_thread.start()

    try:
        while time.time() < start_time + max_stress_time:
            if openvino_thread.temperature != 0 or tflite_thread.temperature != 0:
                print(f"Myriad temp: {openvino_thread.temperature:.2f}. Coral temp: {tflite_thread.temperature}\r", end='')
            time.sleep(0.5)
    except:
        sys.exit()

    print("\nTemperature is stable, accelerator test will passed.")
