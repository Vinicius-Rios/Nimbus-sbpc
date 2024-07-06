from ultralytics import YOLO
import cv2
import schedule
import os
import torch
from PIL import Image, ImageDraw, ImageFont
import numpy as np

torch.cuda.set_device(0)

def captureImage():
    ret, frame = cam.read()

    # Draw the count on the image using PIL

    # Convert back to OpenCV format
    
    cv2.imwrite(f'temp/images/image.png', frame) # writes captured image in local folder /temp/images/camTopic.png

    predictImage()


def predictImage():
    global mqttClient
    global siteTopic
    global predicted
    global imgCounterMax

    # results = model(f'temp/images/image.png', conf=0.3, save=True, device='gpu') # predict all on image with minimum confidence of 0.3
    results = model(f'temp/images/image.png', classes=0, conf=0.3, save=True, device='gpu') # predict humans on image with minimum confidence of 0.3

    for result in results:
        if (len(predicted) < imgCounterMax): # if there's not enough samples to calculate mean
            humanCounter = result.boxes.cls.tolist().count(0)
            predicted.append(humanCounter)
            ## Draw the count on the image using PIL
            img = Image.open('temp/images/image.png')
            draw = ImageDraw.Draw(img)
            font = ImageFont.load_default()  # Use default PIL font

            # Draw the count on the image using the correct count from humanCounter
            draw.text((10, 10), f'Count: {humanCounter}', font=font, fill=(0, 255, 0))

            # Save the annotated image
            img.save('temp/images/image_with_count.png')
            
        else: # when there is enough samples, publish the mean to mqtt topic
            humanCounterMean = round(sum(predicted)/len(predicted))
            print(f'Mean of predicted people in the last {len(predicted)} images is {humanCounterMean}')
            predicted = [] # resets predicted array
            publishContent = f'{{"counter": {humanCounterMean}}}'
''

if not os.path.exists("temp/images/"): # creates temp dir for captured images if not exists
    os.makedirs("temp/images/")

captureInterval = 1 # interval in seconds to capture images
publishInterval = 60 # interval in seconds to publish human detection
imgCounterMax = publishInterval/captureInterval
predicted = []
 
print('Loading pretrained neural network...')
model = YOLO("yolov8x.pt")  # load a pretrained model (recommended for training)

print('Loading cam...')
cam = cv2.VideoCapture(2) # define cam object
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

print('Starting prediction system...')
schedule.every(captureInterval).seconds.do(captureImage)

while True:
    schedule.run_pending()
