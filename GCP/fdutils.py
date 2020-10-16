import time;
import threading;
import random;


class Monitor:

    def __init__(self):
        self.txId = random.randint(1, 1000000);
        self.counter = 1;
        self.max = 330;
        self.isReadyScanning = True;
        self.sleepTime = 5.0;
        self.statusMessage = 'Scanning...';
        self.isUserAuthorised = '';
        self.userName = '';

    def increaseCounter(self):
        print('counter : ' + str(self.counter));
        self.counter = self.counter + 1;
        if self.counter == self.max:
            self.sleep();

    def sleep(self):
        print('Inside sleep function')
        t = threading.Thread(target=self.sleepInThread, args=(), daemon=True);
        t.start();

    def sleepInThread(self):
        self.isReadyScanning = False;
        print('Before setting : ' + self.statusMessage);
        #self.statusMessage = 'Face detection will resume in few seconds'
        print('After setting : ' + self.statusMessage);
        print('sleeping for ' + str(self.sleepTime) + ' seconds');
        time.sleep(self.sleepTime);
        print('Ready for scanning after waiting for ' + str(self.sleepTime) + ' seconds');
        self.isReadyScanning = True;
        self.statusMessage = 'Scanning...'
        self.counter = 0;
        self.txId = random.randint(1, 1000000);
        self.isUserAuthorised = '';
        self.userName = '';
