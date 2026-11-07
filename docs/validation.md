# Validation record

## Verified locally

Environment: Windows, Python 3.13, a new virtual environment installed from the pinned direct dependencies in requirements.txt.

- Dependency installation and pip compatibility check.
- Automated geometry, visibility and counting scenarios.
- Equivalent synthetic cycles at 15, 30 and 60 FPS.
- Single-frame spikes, incomplete cycles and tracking interruptions.
- Video decoding, annotation, progress and H.264 export using synthetic pose results.
- Actual MediaPipe model initialization/inference on a blank video.
- Streamlit demo, upload, result persistence, exercise/side reset and error handling.
- CSV values and explicit simulation/video provenance.
- Model download checksum, cached reuse and rejection of corrupted data.

The real-model blank-video test is an operational smoke test, not a test of exercise recognition or count accuracy.

## Not yet established

- Accuracy on independent real workout videos.
- Reliability across people, camera positions, lighting and clothing.
- Validity of exercise-form or injury-related feedback; this app does not provide it.
- Hosted Linux CI and deployed app behavior until those run on their respective platforms.

## Real-video evaluation protocol

Use videos you own or have permission to process. For each exercise, collect separate clips with different people or recording sessions. Include full repetitions, partial motion, pauses, occlusion and stationary poses.

1. Count complete cycles manually using a written definition.
2. Keep calibration clips separate from evaluation clips.
3. Run Kinetiq without changing thresholds on evaluation clips.
4. Record results using evaluation_template.csv.
5. Report mean absolute count error, exact-count match rate and sample count per exercise.
6. Keep failures visible and describe the camera conditions.
7. If thresholds change after reviewing evaluation failures, use a new holdout set.

MAE = mean(abs(predicted_count - reference_count)).
Exact-count match rate = number of exact matches / number of evaluation clips.

No example score or invented benchmark is provided.
