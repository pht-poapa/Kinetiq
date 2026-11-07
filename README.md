# Kinetiq

A Python app that tracks body landmarks in an uploaded workout video and counts squats, push-ups and single-arm biceps curls. Built with Streamlit and MediaPipe.

## Current features

- Upload and preview an MP4 video.
- Detect one person's pose and overlay the body skeleton.
- Select the exercise and the body side to track.
- Count extended → bent → extended cycles.
- Display the tracked joint angle and repetition count on the output video.
- Plot the angle over time and download the annotated video.

This version uses a pretrained pose model and a rule-based counter. It does not yet assess exercise technique or train a custom model.

## Supported exercises

| Exercise | Landmarks | Initial extended / bent thresholds | Start position |
| --- | --- | --- | --- |
| Squat | Hip, knee, ankle | Above 160° / below 100° | Standing |
| Push-up | Shoulder, elbow, wrist | Above 160° / below 90° | Top position, arms extended |
| Biceps curl (single arm) | Shoulder, elbow, wrist | Above 150° / below 60° | Working arm extended |

The selected exercise determines which landmarks and thresholds are used. The app does not recognize exercises automatically. Elbow motion alone cannot distinguish a push-up from a curl or confirm body alignment.

For curls, explicitly select the working arm using your body's left/right, not screen position. Only that arm is counted; alternating-arm and combined two-arm totals are not supported. For squats and push-ups, Auto selects the more visible usable side and keeps it fixed. You can also select a side manually.

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
5. The app tracks the selected side, or selects the more visible usable side in Auto mode. It keeps the same side throughout the video.
6. The hip–knee–ankle or shoulder–elbow–wrist angle is calculated in image pixel coordinates using the dot product.

The counter waits for an extended joint, then a bent joint, then a return to extension using the exercise's thresholds. Only that final return increments the count. Missing or out-of-frame tracked landmarks reset the pending repetition, but keep completed repetitions. A clip starting mid-repetition does not count that incomplete first cycle.

The exercise definitions live in the plain dictionary in `exercises.py`. `pose_analysis.py` contains the shared angle calculation and counter. `app.py` handles uploads and displays results.

## Recording and limitations

- Start in the exercise's extended position. Film one person from the side with the tracked joints visible; for squats and push-ups, keep the entire body in frame.
- Begin with a short clip containing 3–5 repetitions.
- All thresholds are initial heuristics, not validated technique standards.
- Shallow movements, occlusion, loose clothing and landmark jitter can cause missed or incorrect counts. No temporal smoothing is applied yet.
- A fixed camera and side view matter because the angle is a 2D projection.
- Person detection coverage is not pose accuracy or technique quality.
- The output has no audio. Playback uses the reported FPS; variable-frame-rate inputs may have timing differences.
- Files used during processing are temporary. Results remain in the Streamlit session; changing the exercise, side or uploaded file clears them. Processing runs on the machine hosting the app.

## Manual verification

For each exercise, compare results with a manual count on new videos: staying still, three complete repetitions, a pause in the bent position, a partial movement, and a person leaving the frame mid-repetition. Also test changing the selected exercise and side. Record failures before adjusting thresholds. No real-video counting accuracy has been established yet.

Run the automated geometry and counting tests with:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```
