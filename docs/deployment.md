# Running and sharing Kinetiq

## Local demo

Follow README.md, run Streamlit, and click **Try a simulated example**. The example exercises the counter and reporting code. It is explicitly labelled as simulated.

For a real demo, upload a short side-view clip of one person. Start in the extended position. Keep the tracked joints visible and manually compare the count.

## Streamlit Community Cloud

The repository includes pinned Python dependencies, packages.txt for Linux libraries and .streamlit/config.toml.

1. Push the completed repository to GitHub.
2. In Streamlit Community Cloud, create an app from that repository.
3. Select app.py as the entry point and Python 3.13.
4. Deploy and inspect the build log.
5. Check the simulated demo, then test a short real upload.
6. Add the actual deployed URL to the README only after it works.

The model downloads from Google's official storage on first real analysis and is verified by SHA-256. Internet is required for that first download. No paid API key is needed.

Hosted service resource limits still apply. Each session runs inference on the host CPU; large uploads and concurrent users consume memory and compute. This repository is a portfolio prototype, not a multi-tenant production service.

Official deployment instructions: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app

No public deployment is created automatically by these files.

## Troubleshooting

- Missing or invalid model: delete only models/pose_landmarker_lite.task, then run python model_setup.py again.
- Download failure: check network access to storage.googleapis.com.
- Video failure: use a playable H.264 MP4 shorter than two minutes.
- Low measurement coverage: check selected side, lighting and visibility.
- Unexpected counts: review the angle plot, compare with a manual count and read the limitations.
- Import errors after upgrading an older environment: follow the OpenCV cleanup instructions in README.md, or create a new virtual environment.
