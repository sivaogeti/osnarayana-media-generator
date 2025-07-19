import streamlit as st
from backend.media_gen import generate_audio, generate_image, generate_video
from backend.utils import translate_prompt, sanitize_filename, get_timestamp, ensure_dir
from dotenv import load_dotenv
import os

load_dotenv()

# App settings
st.set_page_config(page_title="OSN Media Generator", layout="wide")

st.title("🎮 Welcome to OSN Media Generator")
st.caption("Enter your media prompt")

# Prompt input
prompt = st.text_input("📝 Prompt", placeholder="e.g., A farmer working in the field", label_visibility="collapsed")

# Debug toggle
debug_mode = st.toggle("🪛 Show Debug Logs", value=False)

# Watermark option
add_watermark = st.checkbox("🌊 Add watermark/logo (optional)", value=False)

# Translate language
lang = st.selectbox("🌐 Language", ["English", "Telugu", "Hindi", "Tamil"], index=0)

# Main media generation tabs
tab1, tab2, tab3 = st.tabs(["🖼️ Image", "🔊 Audio", "🎞️ Video"])

if prompt:
    translated_prompt = translate_prompt(prompt, lang)
    safe_prompt = sanitize_filename(prompt)

    # === IMAGE TAB ===
    with tab1:
        if st.button("Generate Image"):
            image_path = f"outputs/images/{safe_prompt}.png"
            ensure_dir("outputs/images")
            path = generate_image(translated_prompt, image_path, add_watermark=add_watermark)
            if path and os.path.exists(path):
                st.image(path, caption="Generated Image", use_container_width=True)
                st.download_button("📥 Download Image", data=open(path, "rb"), file_name=os.path.basename(path))

    # === AUDIO TAB ===
    with tab2:
        if st.button("Generate Audio"):
            audio_path = f"outputs/audio/{safe_prompt}.mp3"
            ensure_dir("outputs/audio")
            path = generate_audio(translated_prompt, audio_path, debug_mode=debug_mode)
            if path and os.path.exists(path):
                st.audio(path)
                st.download_button("📥 Download Audio", data=open(path, "rb"), file_name=os.path.basename(path))

    # === VIDEO TAB ===
    with tab3:
        if st.button("Generate Video"):
            video_path = f"outputs/videos/{safe_prompt}.mp4"
            ensure_dir("outputs/videos")
            path = generate_video(translated_prompt, video_path, add_watermark=add_watermark)
            if path and os.path.exists(path):
                st.video(path)
                st.download_button("📥 Download Video", data=open(path, "rb"), file_name=os.path.basename(path))
else:
    st.info("Please enter a prompt to begin.")
