from pathlib import Path
from tempfile import TemporaryDirectory

import streamlit as st

from pose_analysis import analyze_video
from exercises import EXERCISES


def clear_results():
    st.session_state.pop('analysis', None)
    st.session_state.pop('processed_video', None)


st.set_page_config(page_title = 'Kinetiq', page_icon = '🏋️', layout = 'centered')

st.title('Kinetiq')
st.write('Understand your movement. Improve your form.')

exercise = st.selectbox('Choose your exercise', list(EXERCISES), on_change = clear_results)
settings = EXERCISES[exercise]
side_options = ['Left', 'Right'] if exercise == 'Biceps curl (single arm)' else ['Auto', 'Left', 'Right']
side = st.selectbox('Side to track', side_options, on_change = clear_results)
st.caption('Left and right refer to your own body, not the screen. For curls, choose the working arm. Auto keeps the first clearly visible side.')

st.subheader('Record your video')
st.write(settings['instructions'])
st.caption('Keep the camera still. Use a short MP4 video with one person and 3–5 repetitions.')
st.info(settings['movement'])

video = st.file_uploader('Upload your workout video', type = ['mp4'], on_change = clear_results)

if video is not None:
    st.subheader('Your video')
    st.video(video)
    st.write(f'Selected exercise: {exercise}')

    if st.button('Analyze exercise', type = 'primary'):
        clear_results()

        with st.spinner('Processing your video...'):
            with TemporaryDirectory() as temporary_directory:
                input_path = Path(temporary_directory) / 'input.mp4'
                output_path = Path(temporary_directory) / 'output.mp4'

                input_path.write_bytes(video.getvalue())
                analysis = analyze_video(input_path, output_path, exercise, side)
                processed_video = output_path.read_bytes()

        st.session_state['analysis'] = analysis
        st.session_state['processed_video'] = processed_video

    if 'analysis' in st.session_state:
        analysis = st.session_state['analysis']
        processed_video = st.session_state['processed_video']

        st.subheader(f'{exercise} analysis')
        st.video(processed_video)
        st.metric('Completed repetitions', analysis['repetitions'])
        bent_angle = settings['bent_angle']
        extended_angle = settings['extended_angle']
        joint = settings['joint']
        st.caption(f'{joint} angle: above {extended_angle}° → below {bent_angle}° → above {extended_angle}°. Prototype thresholds, not a form assessment.')

        if analysis['side'] is not None:
            tracked_side = analysis['side'].title()
            st.write(f'Tracked side: {tracked_side}')

        detection_rate = analysis['detected_frames'] / analysis['total_frames']
        st.metric('Frames with a detected person', f'{detection_rate:.0%}')
        st.caption('Detection coverage is not accuracy. Missing tracked landmarks interrupt the current repetition.')

        st.subheader(f'{joint} angle over time')
        st.line_chart(analysis['angles'], x = 'time', y = 'angle', x_label = 'Time (seconds)', y_label = f'{joint} angle (degrees)')

        if analysis['detected_frames'] == 0:
            st.warning('No person was detected. Try a brighter video with your entire body visible.')
        elif all(row['angle'] is None for row in analysis['angles']):
            st.warning('The selected joints were not visible enough to measure the angle. Check the camera view and tracked side.')

        st.caption('The exported video has no audio.')
        video_name = exercise.lower().replace(' ', '_').replace('(', '').replace(')', '')
        st.download_button('Download annotated video', data = processed_video, file_name = f'kinetiq_{video_name}.mp4', mime = 'video/mp4', on_click = 'ignore')
