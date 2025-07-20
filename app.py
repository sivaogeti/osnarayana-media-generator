import streamlit as st
import os
from datetime import datetime
from backend.media_gen import generate_audio, generate_image, generate_video
from googletrans import Translator

# --- Helper Functions ---

def translate_prompt(prompt, lang):
    if lang == "English":
        return prompt
    try:
        translator = Translator()
        translated = translator.translate(prompt, dest=lang.lower()).text
        return translated
    except Exception:
        return prompt  # fallback to original

def sanitize_filename(prompt):
    return "".join(c if c.isalnum() else "_" for c in prompt.strip())[:50].lower()

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

# --- Streamlit Page Config ---
st.set_page_config(page_title="OSN Media Generator", layout="wide")

# ---------- Inline Settings ----------
with st.expander("⚙️ Settings", expanded=True):
    language_options = ['English', 'Telugu', 'Hindi']
    prompt_lang = st.selectbox("Select Prompt Language", options=language_options, index=0)
    target_lang = st.selectbox("Translate to Language", options=language_options, index=0)
    dark_mode = st.toggle("🌗 Dark Mode", value=False)
    st.markdown("---")
    st.caption("Built by O.S.Narayana ❤️ using Streamlit + ElevenLabs + Unsplash")

# Dark Mode Styling
st.markdown(
    """
    <style>
    body { background-color: %s; color: %s; }
    </style>
    """ % ("#0E1117" if dark_mode else "#FFFFFF", "#FAFAFA" if dark_mode else "#000000"),
    unsafe_allow_html=True,
)

# ---------- Main UI ----------
st.title("🎮 Welcome to OSN Media Generator")
st.caption("Enter your media prompt")

prompt = st.text_input("📝 Prompt", placeholder="e.g., A farmer working in the field", label_visibility="collapsed")

# Inline Debug, Watermark, Lang Toggles
debug_mode = st.toggle("🪛 Show Debug Logs", value=False)
add_watermark = st.checkbox("🌊 Add watermark/logo (optional)", value=False)
lang = st.selectbox("🌐 Language", ["English", "Telugu", "Hindi", "Tamil"], index=0)

# ---------- Tabs for Media ----------
tab1, tab2, tab3 = st.tabs(["🖼️ Image", "🔊 Audio", "🎞️ Video"])

if prompt:
    translated_prompt = translate_prompt(prompt, lang)
    safe_prompt = sanitize_filename(prompt)

    with tab1:
        if st.button("Generate Image"):
            image_path = f"outputs/images/{safe_prompt}.png"
            ensure_dir("outputs/images")
            path = generate_image(translated_prompt, image_path, add_watermark)
            if path and os.path.exists(path):
                st.image(path, caption="Generated Image", use_container_width=True)
                st.download_button("📥 Download Image", data=open(path, "rb"), file_name=os.path.basename(path), mime="image/png")

    with tab2:
        if st.button("Generate Audio"):
            audio_path = f"outputs/audio/{safe_prompt}.mp3"
            ensure_dir("outputs/audio")
            path = generate_audio(translated_prompt, audio_path, debug_mode)
            if path and os.path.exists(path):
                st.audio(path)
                st.download_button("📥 Download Audio", data=open(path, "rb"), file_name=os.path.basename(path), mime="audio/mpeg")

    with tab3:
        if st.button("Generate Video"):
            video_path = f"outputs/videos/{safe_prompt}.mp4"
            image_path = f"outputs/images/{safe_prompt}.jpg"
            audio_path = f"outputs/audio/{safe_prompt}.mp3"
            ensure_dir("outputs/videos")
            path = generate_video(translated_prompt, image_path, audio_path, video_path, add_watermark)
            if path and os.path.exists(path):
                st.video(path)
                st.download_button("📥 Download Video", data=open(path, "rb"), file_name=os.path.basename(path), mime="video/mp4")
