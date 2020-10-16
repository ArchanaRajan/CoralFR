# camera.py# import the necessary packages
import cv2
import GCP as ps
from imutils.video import VideoStream
import numpy as np
import argparse
import imutils
import time
import random
from fdutils import Monitor

# defining prototext and caffemodel paths
caffeModel = "res10_300x300_ssd_iter_140000.caffemodel"
prototextPath = "deploy.prototxt.txt"

# Load Model
print("Loading model...................")
net = cv2.dnn.readNetFromCaffe(prototextPath, caffeModel)
monitor = Monitor();

class VideoCamera(object):
    def __init__(self):
        # initialize the video stream to get the live video frames
        print("[INFO] starting video stream...")
        self.vs = VideoStream(src=0).start()
        print('Monitor isReadyScanning = ' + str(monitor.statusMessage));
        time.sleep(2.0)

    def __del__(self):
        # releasing camera
        self.vs.stop()

    def get_frame(self):
        frame = self.vs.read()
        frame = imutils.resize(frame, width=800)

        # extract the dimensions , Resize image into 300x300 and converting image into blobFromImage
        (h, w) = frame.shape[:2]
        # blobImage convert RGB (104.0, 177.0, 123.0)
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0,
                                     (300, 300), (104.0, 177.0, 123.0))

        # passing blob through the network to detect and pridiction
        net.setInput(blob)
        print('before net forward')
        detections = net.forward()
        print('after net forward')

        color = (0, 128, 255);
        #if face detected
        #
        if not monitor.isUserAuthorised is '':
            color = (0, 255, 0) if monitor.isUserAuthorised is True else (50, 50, 245);

        for i in range(0, detections.shape[2]):
            # extract the confidence and prediction

            if not monitor.isReadyScanning:
                print('Is not ready for scanning')
                break;

            confidence = detections[0, 0, i, 2]

            # filter detections by confidence greater than the minimum confidence
            if confidence < 0.8:
                continue

            monitor.increaseCounter();

            # Determine the (x, y)-coordinates of the bounding box for the
            # object
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            print(confidence)
            # draw the bounding box of the face along with the associated
            text = "{:.2f}%".format(confidence * 100);
            y = startY - 10 if startY - 10 > 10 else startY + 10;

            sub_face = frame[(startY - 30):(endY + 30), (startX - 30):(endX + 30)];
            print('Sub_face className : ' + sub_face.__class__.__name__)

            if monitor.counter % 30 == 0 and monitor.counter <= 180:
                print('monitor.counter : ' + str(monitor.counter));
                #monitor.statusMessage = 'Scanning.....'
                fileName = "face.jpg-" + str(monitor.counter) + str(monitor.txId)
                #cv2.imwrite(fileName, sub_face);
                print('Before publish');
                ps.send(sub_face, monitor.counter, monitor.txId);
                print('After publish');

            cv2.rectangle(frame, (startX, startY), (endX, endY), color, 1)
            cv2.putText(frame, text, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1)

        print('Common status message : ' + monitor.statusMessage);
        cv2.putText(frame, monitor.statusMessage, (10, 40), cv2.FONT_HERSHEY_TRIPLEX, 0.7, color, 1);
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes();
