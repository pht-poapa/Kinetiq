import streamlit as st

st.set_page_config(page_title = 'Kinetiq', page_icon = '🏋️', layout = 'centered')
st.title('Kinetiq')
st.write('Understand your movement. Improve your form.')

exercise = st.selectbox('Choose your exercise', ['Squat'])

st.subheader('Record your video')
st.write('Film yourself from the side, keep your entire body visible, and keep the camera still.')
st.caption('Start with a short video containing 3–5 repetitions.')

video = st.file_uploader('Upload your workout video', type = ['mp4'])

if video is not None:
    st.subheader('Your video')
    st.video(video)
    st.write(f'Selected exercise: {exercise}')
    st.info('Video preview is ready. Movement analysis will be added in the next version.')