from pathlib import Path
from tempfile import TemporaryDirectory

import streamlit as st

from pose_analysis import analyze_video


def clear_results():
    st.session_state.pop('analysis', None)
    st.session_state.pop('processed_video', None)


st.set_page_config(page_title = 'Kinetiq', page_icon = '🏋️', layout = 'centered')

st.title('Kinetiq')
st.write('Understand your movement. Improve your form.')

exercise = st.selectbox('Choose your exercise', ['Squat'])

st.subheader('Record your video')
st.write('Film yourself from the side, keep your entire body visible, and keep the camera still.')
st.caption('Start standing. Use a short MP4 video with one person and 3–5 repetitions.')

video = st.file_uploader('Upload your workout video', type = ['mp4'], on_change = clear_results)

if video is not None:
    st.subheader('Your video')
    st.video(video)
    st.write(f'Selected exercise: {exercise}')

    if st.button('Analyze squats', type = 'primary'):
        clear_results()

        with st.spinner('Processing your video...'):
            with TemporaryDirectory() as temporary_directory:
                input_path = Path(temporary_directory) / 'input.mp4'
                output_path = Path(temporary_directory) / 'output.mp4'

                input_path.write_bytes(video.getvalue())
                analysis = analyze_video(input_path, output_path)
                processed_video = output_path.read_bytes()

        st.session_state['analysis'] = analysis
        st.session_state['processed_video'] = processed_video

    if 'analysis' in st.session_state:
        analysis = st.session_state['analysis']
        processed_video = st.session_state['processed_video']

        st.subheader('Squat analysis')
        st.video(processed_video)
        st.metric('Completed repetitions', analysis['repetitions'])
        st.caption('Counts standing → knee angle below 100° → standing above 160°. These are prototype thresholds, not a form assessment.')

        detection_rate = analysis['detected_frames'] / analysis['total_frames']
        st.metric('Frames with a detected person', f'{detection_rate:.0%}')
        st.caption('Detection coverage is not accuracy. Missing leg landmarks interrupt the current repetition.')

        st.subheader('Knee angle over time')
        st.line_chart(analysis['angles'], x = 'time', y = 'angle', x_label = 'Time (seconds)', y_label = 'Knee angle (degrees)')

        if analysis['detected_frames'] == 0:
            st.warning('No person was detected. Try a brighter video with your entire body visible.')
        elif all(row['angle'] is None for row in analysis['angles']):
            st.warning('The hip, knee and ankle were not visible enough to measure the angle.')

        st.caption('The exported video has no audio.')
        st.download_button('Download annotated video', data = processed_video, file_name = 'kinetiq_squats.mp4', mime = 'video/mp4', on_click = 'ignore')
