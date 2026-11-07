from pathlib import Path
from tempfile import TemporaryDirectory

import streamlit as st

from pose_analysis import analyze_video


st.set_page_config(page_title = 'Kinetiq', page_icon = '🏋️', layout = 'centered')

st.title('Kinetiq')
st.write('Understand your movement. Improve your form.')

exercise = st.selectbox('Choose your exercise', ['Squat'])

st.subheader('Record your video')
st.write('Film yourself from the side, keep your entire body visible, and keep the camera still.')
st.caption('Use a short MP4 video with one person and 3–5 repetitions.')

video = st.file_uploader('Upload your workout video', type = ['mp4'])

if video is not None:
    st.subheader('Your video')
    st.video(video)
    st.write(f'Selected exercise: {exercise}')

    if st.button('Detect body pose', type = 'primary'):
        with st.spinner('Processing your video...'):
            with TemporaryDirectory() as temporary_directory:
                input_path = Path(temporary_directory) / 'input.mp4'
                output_path = Path(temporary_directory) / 'output.mp4'

                input_path.write_bytes(video.getvalue())
                total_frames, detected_frames = analyze_video(input_path, output_path)
                processed_video = output_path.read_bytes()

        st.subheader('Pose detection result')
        st.video(processed_video)

        detection_rate = detected_frames / total_frames
        st.metric('Frames with a detected person', f'{detection_rate:.0%}')
        st.caption('This measures detection coverage, not exercise quality or accuracy.')

        if detected_frames == 0:
            st.warning('No person was detected. Try a brighter video with your entire body visible.')

        st.download_button('Download annotated video', data = processed_video, file_name = 'kinetiq_pose.mp4', mime = 'video/mp4', on_click = 'ignore')