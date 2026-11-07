# Kinetiq

A Python app that tracks body landmarks in an uploaded workout video and counts squats using the knee angle. Built with Streamlit and MediaPipe.

## Current features

- Upload and preview an MP4 video.
- Detect one person's pose and overlay the body skeleton.
- Count standing → lowered → standing cycles.
- Display the knee angle and repetition count on the output video.
- Plot knee angle over time and download the annotated video.

This version uses a pretrained pose model and a rule-based counter. It does not yet assess exercise technique or train a custom model.

## Setup on Windows

Run these commands inside the repository:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
New-Item -ItemType Directory -Force models
Invoke-WebRequest -Uri 'https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task' -OutFile 'models/pose_landmarker_lite.task'
.\.venv\Scripts\python.exe -m streamlit run app.py
```

The downloaded model is excluded from Git. Model source and documentation: [MediaPipe Pose Landmarker](https://developers.google.com/edge/mediapipe/solutions/vision/pose_landmarker?tab=Python).

## How tracking works

1. ImageIO decodes the video into RGB frames.
2. MediaPipe estimates 33 body landmarks. VIDEO mode also uses tracking between frames.
3. Each landmark includes normalized coordinates and visibility/presence scores. Multiplying x by frame width and y by frame height gives pixel coordinates.
4. OpenCV draws visible points and connects shoulders, arms, hips and legs using their landmark indices. Drawing only visualizes the model output; it does not perform tracking.
5. The app selects the more visible leg at the first usable detection and keeps that side throughout the video.
6. The hip–knee–ankle angle is calculated in image pixel coordinates using the dot product.

The counter waits for an angle above 160°, then a descent below 100°, then a return above 160°. Only that final return increments the count. Missing or out-of-frame leg landmarks reset the pending repetition, but keep completed repetitions.

## Recording and limitations

- Start standing and film one person from the side with the entire body visible.
- Begin with a short clip containing 3–5 repetitions.
- The 100°/160° thresholds are initial heuristics, not validated technique standards.
- Shallow movements, occlusion, loose clothing and landmark jitter can cause missed or incorrect counts. No temporal smoothing is applied yet.
- A fixed camera and side view matter because the angle is a 2D projection.
- Person detection coverage is not pose accuracy or technique quality.
- The output has no audio. Playback uses the reported FPS; variable-frame-rate inputs may have timing differences.
- Files used during processing are temporary. Results remain in the Streamlit session; uploading another file clears them. Processing runs on the machine hosting the app.

## Manual verification

Compare results with a manual count on new videos: standing still, three complete repetitions, a pause at the bottom, a shallow descent, and a person leaving the frame mid-repetition. Record failures before adjusting thresholds. No real-video counting accuracy has been established yet.
