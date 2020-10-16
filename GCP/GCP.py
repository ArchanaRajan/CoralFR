import threading
import camera
import json
import io

from PIL import Image
from base64 import b64encode
from json import dumps
from google.cloud import pubsub_v1
from concurrent.futures import TimeoutError

project_id = "speaker-agent-rminpp"
topic_id = "CoralDeviceToBMSServer"
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_id)

ENCODING = 'utf-8'
IMAGE_NAME = '/home/archana/Desktop/FaceDetection/A1_96.jpg'
JSON_NAME = 'output.json'
timeout = 5.0

def send_In_Thread(sub_face, imageId, txId):
    print('Inside send_In_Thread')

    # if True:
    #     time.sleep(1.0);
    #     print('Published with fileName', fileName, ', imageId', imageId, ', txId', txId);
    #     return;
    
    #imgByteArr = io.BytesIO()
    #byte_content = sub_face.tobytes()
    image = Image.fromarray(sub_face)
    imgByteArr = io.BytesIO()
    image.save(imgByteArr, "PNG")
    base64_bytes = b64encode(imgByteArr.getvalue())
    base64_string = base64_bytes.decode(ENCODING)
    #print("BASE 64 STRING : " + base64_string)
    #imageId = random.randint(1, 1000000)
    data = {
        'imageByteArray': base64_string,
        'imageId': str(imageId),
        'transactionId' : str(txId)
    }
    decoded = dumps(data, indent=2)
    #print("JSON DATA : " + decoded)
    byte_string = decoded.encode('utf-8')
    publisher.publish(topic_path, data=byte_string)

    print('Published with imageId', imageId, ', txId', txId);

def send(sub_face, id, txId):
    #send_In_Thread(fileName)
    t = threading.Thread(target=send_In_Thread, args=(sub_face, id, txId,), daemon=True)
    t.start()

class PubSub:

    def __init__(self):
        self.subscribeInThread()

    def subscribeInThread(self):
        x = threading.Thread(target=self.subscribe, daemon=True)
        x.start()

    def callback(self, message):
        print("Received message: {}".format(message))
        inputMap = json.loads(message.data);
        print("MAPPPPPP :"+str(inputMap));
        camera.monitor.isUserAuthorised = inputMap.get('isUserAuthorized');
        camera.monitor.userName = inputMap.get('userName');
        if inputMap.get('isUserAuthorized') is True:
            camera.monitor.statusMessage = 'Welcome ' + inputMap.get('userName');
        else:
            camera.monitor.statusMessage = 'Access denied';
        
        message.ack()
        print("Received and acknowledged messages. Done !!!! ")

    def subscribe(self):
        subscriber = pubsub_v1.SubscriberClient()
        subscription_path = subscriber.subscription_path(project_id, "BMSToGCP")
        print("Subscribeddddddddddd")
	    #print("Listening for messages on {}..\n".format(subscription_path))
        streaming_pull_future = subscriber.subscribe(subscription_path, callback=self.callback)

        # Wrap subscriber in a 'with' block to automatically call close() when done.
        with subscriber:
            try:
                # When `timeout` is not set, result() will block indefinitely,
                # unless an exception is encountered first.
                streaming_pull_future.result(timeout=None)
            except TimeoutError:
                streaming_pull_future.cancel()
