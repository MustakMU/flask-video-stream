

import os
from threading import Thread
import cv2
import sys
import signal
import sys
import signal
from flask import Flask, Response, render_template


app = Flask(__name__)
camera_ids = [0 ,"D:\\test\\test\\1.mkv"]

camera_map = {}
camera_threads = {}

class DeepFaceNew:

    def __init__(self, camera_link):
        self.camera_link = camera_link
        self.camera_run = True

    def run_face_recognation(self):
        self.camera = cv2.VideoCapture(self.camera_link)
        _, self.frame = self.camera.read()  # Read a frame from the camera
        while self.camera_run:
            success, frame  = self.camera.read()  # Read a frame from the camera
            if not success:
                return False
            else:
                # Encode the frame as JPEG
                self.frame = cv2.imencode('.jpg', frame)[1].tobytes()
        print("run_face_recognation exit")
        return False

    def get_frame(self):
        return self.frame
    
    def close_camera(self):
        self.camera_run = False
        print("camera_run ", self.camera_run)
        self.camera.release()

    
def gen(deep):
    """Video streaming generator function."""
    while True:
        frame = deep.get_frame()
        if frame == False:
            break
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Route to serve the video stream
@app.route('/video_feed/<camera_id>')
def video_feed(camera_id):
    camera = camera_map[int(camera_id)]
    return Response(gen(camera), mimetype='multipart/x-mixed-replace; boundary=frame')

# Route to serve the HTML page that displays the video stream
@app.route('/')
def index():
    return render_template('index.html', camera_ids=camera_map.keys())


def handler(signal, frame):
    print('CTRL-C pressed!')
    for camera_id in camera_threads:
        camera_threads[camera_id].close_camera()
    sys.exit(0)

if __name__ == "__main__":
    
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)

    try:
        for idx, camera_id in enumerate(camera_ids):
            thr = DeepFaceNew(camera_link=camera_id)
            Thread(target=thr.run_face_recognation).start()
            camera_threads[camera_id] = thr
            camera_map[idx] = thr
        os.environ["WERKZEUG_RUN_MAIN"] = "false"
        app.run(host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print('Interrupted')
    