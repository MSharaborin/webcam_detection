FROM borda/docker_python-opencv-ffmpeg:gpu-py3.8-cv4.5.0


COPY requirements.txt .
RUN pip install -r requirements.txt
# copy project
COPY . .
