from pathlib import Path
from tempfile import TemporaryDirectory

import streamlit as st

from demo import demo_analysis
from exercises import EXERCISES
from pose_analysis import analyze_video
from reporting import report_csv


def clear_results():
    st.session_state.pop('analysis', None)
    st.session_state.pop('processed_video', None)


st.set_page_config(page_title = 'Kinetiq', page_icon = '🏋️', layout = 'centered')

st.title('Kinetiq')
st.write('Track your movement. Understand every repetition.')
st.caption('Video pose estimation · Three exercises · Downloadable reports')

exercise = st.selectbox('Choose your exercise', list(EXERCISES), on_change = clear_results)
settings = EXERCISES[exercise]
side_options = ['Left', 'Right'] if exercise == 'Biceps curl (single arm)' else ['Auto', 'Left', 'Right']
side = st.selectbox('Side to track', side_options, on_change = clear_results)
st.caption('Left and right refer to your own body, not the screen. For curls, choose the working arm. Auto keeps the first clearly visible side.')

with st.expander('How to record', expanded = True):
    st.write(settings['instructions'])
    st.write(settings['movement'])
    st.caption('Keep the camera still. Start with 3–5 repetitions. Upload one person in an MP4 video, up to 100 MB and 2 minutes.')

if st.button('Try a simulated example'):
    clear_results()
    st.session_state['analysis'] = demo_analysis(exercise)

video = st.file_uploader('Upload your workout video', type = ['mp4'], max_upload_size = 100, on_change = clear_results)
st.caption('Videos are processed on the machine hosting this app. Temporary files are deleted after processing; results remain in your session. No external AI API receives your video.')

if video is not None:
    with st.expander('Original video'):
        st.video(video)

    if st.button('Analyze exercise', type = 'primary'):
        clear_results()
        progress_bar = st.progress(0, text = 'Preparing the model and opening video...')

        def show_progress(fraction, seconds):
            progress_bar.progress(fraction, text = f'Processed {seconds:.1f} seconds of video')

        try:
            with TemporaryDirectory() as temporary_directory:
                input_path = Path(temporary_directory) / 'input.mp4'
                output_path = Path(temporary_directory) / 'output.mp4'
                input_path.write_bytes(video.getvalue())
                analysis = analyze_video(input_path, output_path, exercise, side, progress = show_progress)
                processed_video = output_path.read_bytes()
        except FileNotFoundError:
            st.error('A required file could not be found. Check the setup steps in README.md.')
        except (OSError, ValueError, RuntimeError):
            st.error('Analysis could not finish. Use a playable H.264 MP4 under 2 minutes and check free disk space. On the first run, internet access is needed to download the pose model.')
        else:
            st.session_state['analysis'] = analysis
            st.session_state['processed_video'] = processed_video
        finally:
            progress_bar.empty()

if 'analysis' in st.session_state:
    analysis = st.session_state['analysis']
    source = analysis.get('source', 'video')
    simulated = source == 'simulation'
    joint = settings['joint']

    st.subheader(f'{exercise} analysis')

    if simulated:
        st.info('Simulated joint angles: this example demonstrates the counter and report. It does not use video or measure pose-detection accuracy.')

    first, second, third = st.columns(3)
    first.metric('Repetitions', analysis['repetitions'])

    if simulated:
        second.metric('Input', 'Simulated')
    else:
        coverage = analysis['measured_frames'] / analysis['total_frames']
        second.metric('Measured frames', f'{coverage:.0%}')

    duration = analysis['duration']
    third.metric('Duration', f'{duration:.1f} s')

    if not simulated:
        st.caption('Measured frames means the selected joints were visible enough to calculate an angle. It is not an accuracy score.')

        if analysis['side'] is not None:
            tracked_side = analysis['side'].title()
            st.write(f'Tracked side: {tracked_side}')

        if analysis['measured_frames'] == 0:
            st.warning('No usable joint angles were found. Check the selected side, lighting and camera view.')
        elif coverage < 0.7:
            st.warning('The selected joints were often hidden. The count may miss repetitions; try a clearer side view.')
        elif analysis['repetitions'] == 0:
            st.info('No complete repetitions were confirmed. Start in the extended position and keep the tracked joints visible through the full movement.')

    chart_tab, report_tab, video_tab = st.tabs(['Angle chart', 'Repetition report', 'Annotated video'])

    with chart_tab:
        st.subheader(f'{joint} angle over time')
        st.line_chart(analysis['angles'], x = 'time', y = 'angle', x_label = 'Time (seconds)', y_label = f'{joint} angle (degrees)')
        st.caption('Angles use a short median filter. Gaps indicate missing measurements.')

    with report_tab:
        if analysis['report']:
            st.dataframe(analysis['report'], hide_index = True)
            st.caption('Times are seconds from the start. Duration and minimum angle use the filtered signal; confirmation adds a small delay.')
        else:
            st.write('The report will appear after a complete repetition is detected.')

    with video_tab:
        if simulated:
            st.write('Upload a video to see the skeleton overlay on your own movement.')
        else:
            st.video(st.session_state['processed_video'])
            st.caption('The exported video has no audio and is resized to at most 960 pixels on its longest side.')

    bent_angle = settings['bent_angle']
    extended_angle = settings['extended_angle']
    with st.expander('How the count works'):
        st.write(f'{joint} angle: above {extended_angle}° → below {bent_angle}° → above {extended_angle}°.')
        st.write('Each endpoint must persist for about 0.15 seconds. Missing tracked joints cancel the unfinished repetition.')
        st.caption('These are prototype thresholds. Kinetiq counts selected movements; it does not validate exercise technique.')

    video_name = exercise.lower().replace(' ', '_').replace('(', '').replace(')', '')
    if not simulated:
        st.download_button('Download annotated video', data = st.session_state['processed_video'], file_name = f'kinetiq_{video_name}.mp4', mime = 'video/mp4', on_click = 'ignore')

    st.download_button('Download repetition report (CSV)', data = report_csv(analysis), file_name = f'kinetiq_{video_name}_{source}.csv', mime = 'text/csv', disabled = not analysis['report'], on_click = 'ignore')
