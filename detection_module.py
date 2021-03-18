import sys
import argparse
import time
from pathlib import Path

import cv2
import torch
import torch.backends.cudnn as cudnn
from numpy import random, ascontiguousarray

from models.experimental import attempt_load
# from models import experimental

from utils.datasets import LoadStreams, LoadImages, letterbox
from utils.general import check_img_size, check_requirements, check_imshow, non_max_suppression, apply_classifier, \
    scale_coords, xyxy2xywh, strip_optimizer, set_logging, increment_path
from utils.plots import plot_one_box
from utils.torch_utils import select_device, load_classifier, time_synchronized


model = None
imgsz = None
device = None
half = None
opt = None
names = None
colors = None


def load_model(weights=None, image_size=416, conf_thres=0.25, iou_thres=0.45, device_str=''):
    global model, imgsz, device, half, opt, names, colors
    if weights is None:
        weights = "yolov5s.pt"
    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', nargs='+', type=str, default=weights, help='model.pt path(s)')
    parser.add_argument('--img-size', type=int, default=image_size, help='inference size (pixels)')
    parser.add_argument('--conf-thres', type=float, default=conf_thres, help='object confidence threshold')
    parser.add_argument('--iou-thres', type=float, default=iou_thres, help='IOU threshold for NMS')
    parser.add_argument('--device', default=device_str, help='cuda device, i.e. 0 or 0,1,2,3 or cpu')

    parser.add_argument('--classes', nargs='+', type=int, help='filter by class: --class 0, or --class 0 2 3')
    parser.add_argument('--agnostic-nms', action='store_true', help='class-agnostic NMS')
    parser.add_argument('--augment', action='store_true', help='augmented inference')
    # parser.add_argument('--update', action='store_true', help='update all models')


    opt = parser.parse_args([])
    print(opt)

    # namespace = argparse.Namespace()

    with torch.no_grad():
        weights, imgsz = opt.weights, opt.img_size
        set_logging()
        device = select_device(opt.device)
        half = device.type != 'cpu'  # half precision only supported on CUDA
        # Load model
        # model = experimental.attempt_load(weights, map_location=device)  # load FP32 model
        model = attempt_load(weights, map_location=device)  # load FP32 model
        imgsz = check_img_size(imgsz, s=model.stride.max())  # check img_size

        if half:
            model.half()  # to FP16

        names = model.module.names if hasattr(model, 'module') else model.names
        colors = [[random.randint(0, 255) for _ in range(3)] for _ in range(len(names))]
        print("names : ", names)
        # warming
        img = torch.zeros((1, 3, imgsz, imgsz), device=device)  # init img
        _ = model(img.half() if half else img) if device.type != 'cpu' else None  # run once

        print("model loaded....")


def detect(image, conf_thres=None, classes=None):
    global model, imgsz, device, half, names, colors
    if conf_thres is not None:
        opt.__setattr__("conf_thres", conf_thres)
    if classes is not None:
        opt.__setattr__("classes", classes)

    # Padded resize
    # print("image.shape : ", image.shape)

    img = letterbox(image, new_shape=(imgsz, imgsz))[0]

    # Convert
    img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
    img = ascontiguousarray(img)

    # Run inference
    img = torch.from_numpy(img).to(device)

    img = img.half() if half else img.float()  # uint8 to fp16/32
    img /= 255.0  # 0 - 255 to 0.0 - 1.0
    if img.ndimension() == 3:
        img = img.unsqueeze(0)

    # print("opt : ", opt)

    # Inference
    t1 = time_synchronized()
    pred = model(img, augment=opt.augment)[0]

    # Apply NMS
    pred = non_max_suppression(pred, opt.conf_thres, opt.iou_thres, classes=opt.classes, agnostic=opt.agnostic_nms)
    t2 = time_synchronized()

    # Process detections
    bboxes, scores, ids, labeles = [], [], [], []

    for i, det in enumerate(pred):  # detections per image
        # print("i : ", i, "det : ", det)
        gn = torch.tensor(image.shape)[[1, 0, 1, 0]]  # normalization gain whwh
        if det is not None and len(det):
            # Rescale boxes from img_size to image size
            det[:, :4] = scale_coords(img.shape[2:], det[:, :4], image.shape).round()

            for *xyxy, conf, cls in reversed(det):
                c1, c2 = (int(xyxy[0]), int(xyxy[1])), (int(xyxy[2]), int(xyxy[3]))
                bboxes.append([int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3])])
                scores.append(conf)
                ids.append(int(cls))
                labeles.append(names[int(cls)])

    return bboxes, ids, scores, labeles

# if __name__ == '__main__':
#     print("sys.argv: ", sys.argv)
#     image_file = "data/images/zidane.jpg"  # sys.argv[3]
#     if len(sys.argv) >= 2:
#         image_file = sys.argv[1]
#
#     weights = None
#     if len(sys.argv) >= 3:
#         weights = sys.argv[2]
#     load_model(weights, 416)
#
#     image = cv2.imread(image_file)
#     # detect(image, 0.1, classes=[0, 5])
#     detect_and_show(image, 0.5, classes=None)
#
#
#
#
# # python detection_modul.py /media/gg-ai-team/DATA/TaiNH/yolov5-master/data/images/bus.jpg best.pt
# # python detection_modul.py /media/gg-ai-team/DATA/TaiNH/yolov5-master/data/images/zidane.jpg best.pt
