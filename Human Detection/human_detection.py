from ultralytics import YOLO
import paho.mqtt.client as mqtt
import cv2
import schedule
import os

def mqttConnection(): # mqtt broker connection
    global siteTopic

    broker_address = "ADDR'
    broker_port = 1883
    username = "USER"
    password = "PASSWORD"

    client = mqtt.Client()
    client.username_pw_set(username, password)

    client.connect(broker_address, broker_port)

    client.publish(f'/{siteTopic}/logs', "Client MQTT connected!") # publish to site logs topic

    return client

def captureImage():
    ret, frame = cam.read()
    cv2.imwrite(f'temp/images/{camTopic}.png', frame) # writes captured image in local folder /temp/images/camTopic.png

    predictImage()


def predictImage():
    global mqttClient
    global siteTopic
    global camTopic
    global predicted
    global imgCounterMax

    results = model(f'temp/images/{camTopic}.png', classes=0, conf=0.4) # predict humans on image with minimum confidence of 0.4

    for result in results:
        if (len(predicted) < imgCounterMax): # if there's not enough samples to calculate mean
            humanCounter = result.boxes.cls.tolist().count(0)
            predicted.append(humanCounter)
            # print(predicted)
        else: # when there is enough samples, publish the mean to mqtt topic
            humanCounterMean = round(sum(predicted)/len(predicted))
            print(f'Mean of predicted people in the last {len(predicted)} images is {humanCounterMean}')
            predicted = [] # resets predicted array
            publishContent = f'{{"counter": {humanCounterMean}}}'
            mqttClient.publish(f'/{siteTopic}/cams/{camTopic}', publishContent) # send people counting to topic /siteTopic/cams/camTopic



if not os.path.exists("temp/images/"): # creates temp dir for captured images if not exists
    os.makedirs("temp/images/")

siteTopic = '656c954bd3518eb7af0270f3' # should be the id in the database. currently is the home user
camTopic = 'webcam'

captureInterval = 4 # interval in seconds to capture images
publishInterval = 60 # interval in seconds to publish human detection
imgCounterMax = publishInterval/captureInterval
predicted = []
 
print('Loading pretrained neural network...')
model = YOLO("yolov8x.pt")  # load a pretrained model (recommended for training)

print('Loading cam...')
cam = cv2.VideoCapture(0) # define cam object

print('Connecting to MQTT broker...')
mqttClient = mqttConnection()

print('Starting prediction system...')
schedule.every(captureInterval).seconds.do(captureImage)

while True:
    schedule.run_pending()
