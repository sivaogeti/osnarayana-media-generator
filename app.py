"""Streamlit app for generating media (image, audio, video) using prompts."""


import os

import streamlit as st
from dotenv import load_dotenv
from PIL import UnidentifiedImageError

from backend.media_gen import generate_image, generate_audio, generate_video
from backend.media_gen import sanitize_filename, translate_text

load_dotenv()

st.set_page_config(page_title="OSN Media Studio", layout="wide", page_icon="🎬")

# ---------- Sidebar ----------
with st.sidebar:
    st.title("⚙️ Settings")
    language_options = ['English', 'Telugu', 'Hindi']
    prompt_lang = st.selectbox("Select Prompt Language", options=language_options, index=0)
    target_lang = st.selectbox("Translate to Language", options=language_options, index=0)
    add_watermark = st.checkbox("Add watermark/logo", value=True)
    dark_mode = st.toggle("🌗 Dark Mode", value=False)
    st.markdown("---")
    st.caption("Built by O.S.Narayana ❤️ using Streamlit + ElevenLabs + Unsplash")

if dark_mode:
    st.markdown(
        """
        <style>
        body {
            background-color: #0e1117;
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# ---------- Title ----------
st.title("🎬 Welcome to OSN Media Generator")

# ---------- Prompt Input ----------
prompt = st.text_input("Enter your media prompt", max_chars=200)

if prompt:
    translated_prompt = prompt
    if prompt_lang != target_lang:
        translated_prompt = translate_text(prompt, target_lang)

    filename_prefix = sanitize_filename(translated_prompt)

    # ---------- Tabs ----------
    tab1, tab2, tab3 = st.tabs(["🖼️ Image", "🔊 Audio", "🎞️ Video"])

    # ---------- Image Generation ----------
    with tab1:
        if st.button("Generate Image"):
            with st.spinner("Generating image..."):
                image_path = generate_image(translated_prompt, filename_prefix, add_watermark)
            if image_path and os.path.exists(image_path):  # pylint: disable=no-member
                try:
                    st.image(image_path, caption="Generated Image", use_container_width=True)
                    with open(image_path, "rb") as f:
                        st.download_button("Download Image", f, file_name=os.path.basename(image_path), mime="image/png")
                except UnidentifiedImageError:
                    st.error("❌ Error displaying image. Please try with a different prompt or disable watermark.")
            else:
                st.warning("⚠️ Image generation failed. Please try again.")

    # ---------- Audio Generation ----------
    
    with tab2:
        if prompt:  # Ensure prompt is not empty
            # Generate a safe and unique file name
            from datetime import datetime
            import re

            def sanitize_filename(text):
                return re.sub(r'\W+', '_', text).lower()

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"{sanitize_filename(prompt)[:50]}_{timestamp}"

            if st.button("Generate Audio"):
                st.write("🔄 Audio generation started...")
                with st.spinner("Generating audio..."):
                    audio_path = os.path.join("outputs/audio", f"{file_name}.mp3")
                    try:
                        result_path = generate_audio(prompt, audio_path)
                        if result_path and os.path.exists(result_path):
                            st.audio(result_path)
                            st.success("Audio generation complete.")
                        else:
                            st.error("Audio generation failed.")
                            st.write(f"🔍 File not found at: {audio_path}")
                    except Exception as e:
                        st.error("⚠️ Audio generation crashed.")
                        st.write(f"Error: {str(e)}")
        else:
            st.warning("Please enter a prompt to generate audio.")

    
 
    # ---------- Video Generation ----------
    with tab3:
        if st.button("Generate Video"):
            with st.spinner("Generating video..."):
                image_path = f"outputs/images/{sanitize_filename(translated_prompt)}.jpg"
                audio_path = f"outputs/audio/{sanitize_filename(translated_prompt)}.mp3"
                if os.path.exists(image_path) and os.path.exists(audio_path):  # pylint: disable=no-member
                    video_path = generate_video(translated_prompt, image_path, audio_path)
                    if video_path and os.path.exists(video_path):  # pylint: disable=no-member
                        st.video(video_path)
                        with open(video_path, "rb") as f:
                            st.download_button("Download Video", f, file_name=os.path.basename(video_path), mime="video/mp4")
                    else:
                        st.error("❌ Video generation failed.")
                else:
                    st.warning("⚠️ Please generate both image and audio first.")
