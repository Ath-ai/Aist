import streamlit as st
import whisper
import os
import tempfile
from moviepy.editor import VideoFileClip
import numpy as np

# Function to format time in SRT format
def format_time(seconds):
    ms = int((seconds % 1) * 1000)
    time_str = f"{int(seconds // 3600):02}:{int((seconds % 3600) // 60):02}:{int(seconds % 60):02},{ms:03}"
    return time_str

# Function to generate subtitles from video file
def generate_subtitles(video_file_path):
    # Extract audio from the video
    clip = VideoFileClip(video_file_path)
    
    # Save audio as a temporary file
    temp_audio_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    audio_path = temp_audio_file.name
    clip.audio.write_audiofile(audio_path)
    
    # Load Whisper model
    model = whisper.load_model("base")
    
    # Load audio file using moviepy
    audio_clip = AudioFileClip(audio_path)
    duration = audio_clip.duration
    segment_duration = 30  # Transcribe in 30-second segments
    subtitles = []

    # Process audio in segments
    for start in np.arange(0, duration, segment_duration):
        end = min(start + segment_duration, duration)

        # Slicing the audio and saving it as a temporary file
        audio_segment = audio_clip.subclip(start, end)
        temp_segment_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        audio_segment.write_audiofile(temp_segment_file.name)

        # Transcribe the audio segment
        result = model.transcribe(temp_segment_file.name, task="transcribe")

        # Create SRT format subtitles
        for segment in result['segments']:
            segment_start = start + segment['start']
            segment_end = start + segment['end']
            text = segment['text'].strip()

            # Format the timing in SRT format
            start_time = format_time(segment_start)
            end_time = format_time(segment_end)
            subtitles.append(f"{len(subtitles) + 1}\n{start_time} --> {end_time}\n{text}\n")
    
    return "\n".join(subtitles)

# Set up the Streamlit App layout
st.title('Video Subtitles Generator')
st.write("Upload a video file, and the system will generate subtitles for you!")

# File uploader
uploaded_file = st.file_uploader("Upload a video file", type=['mp4', 'mkv', 'avi', 'mov'])

if uploaded_file is not None:
    # Save the uploaded video to a temporary file
    temp_video_file = tempfile.NamedTemporaryFile(delete=False)
    temp_video_file.write(uploaded_file.read())
    
    st.write("Generating subtitles... This might take a while.")
    
    # Generate subtitles
    subtitles = generate_subtitles(temp_video_file.name)
    
    # Display subtitle content
    st.text_area("Generated Subtitles", subtitles, height=300)
    
    # Download option for the subtitles
    st.download_button("Download SRT File", subtitles, file_name="subtitles.srt")
