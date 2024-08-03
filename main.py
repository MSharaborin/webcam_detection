import os
from datetime import datetime

import cv2
import requests

from settings import (
    username,
    password,
    ip_address,
    port,
    gap_time_second,
    date_file,
    url,
    token_telegram,
    chat_id,
)


os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'rtsp_transport;tcp'
SEND_TIME = datetime.now()
url_640x480 = f"rtsp://{username}:{password}@{ip_address}:{port}/stream1"
url_1080p = f"rtsp://{username}:{password}@{ip_address}:{port}/stream1"

rtsp_url = url_640x480
# rtsp_url = url_1080p

def start_cam():
    cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
    if not cap.isOpened():
        print("Failed to open RTSP stream")
        exit()

    while True:
        # Read a frame from the RTSP stream
        ret, frame = cap.read()
        _, new_frame = cap.read()

        deference = cv2.absdiff(frame, new_frame)
        gray = cv2.cvtColor(deference, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blur, 10, 255, cv2.THRESH_BINARY)
        dilated = cv2.dilate(thresh, None, iterations=2)
        contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        counter = 0

        for cnt in contours:
            counter += 1
            if cv2.contourArea(cnt) < 5000:
                continue
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(frame, (x, y), (x + w, y + y), (0, 255, 0), 2)

            # if date_point is None or
            cv2.imwrite(date_file, frame)
            if check_interval():
                send_photo_to_telegram()

        # Check if the frame is read correctly
        if not ret:
            print("Failed to read frame")
            break

        # # Display the frame
        # cv2.imshow("RTSP Stream", frame)
        # #
        # # Press 'q' to quit
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break

    # Release the RTSP stream and close the window
    cap.release()
    cv2.destroyAllWindows()


def check_interval():
    print('Start checking interval')
    gap = datetime.now() - SEND_TIME
    if gap.total_seconds() > gap_time_second:
        return True
    return False


def send_photo_to_telegram():
    print('Send photo to telegram')
    files = {'photo': open(date_file, 'rb')}
    requests.post(f'{url}{token_telegram}/sendPhoto?chat_id={chat_id}', files=files)
    SEND_TIME = datetime.now()


if __name__ == '__main__':
    start_cam()