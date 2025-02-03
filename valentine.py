#! venv/bin/python

import logging
import os, os.path
import random
import signal
import subprocess
import sys
import time
from gpiozero import Button

PRINTER_FOUND=False

LOG_FILE='/tmp/valentine.log'
PTOUCH_PRINT='/usr/local/bin/ptouch-print'
IMAGE_DIR=os.path.join(os.curdir, 'images')

BUTTON_GPIO=27
DEBOUNCE_TIME=0.1
WAIT_TIME=30

def signal_handler(sig, frame):
    button.close()
    logger.info('Stopping Valentine')
    sys.exit(0)

def test_printer():
    logger.info(f'Looking for Printer')
    printer = subprocess.run([PTOUCH_PRINT, '--info'], capture_output=False) 
    if printer.returncode != 0:
        logger.info(f'Printer Not Found')
        return False
    else:
        logger.info(f'Printer Found')
        return True

def get_image(images):
    index = random.randint(0,len(images) - 1) 
    return os.path.join(IMAGE_DIR, images[index])

def on_press(images):
    image = get_image(images)
    logger.info(f'Calling print_image with {image}')
    print_image(image)
    time.sleep(WAIT_TIME)
    logger.info(f'Printing done.')

def print_image(image):
    if test_printer():
        logger.info(f'Printing image: {image}')
        printer = subprocess.run([PTOUCH_PRINT, '--image', image], capture_output=True) 
    else:
        logger.info(f'Dummy Print of image: {image}')

signal.signal(signal.SIGINT, signal_handler)
logger = logging.getLogger('valentine')
logging.basicConfig(filename=LOG_FILE, level=logging.INFO)
logger.info(f'Starting Valentine\n---\nReading images from: {os.path.abspath(IMAGE_DIR)}')

images = os.listdir(IMAGE_DIR)
button = Button(BUTTON_GPIO, bounce_time=DEBOUNCE_TIME)

while True:
    button.wait_for_press()
    on_press(images)
