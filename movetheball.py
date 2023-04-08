import re

import pygame
import time
import speech_recognition as sr
import random
from transformers import pipeline
import threading
from queue import Queue

# If running on macOS, you may need to set the
# following environment variable before execution
# OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

# Worker process: get user input
# -----------------------------------

q_color = Queue()
q_size = Queue()
q_go = Queue()
q_Xspeed = Queue()
q_Yspeed = Queue()

classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
candidate_labels = ['change to red',
                    'change to green',
                    'change to blue',
                    'change to stop',
                    'change to go',
                    'change size',
                    'change speed',
                    'approval']

size_candidate = ['small', 'big']
speed_candidate = ['fast', 'slow']


def listen():
    r = sr.Recognizer()
    # sr.Microphone.list_microphone_names()
    with sr.Microphone() as source:
        print('Calibrating...')
        r.adjust_for_ambient_noise(source)
        r.energy_threshold = 150
        print('Okay, go!')
        isStop = True
        ballsize = 50
        while (isStop):
            """
            Comment out these to use mike 
            """
            text = input("Enter your value: ")

            """
            Uncomment these to use mike 
            """
            # audio = r.listen(source)
            # audio = r.record(source, duration=5)
            try:
                # text = r.recognize_google(audio)
                time.sleep(3);
            except:
                unrecognized_speech_text = 'Sorry, I didn\'t catch that.'
                text = unrecognized_speech_text

            classified = classifier(text, candidate_labels, multi_label=True)
            print(classified)
            # TODO: use the extracted text to add
            print("input Text: " + text)

            while "approval" in classified['labels'][0]:
                q_color.put((124, 252, 0))
                q_color.put((0, 0, 255))
                q_color.put((255, 0, 0))

            if "stop" in classified['labels'][0]:
                print("okay I am going to stop")
                q_go.put('STOP')
                # isStop = False
            elif "go" in classified['labels'][0]:
                print("okay I am going to move again")
                q_go.put('GO')

            elif "size" in classified['labels'][0]:
                sizelist = re.findall(r'\d+', text)
                size_classified = classifier(text, size_candidate, multi_label=True)
                if len(sizelist) != 0:
                    print("okay I am going to change the size to " + sizelist[0])
                    q_size.put(int(sizelist[0]))

                elif "small" in size_classified['labels'][0]:
                    print("okay I am going to make myself smaller")
                    ballsize = ballsize - 10
                    if ballsize > 0:
                        q_size.put(ballsize)
                    else:
                        print("I can't get smaller than now")
                elif "big" in "small" in size_classified['labels'][0]:
                    print("okay I am going to make myself bigger")
                    ballsize = ballsize + 10
                    if ballsize > 250:
                        print("I can't get bigger than now")
                    else:
                        q_size.put(ballsize)
                    q_size.put(ballsize)


            elif "green" in classified['labels'][0]:
                q_color.put((124, 252, 0))
            elif "blue" in classified['labels'][0]:
                q_color.put((0, 0, 255))
            elif "red" in classified['labels'][0]:
                q_color.put((255, 0, 0))

            elif "speed" in classified['labels'][0]:
                speedList = re.findall(r'\d+', text)
                speed_classified = classifier(text, speed_candidate, multi_label=True)

                x_speed = 6
                y_speed = 6
                if len(speedList) != 0:
                    print("okay I am going to change speed you said ")
                    print(speedList)
                    q_Xspeed.put(int(speedList[0]))
                    q_Yspeed.put(int[speedList[1]]) if len(speedList) > 1 else print("")
                elif "fast" in speed_classified['labels'][0]:
                    print("okay I am going to make ball faster")
                    if x_speed and y_speed < 30:
                        x_speed = x_speed + 2
                        y_speed = y_speed + 2
                        q_Xspeed.put(x_speed)
                        q_Yspeed.put(y_speed)
                    else:
                        print("I can't go faster")

                elif "slow" in speed_classified['labels'][0]:
                    print("okay I am going to make ball slower")
                    if x_speed and y_speed > 0:
                        x_speed = x_speed - 2
                        y_speed = y_speed - 2
                        q_Xspeed.put(x_speed)
                        q_Yspeed.put(y_speed)
                    else:
                        print("I can't go slower")


            # the correct next actions to the queue
            # q_size.put(random.choice([100, 50]))
            # q_color.put(random.choice([(255, 0, 0), (0, 0, 255)]))
            # q_go.put(random.choice(['STOP', 'GO']))


# Main execution loop
# -----------------------------------

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
MAX_VEL = 10

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

ball_x = random.randint(0, SCREEN_WIDTH)
ball_y = random.randint(0, SCREEN_HEIGHT)
ball_r = 50

x_vel = MAX_VEL
y_vel = MAX_VEL
delta_r = 0
ball_color = (255, 0, 0)

listener = threading.Thread(target=listen)
listener.start()

done = False
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    # Check for new commands from user
    try:
        ball_color = q_color.get(block=False, timeout=0.1)
    except:
        pass
    try:
        ball_r = q_size.get(block=False, timeout=0.1)
    except:
        pass
    try:
        stop_go = q_go.get(block=False, timeout=0.1)
        x_vel = MAX_VEL if stop_go == 'GO' else 0
        y_vel = MAX_VEL if stop_go == 'GO' else 0
    except:
        pass
    try:
        # x_vel = q_Xspeed.get(block=False, timeout=0.1)
        # y_vel = q_Yspeed.get(block=False, timeout=0.1)
        MAX_VEL = q_Xspeed.get(block=False, timeout=0.1)
        print(q_Xspeed)
    except:
        pass
    # Move the ball
    ball_x += x_vel
    ball_y += y_vel
    ball_r += delta_r

    # If the ball hit the wall, reverse direction
    if ball_x + ball_r > SCREEN_WIDTH: x_vel = -MAX_VEL
    if ball_x - ball_r < 0: x_vel = MAX_VEL
    if ball_y + ball_r > SCREEN_HEIGHT: y_vel = -MAX_VEL
    if ball_y - ball_r < 0: y_vel = MAX_VEL

    # Update the screen
    # screen.fill((0,0,0))    # clear all previously drawn images
    pygame.draw.circle(screen, ball_color, (ball_x, ball_y), ball_r)
    pygame.display.flip()  # updates the display
    pygame.draw.circle(screen, (0, 0, 0), (ball_x, ball_y), ball_r)

    clock.tick(60)  # pauses execution until 1/60 seconds
    # have passed since the last tick
