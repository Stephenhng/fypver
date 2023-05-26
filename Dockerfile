# Use a Python base image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the application files to the container
COPY requirements.txt .
COPY . .

# Set the environment variable for Kivy to work in a Docker container
ENV KIVY_METRICS_DENSITY=2

# Install system dependencies for Kivy
RUN apt-get update && apt-get install -y \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    pkg-config \
    libgl1-mesa-dev \
    libgles2-mesa-dev \
    python3-setuptools \
    libgstreamer1.0-dev \
    git-core \
    gstreamer1.0-plugins-{bad,base,good,ugly} \
    gstreamer1.0-{omx,alsa} \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install -r requirements.txt

# Start the Kivy application
CMD ["python", "main.py"]
