# Capture movement from webcam
import os
import cv2
import time, glob
from threading import Thread
from emailing import send_email

video = cv2.VideoCapture(0)
time.sleep(1)

first_frame = None
status_list = []
count = 1
img_with_obj=''
def clean_folder():
    images = glob.glob('images/*.png')
    for image in images:
        os.remove(image)

while True:
    status = 0
    check, frame = video.read()

    # Turn pixels to grayscale => simplify
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray_frame_gau = cv2.GaussianBlur(gray_frame, (21, 21), 0)

    if first_frame is None:
        first_frame = gray_frame_gau

    delta_frame = cv2.absdiff(first_frame, gray_frame_gau)

    thresh_frame = cv2.threshold(delta_frame, 60, 255, cv2.THRESH_BINARY)[1]
    dil_frame = cv2.dilate(thresh_frame, None, iterations=2)
    cv2.imshow('My video', thresh_frame)

    # Detect contours around white area
    contours, check = cv2.findContours(dil_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        # If is small object, continue
        if cv2.contourArea(contour) < 5000:
            continue
        x, y, w, h = cv2.boundingRect(contour)

        # Make green rectangle
        rectangle = cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)
        if rectangle.any():
            status = 1 # Object in view
            cv2.imwrite(f'images/{count}.png', frame)
            count += 1
            all_images = glob.glob('images/*.png')
            index = int(len(all_images) / 2)
            img_with_obj = all_images[index]

    status_list.append(status)
    status_list = status_list[-2:]

    # Catch event when object out of view
    if status_list[0] == 1 and status_list[1] == 0:
        # Make send_email run background so not affect displaying frame
        email_thread = Thread(target = send_email, args = (img_with_obj, ))
        email_thread.daemon = True

        # Make clean_folder run background so not affect displaying frame
        clean_thread = Thread(target = clean_folder)
        clean_thread.daemon = True

        email_thread.start()

    # Draw rectangle around object
    cv2.imshow('Video', frame)

    key = cv2.waitKey(1)

    # If press q
    if key == ord('q'):
        break

video.release()
clean_thread.start()
