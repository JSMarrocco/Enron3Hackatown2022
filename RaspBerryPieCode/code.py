import RPi.GPIO as GPIO
import time
import imageio as iio
from PIL import Image
import numpy as np
from tflite_runtime.interpreter import Interpreter
import copy

import matplotlib.pyplot as plt

import requests
config = {}
config['CONTAINER_ID'] = '001' # stay constant
config['ENRON3WEB_URI'] = 'http://51.222.45.44:3000/api/container/post/%s/%d'


#assign GPIO pins for motors and sensors
motor_channel = (29,31,33,35)
ledG = 32
ledR = 12
ultrasonic_trigG = 11
ultrasonic_echoG = 13
ultrasonic_trigR = 16
ultrasonic_echoR = 18
motion_sensor = 7

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

#for defining GPIO channels as input/output use
GPIO.setup(motor_channel, GPIO.OUT)
GPIO.setup(ultrasonic_trigG, GPIO.OUT)
GPIO.setup(ultrasonic_echoG, GPIO.IN)
GPIO.setup(ultrasonic_trigR, GPIO.OUT)
GPIO.setup(ultrasonic_echoR, GPIO.IN)
GPIO.setup(motion_sensor, GPIO.IN)
GPIO.setup(ledG, GPIO.OUT)
GPIO.setup(ledR, GPIO.OUT)

def rotateTrash():
    for i in range(0,64):
        print('TRASH\n')
        GPIO.output(motor_channel, (GPIO.HIGH,GPIO.LOW,GPIO.LOW,GPIO.HIGH))
        time.sleep(0.005)
        GPIO.output(motor_channel, (GPIO.HIGH,GPIO.HIGH,GPIO.LOW,GPIO.LOW))
        time.sleep(0.005)
        GPIO.output(motor_channel, (GPIO.LOW,GPIO.HIGH,GPIO.HIGH,GPIO.LOW))
        time.sleep(0.005)
        GPIO.output(motor_channel, (GPIO.LOW,GPIO.LOW,GPIO.HIGH,GPIO.HIGH))
        time.sleep(0.005)
    time.sleep(1)
    for i in range(0,64):
        print('RETURN TO CENTER\n')
        GPIO.output(motor_channel, (GPIO.HIGH,GPIO.LOW,GPIO.LOW,GPIO.HIGH))
        time.sleep(0.005)
        GPIO.output(motor_channel, (GPIO.LOW,GPIO.LOW,GPIO.HIGH,GPIO.HIGH))
        time.sleep(0.005)
        GPIO.output(motor_channel, (GPIO.LOW,GPIO.HIGH,GPIO.HIGH,GPIO.LOW))
        time.sleep(0.005)
        GPIO.output(motor_channel, (GPIO.HIGH,GPIO.HIGH,GPIO.LOW,GPIO.LOW))
        time.sleep(0.005)

def rotateRecycling():
    for i in range(0,64):
        print('RECYCLING\n')
        GPIO.output(motor_channel, (GPIO.HIGH,GPIO.LOW,GPIO.LOW,GPIO.HIGH))
        time.sleep(0.005)
        GPIO.output(motor_channel, (GPIO.LOW,GPIO.LOW,GPIO.HIGH,GPIO.HIGH))
        time.sleep(0.005)
        GPIO.output(motor_channel, (GPIO.LOW,GPIO.HIGH,GPIO.HIGH,GPIO.LOW))
        time.sleep(0.005)
        GPIO.output(motor_channel, (GPIO.HIGH,GPIO.HIGH,GPIO.LOW,GPIO.LOW))
        time.sleep(0.005)
    time.sleep(1)
    for i in range(0,64):
        print('RETURN TO CENTER\n')
        GPIO.output(motor_channel, (GPIO.HIGH,GPIO.LOW,GPIO.LOW,GPIO.HIGH))
        time.sleep(0.005)
        GPIO.output(motor_channel, (GPIO.HIGH,GPIO.HIGH,GPIO.LOW,GPIO.LOW))
        time.sleep(0.005)
        GPIO.output(motor_channel, (GPIO.LOW,GPIO.HIGH,GPIO.HIGH,GPIO.LOW))
        time.sleep(0.005)
        GPIO.output(motor_channel, (GPIO.LOW,GPIO.LOW,GPIO.HIGH,GPIO.HIGH))
        time.sleep(0.005)

def distanceG():
    # set Trigger to HIGH
    GPIO.output(ultrasonic_trigG, True)

    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(ultrasonic_trigG, False)

    StartTime = time.time()
    StopTime = time.time()

    # save StartTime
    while GPIO.input(ultrasonic_echoG) == 0:
        StartTime = time.time()

    # save time of arrival
    while GPIO.input(ultrasonic_echoG) == 1:
        StopTime = time.time()

    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2

    return distance



def distanceR():
    # set Trigger to HIGH
    GPIO.output(ultrasonic_trigR, True)

    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(ultrasonic_trigR, False)

    StartTime = time.time()
    StopTime = time.time()

    # save StartTime
    while GPIO.input(ultrasonic_echoR) == 0:
        StartTime = time.time()

    # save time of arrival
    while GPIO.input(ultrasonic_echoR) == 1:
        StopTime = time.time()

    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2

    return distance

def classify_image(interpreter, image, top_k=1):
  tensor_index = interpreter.get_input_details()[0]['index']
  input_tensor= np.array(np.expand_dims(image ,0), dtype="float32")  
  interpreter.tensor(tensor_index, input_tensor)
  input_tensor[:, :] = image

  interpreter.invoke()
  output_details = interpreter.get_output_details()[0]
  output = np.squeeze(interpreter.get_tensor(output_details['index']))

  scale, zero_point = output_details['quantization']
  output = scale * (output - zero_point)

  ordered = np.argpartition(-output, top_k)
  return [(i, output[i]) for i in ordered[:top_k]][0]


def objecttype():

    print('taking picture')

    camera  = iio.get_reader("<video0>")
    screenshot = camera.get_data(0)
    camera.close()
    iio.imwrite('comparor.png', screenshot)

    model_path = './model3.tflite'


    print('loading model')
    interpreter = Interpreter(model_path)
    print("Model Loaded Successfully.")

    interpreter.allocate_tensors()
    _, height, width, _ = interpreter.get_input_details()[0]['shape']
    print("Image Shape (", width, ",", height, ")")

    # Load an image to be classified.
    image = Image.open("comparor.png").convert('RGB').resize((width, height))

    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    input_shape = input_details[0]['shape']
    input_tensor= np.array(np.expand_dims(image ,0), dtype="float32")


    input_index = interpreter.get_input_details()[0]["index"]

    interpreter.set_tensor(input_index, input_tensor)

    interpreter.invoke()
    output_details = interpreter.get_output_details()
    print(output_details)
    output_data = interpreter.get_tensor(output_details[0]['index'])
    pred = np.squeeze(output_data)


#    label_id, prob = classify_image(interpreter, image)
#    print(label_id)


    if pred.item(0) > pred.item(1):

        print("recycle")
        recyclebool = True
    elif pred.item(1) > pred.item(0):

        print("trash")
        recyclebool = False

    return (recyclebool)

canEmpty = 53

while True:

    if GPIO.input(motion_sensor):
        print("Motion Detected!")
        time.sleep(5)
        Trashorrecycle = objecttype()

        if (Trashorrecycle):
            print("Rotating to Recycling")
            GPIO.output(ledR, GPIO.HIGH)
            time.sleep(2)
            GPIO.output(ledR, GPIO.LOW)
            rotateRecycling()
        elif not(Trashorrecycle):
            print("Rotating to Trash")
            GPIO.output(ledG,GPIO.HIGH)
            time.sleep(2)
            GPIO.output(ledG,GPIO.LOW)
            rotateTrash()

        print("Measuring distances")
        distR = ((canEmpty - distanceR())/canEmpty)
        distG = ((canEmpty - distanceG())/canEmpty)
        if distG > distR:
            capacity = distG*100
        elif distR > distG:
            capacity = distR*100
        print(distR)
        print(distG)
        response = requests.post(config['ENRON3WEB_URI'] % ( config['CONTAINER_ID'] ,  capacity)) # stay constant
        print(response)

