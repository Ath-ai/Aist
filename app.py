import streamlit as st
import whisper
import os
from moviepy.editor import VideoFileClip
import tempfile

# Set up the Streamlit App layout
st.title('Video Subtitles Generator')
st.write("Upload a video file, and the system will generate subtitles for you!")

# Function to generate subtitles
def generate_subtitles(video_file_path):
    # Extract audio from the video
    clip = VideoFileClip(video_file_path)
    
    # Save audio as a temporary file
    temp_audio_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    audio_path = temp_audio_file.name
    clip.audio.write_audiofile(audio_path)
    
    # Load Whisper model
    model = whisper.load_model("base")
    
    # Transcribe the audio file
    result = model.transcribe(audio_path)
    
    # Create SRT format subtitles
    subtitles = []
    for segment in result['segments']:
        start = segment['start']
        end = segment['end']
        text = segment['text']
        
        # Format the timing in SRT format
        start_time = format_time(start)
        end_time = format_time(end)
        
        subtitles.append(f"{len(subtitles) + 1}\n{start_time} --> {end_time}\n{text}\n")
    
    # Return subtitles in SRT format
    return "\n".join(subtitles)

# Function to format time in SRT format
def format_time(seconds):
    ms = int((seconds % 1) * 1000)
    time_str = f"{int(seconds // 3600):02}:{int((seconds % 3600) // 60):02}:{int(seconds % 60):02},{ms:03}"
    return time_str

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
