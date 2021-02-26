import nnio
import requests
import time
from openvino.inference_engine import IECore


URL_MODEL_BIN = 'https://github.com/FastSense/nnio/raw/development/models/openvino/ssd_mobilenet_v2_coco/ssd_mobilenet_v2_coco_fp16.bin'
URL_MODEL_XML = 'https://github.com/FastSense/nnio/raw/development/models/openvino/ssd_mobilenet_v2_coco/ssd_mobilenet_v2_coco_fp16.xml'
URL_TEST_IMAGE = 'https://raw.githubusercontent.com/FastSense/nnio/master/tests/dogs.jpg'

def system_check(iecore):
    #iecore.get_metric()

    return True


def prepare_network():
    # Load models
    model = nnio.zoo.openvino.detection.SSDMobileNetV2("MYRIAD")

    # Get preprocessing function
    preproc = model.get_preprocessing()

    image_prepared = preproc('dogs.jpg')

    return image_prepared, model


def inference(preproc, model):
    boxes, info = model(image_prepared, return_info=True)
    print(info.temperature)


if __name__ == '__main__':
    max_stress_time = 60 * 10
    start_time = time.time()

    critical_temp = 100
    warning_temp = 80

    img_data = requests.get(URL_TEST_IMAGE).content
    with open('dog.jpg', 'wb') as image_file:
        image_file.write(img_data)

    image, net_model = prepare_network()
    while time.time() < start_time + max_stress_time:
        boxes, info = net_model(image, return_info=True)
        print("Intel Myriad. Temp:{:.2f}\r".format(info["temperature"]), end='')
        if info["temperature"] > warning_temp:
            print("Warning {}".format(warning_temp))
        elif info["temperature"] > critical_temp:
            print("Critical {}".format(critical_temp))
